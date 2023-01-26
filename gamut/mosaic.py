from base import AudioAnalyzer
from corpus import Corpus
from config import FILE_EXT, LOGGER
import numpy as np
from librosa import load
from os.path import join, basename
from copy import deepcopy
from time import time
from progress.counter import Counter
from progress.bar import IncrementalBar
from utils import resample_array
from scipy.signal import get_window
from random import choices, random
from audio import AudioBuffer


class Mosaic(AudioAnalyzer):
    """ 
    Audio Mosaic class
    """

    def __init__(self,
                 target: str | None = None,
                 corpus: list | Corpus = None,
                 sr: int | None = None) -> None:

        if any([target, corpus]) and not all([target, corpus]):
            raise ValueError(
                f'You must either provide both target and corpus attributes, or leave them blank to build Mosaic from {FILE_EXT} file')

        super().__init__()

        self.target = target
        self.sr = None
        self.frames = list()
        self.portable = None
        self.counter = Counter()

        corpora = self.__parse_corpus(corpus)
        self.soundfiles = {i: dict() for i in range(len(corpora or []))}
        if self.target and corpora:
            self.__build(corpora=corpora, sr=sr)

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
                path = join(corpus['source_root'], source['file'])
                if 'y' in soundfiles[corpus_id][source_id]:
                    continue
                soundfiles[corpus_id][source_id]['y'] = load(
                    path, sr=source['sr'])[0]
                self.counter.next()
        self.counter.finish()

    def __duplicate_channels(self, soundfiles: dict, n_chans: int) -> None:
        for corpus in soundfiles:
            for source in soundfiles[corpus]:
                if source == 'source_root':
                    continue
                soundfiles[corpus][source]['y'] = np.repeat(
                    np.array([soundfiles[corpus][source]['y']]).T, n_chans, axis=1)

    def __make_control_table(self, value, length):
        value_type = type(value)
        if value_type in [list, np.ndarray]:
            return resample_array(np.array(value), length)
        elif value_type in [int, float]:
            arr = np.empty(length)
            arr.fill(value)
            return arr

    def __quantize_array(self, arr, res):
        return np.round(arr / res) * res

    def synthesize(self,
                   accuracy: float = 1.0,
                   grain_dur: float = 0.1,
                   stretch_factor: float = 1.0,
                   onset_var: float = 0,
                   target_mix: float = 0,
                   pan_depth: float = 5,
                   n_chans: int = 2,
                   envelope: list | str = 'hann',
                   sr: int | None = None,
                   frame_length_res: int = 512) -> AudioBuffer:
        st = time()
        LOGGER.process(
            f'Generating audio mosaic for {basename(self.target)}...')
        # playback ratio
        sr, sr_ratio = (self.sr, 1) if not sr else (sr, sr/self.sr)
        hop_length = int(self.hop_length * sr_ratio)

        soundfiles = deepcopy(self.soundfiles)
        self.__duplicate_channels(soundfiles, n_chans=n_chans)

        n_segments = len(self.frames)

        # DYNAMIC CONTROL TABLES

        target_mix_table = self.__make_control_table(target_mix, n_segments)

        frame_length_table = self.__make_control_table(
            grain_dur * sr, n_segments)
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

        env_type = type(envelope)
        if env_type == str:
            windows = [np.repeat(np.array(
                [get_window(envelope, Nx=wl)]).T, n_chans, axis=1) for wl in frame_lengths]
        elif env_type in [list, np.ndarray]:
            windows = [np.repeat(np.array(
                [resample_array(envelope, N=wl)]).T, n_chans, axis=1) for wl in frame_lengths]

        # compute panning table
        pan_depth = max(0, pan_depth)
        pan_type = type(pan_depth)
        if pan_type in [list, np.ndarray]:
            pan_depth = np.repeat(
                np.array([resample_array(np.array(pan_depth), n_segments)]).T, n_chans, axis=1)
        pan_table = 1 / np.power(2, pan_depth * np.abs(np.repeat(np.array(
            [np.linspace(0, 1, n_chans)]), n_segments, axis=0) - np.random.rand(n_segments, 1)))
        row_sums = pan_table.sum(axis=1)
        pan_table = pan_table / row_sums[:, np.newaxis]

        # make buffer array
        buffer = np.empty(
            shape=(int(np.amax(samp_onset_table) + np.amax(frame_length_table)), n_chans))
        buffer.fill(0)

        grain_counter = IncrementalBar(LOGGER.subprocess('Concatenating grains: '), max=len(
            self.frames), suffix='%(index)d/%(max)d grains')

        for n, (ds, so, fl, p, tm) in enumerate(zip(self.frames, samp_onset_table, frame_length_table, pan_table, target_mix_table)):
            if random() > tm*0:
                num_frames = max(1, int(len(ds) * (1 - accuracy)))
                weights = np.linspace(1.0, 0.0, num_frames)
                f = choices(ds[:num_frames], weights=weights)[0]
            else:
                pass
                # f = recipe_dict['target_info']['data_samples'][n]
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
        LOGGER.elapsed_time(st)
        # return normalized buffer
        return AudioBuffer(y=(buffer / np.amax(np.abs(buffer))) * np.sqrt(0.5), sr=sr)


if __name__ == '__main__':
    source = '/Users/felipe-tovar-henao/Documents/Sample collections/Berklee44v11'
    target = '/Users/felipe-tovar-henao/Documents/GAMuT files/target_samples/angel_poema_44.1kHz.wav'
    corpus_output = './my_corpus.gamut'
    corpus_output2 = './my_corpus2.gamut'
    mosaic_output = './my_mosaic.gamut'
    # read = True
    # # # if read:
    c = Corpus()
    c.read(corpus_output)
    c2 = Corpus()
    c2.read(corpus_output2)
    # # else:
    c = Corpus(source)
    c.write(corpus_output, portable=False)
    mos = Mosaic(target=target, corpus=[c, c2])
    mos.write(mosaic_output, portable=False)
    mos = Mosaic()
    mos.read(mosaic_output)
    audio = mos.synthesize(accuracy=0.8, envelope=[0,1,0.5,0.25,0.125,0.006,0.0])
    audio.play()
