from .corpus import Corpus
from .config import FILE_EXT, LOGGER, AUDIO_FORMATS
from .audio import AudioBuffer
from .utils import resample_array
from .base import AudioAnalyzer
from .envelope import Envelope
from .envelope import Points

import numpy as np
from librosa import load
from os.path import join, basename, splitext, realpath, isdir
from copy import deepcopy
from time import time
from progress.counter import Counter
from progress.bar import IncrementalBar

from scipy.signal import get_window
from random import choices, random


class Mosaic(AudioAnalyzer):
    """ 
    Audio Mosaic class
    """

    def __init__(self,
                 target: str | None = None,
                 corpus: list | Corpus = None,
                 sr: int | None = None,
                 *args,
                 **kwargs) -> None:

        self.__validate(target, corpus)
        super().__init__(*args, **kwargs)

        self.target = target
        self.sr = None
        self.frames = list()
        self.portable = None
        self.counter = Counter()

        corpora = self.__parse_corpus(corpus)
        self.soundfiles = {i: dict() for i in range(-1, len(corpora or []))}

        if self.target and corpora:
            self.__build(corpora=corpora, sr=sr)

    def __validate(self, target, corpus):
        if any([target, corpus]) and not all([target, corpus]):
            raise ValueError(
                f'You must either provide both target and corpus attributes, or leave them blank to build Mosaic from {FILE_EXT} file')
        if not target:
            return
        if isdir(realpath(target)):
            raise ValueError(LOGGER.error(
                f'{target} is not a valid audio file path'))
        file = basename(target)
        if splitext(file)[1] not in AUDIO_FORMATS:
            raise ValueError(LOGGER.error(
                f'{file} is an invalid or unsupported audio file format.'))

    def __parse_corpus(self, corpus: list | Corpus, corpora: list = list()):
        if not corpus:
            return
        if isinstance(corpus, list):
            for c in corpus:
                return self.__parse_corpus(c)
        elif isinstance(corpus, Corpus):
            corpora.append(corpus)
        else:
            raise ValueError(f'{corpus} is not a corpus')
        return corpora

    def __build(self, corpora: list, sr: int | None = None) -> None:
        y, self.sr = load(self.target, sr=sr)
        target_analysis = self._analyze_audio_file(y=y, sr=self.sr)[0]
        self.soundfiles[-1][0] = {
            'file': self.target,
            'sr': self.sr,
            'y': y,
        }
        for x in target_analysis:
            matches = list()
            for corpus_id, corpus in enumerate(corpora):
                self.soundfiles[corpus_id]['source_root'] = corpus.source_root
                nearest_neighbors = corpus.tree.knn(
                    x=x,
                    vector_path='features',
                    first_n=corpus.tree.leaf_size)
                for nn in nearest_neighbors:
                    # get id of source audio file
                    source_id = nn['value']['source']
                    self.soundfiles[corpus_id][source_id] = corpus.soundfiles[source_id]
                    nn['value']['corpus'] = corpus_id
                    option = deepcopy(nn)
                    del option['value']['features']
                    matches.append(option)
            self.frames.append([x['value']
                               for x in sorted(matches, key=lambda x: x['cost'])])

    def serialize(self, spinner):
        mosaic = deepcopy(vars(self))
        spinner.next()

        # if not portable, delete audio samples from soundfiles on write
        if not self.portable:
            for corpus_id in mosaic['soundfiles']:
                for source_id in mosaic['soundfiles'][corpus_id]:
                    spinner.next()
                    if source_id == 'source_root':
                        continue
                    del mosaic['soundfiles'][corpus_id][source_id]['y']
        return mosaic

    def preload(self, obj):
        # reload soundfiles if non-portable
        if not obj['portable']:
            self.__load_soundfiles(obj['soundfiles'])
        return obj

    def read(self, file: str) -> None:
        return super().read(file, warn_user=self.frames)

    def __load_soundfiles(self, soundfiles):
        self.counter.message = LOGGER.subprocess('Loading audio files: ')
        for corpus_id in soundfiles:
            for source_id in soundfiles[corpus_id]:
                if source_id == 'source_root':
                    continue
                corpus = soundfiles[corpus_id]
                source = corpus[source_id]
                path = join(corpus['source_root'], source['file']) if corpus_id != -1 else source['file']
                if 'y' in soundfiles[corpus_id][source_id]:
                    continue
                soundfiles[corpus_id][source_id]['y'] = load(
                    path, sr=source['sr'])[0]
                self.counter.next()
        self.counter.finish()

    def __preprocess_samples(self, soundfiles: dict, n_chans: int, sr: int) -> None:
        c = Counter(LOGGER.subprocess('Preprocessing audio files: '))
        for corpus in soundfiles:
            for source in soundfiles[corpus]:
                if source == 'source_root':
                    continue
                y = soundfiles[corpus][source]['y']
                if soundfiles[corpus][source]['sr'] != sr:
                    y = resample_array(
                        y, int(len(y) * sr/soundfiles[corpus][source]['sr']))
                soundfiles[corpus][source]['y'] = np.repeat(
                    np.array([y]).T, n_chans, axis=1)
                c.next()
        c.finish()

    def __make_control_table(self, value, length):
        value_type = type(value)
        if value_type in [list, np.ndarray]:
            return resample_array(np.array(value), length)
        elif value_type in [int, float]:
            arr = np.empty(length)
            arr.fill(value)
            return arr

    def __param_points(self, param, N):
        if isinstance(param, Envelope):
            return param.get_points(N)
        else:
            return Points().fill(N, param)

    def __quantize_array(self, arr, res):
        return np.round(arr / res) * res

    def to_audio(self,
                 accuracy: float = 1.0,
                 grain_dur: float = 0.1,
                 stretch_factor: float = 1.0,
                 onset_var: float = 0,
                 target_mix: float = 0,
                 pan_depth: float = 5,
                 n_chans: int = 2,
                 grain_envelope: Envelope = Envelope(),
                 sr: int | None = None,
                 frame_length_res: int = 512) -> AudioBuffer:
        st = time()
        LOGGER.process(
            f'Generating audio from mosaic target: {basename(self.target)}...').print()
        # playback ratio
        sr, sr_ratio = (self.sr, 1) if not sr else (sr, sr/self.sr)
        hop_length = int(self.hop_length * sr_ratio)

        soundfiles = deepcopy(self.soundfiles)
        self.__preprocess_samples(soundfiles, n_chans=n_chans, sr=sr)

        n_segments = len(self.frames)

        # DYNAMIC CONTROL TABLES

        target_mix_table = self.__make_control_table(target_mix, n_segments)

        frame_length_table = self.__make_control_table(
            grain_dur, n_segments) * sr

        frame_length_table = self.__quantize_array(
            frame_length_table, frame_length_res).astype('int64')

        frame_lengths = np.arange(frame_length_res, np.amax(
            frame_length_table) + frame_length_res, frame_length_res, dtype='int64')

        samp_onset_table = self.__make_control_table(
            stretch_factor, n_segments) * hop_length
        samp_onset_table = np.concatenate(
            [[0], np.round(samp_onset_table)]).astype('int64').cumsum()[:-1]

        # apply onset variation to samp_onset_table
        onset_var_type = type(onset_var)
        if onset_var_type in [int, float]:
            if onset_var > 0:
                jitter = max(1, onset_var * sr // 2)
                samp_onset_table += np.random.randint(
                    low=jitter*-1, high=jitter, size=n_segments)
        if onset_var_type in [list, np.ndarray]:
            onset_var_table = resample_array(
                np.array(onset_var)*sr, n_segments) * np.random.rand(n_segments)
            samp_onset_table = samp_onset_table + \
                onset_var_table.astype('int64')
        samp_onset_table[samp_onset_table < 0] = 0

        # compute amplitude windows
        windows = [grain_envelope.get_points(wl).wrap().T.replicate(n_chans, axis=1) for wl in frame_lengths]

        # compute panning table
        pan_depth_table = self.__param_points(pan_depth, n_segments).wrap().T.replicate(n_chans, axis=1)
        pan_table = Points(np.linspace(0, 1, n_chans)).wrap().replicate(n_segments, axis=0) - np.random.rand(n_segments, 1)
        pan_table = 1 / (2**(pan_depth_table * pan_table.abs()))
        pan_table /= pan_table.sum(axis=1)[:, np.newaxis]

        # make buffer array
        buffer = np.empty(
            shape=(int(np.amax(samp_onset_table) + np.amax(frame_length_table)), n_chans))
        buffer.fill(0)

        grain_counter = IncrementalBar(LOGGER.subprocess('Concatenating grains: '), max=len(
            self.frames), suffix='%(index)d/%(max)d grains')

        for n, (ds, so, fl, p, tm) in enumerate(zip(self.frames, samp_onset_table, frame_length_table, pan_table, target_mix_table)):
            if random() > tm:
                num_frames = max(1, int(len(ds) * (1 - accuracy)))
                weights = np.linspace(1.0, 0.0, num_frames)
                f = choices(ds[:num_frames], weights=weights)[0]
            else:
                f = {
                    'corpus': -1,
                    'source': 0,
                    'marker': n * self.hop_length,
                }
            snd_id = f['source']
            corpus_id = f['corpus']
            snd = soundfiles[corpus_id][snd_id]['y']
            snd_sr_ratio = sr/soundfiles[corpus_id][snd_id]['sr']
            max_idx = len(snd) - 1
            samp_st = int(f['marker'] * snd_sr_ratio)
            samp_end = min(max_idx, samp_st+fl)
            seg_size = round((samp_end-samp_st) /
                             frame_length_res) * frame_length_res
            samp_end = samp_st+seg_size
            if seg_size != 0 and samp_end <= max_idx:
                idx = int(np.where(frame_lengths == seg_size)[0])
                window = windows[idx]
                segment = (snd[samp_st:samp_end] * window) * p
                buffer[so:so+seg_size] = buffer[so:so+seg_size] + segment
            grain_counter.next()

        grain_counter.finish()
        LOGGER.elapsed_time(st).print()

        # return normalized buffer
        return AudioBuffer(y=(buffer / np.amax(np.abs(buffer))) * np.sqrt(0.5), sr=sr)
