from .corpus import Corpus
from .config import FILE_EXT, LOGGER, AUDIO_FORMATS
from .audio import AudioBuffer
from .utils import resample_array
from .base import Analyzer
from .envelope import Envelope
from .envelope import Points

import numpy as np
from librosa import load
from os.path import join, basename, splitext, realpath, isdir
from copy import deepcopy
from time import time
from progress.counter import Counter
from progress.bar import IncrementalBar

from collections.abc import Iterable
from random import choices, random

from librosa.beat import tempo


class Mosaic(Analyzer):
    """ 
    A ``Mosaic`` represents the blueprint from which an audio mosaic can be synthesized.
    Given an input audio target file path and a ``Corpus`` instance, a virtual representation of 
    an audio mosaic is built, to be later converted to audio with the ``to_audio()`` method.\n

    By "blueprint" it's meant that a ``Mosaic`` instance generates and stores the necessary
    information to synthesize an audio mosaic, but does not automatically generate the audio mosaic.\n

    This allows the user to create different versions, based on the audio parameters passed to the 
    ``to_audio()`` method.

    target: str | None = None
        File path to target audio file.

    corpus: Iterable | Corpus = None
        ``Corpus`` instance to reconstruct ``target``

    sr: int | None = None
        Sampling rate of output audio file

    beat_unit: float | int | None = None
        Optional argument to set the grain rate to a beat unit relative to detected tempo (e.g., 1/4, 1/8, 1/16, etc.).
        Works best when ``target`` has a steady and perceptible tempo.
    """

    def __init__(self,
                 target: str | None = None,
                 corpus: Iterable | Corpus = None,
                 sr: int | None = None,
                 beat_unit: float | int | None = None,
                 *args,
                 **kwargs) -> None:
        self.__validate(target, corpus)
        super().__init__(*args, **kwargs)

        self.target = target
        self.sr = sr
        self.frames = []
        self.counter = Counter()
        self.beat_unit = beat_unit

        corpora = self.__parse_corpus(corpus)
        self.soundfiles = {i: {} for i in range(-1, len(corpora or []))}

        if self.target and corpora:
            self.__build(corpora=corpora, sr=sr)

    def __validate(self, target, corpus):
        if any([target, corpus]) and not all([target, corpus]):
            raise ValueError(
                f'You must either provide both target and corpus attributes, or leave them blank to build Mosaic from {FILE_EXT} file')
        if not target:
            return
        if isdir(realpath(target)):
            raise ValueError(LOGGER.error(f'{target} is not a valid audio file path'))
        file = basename(target)
        if splitext(file)[1] not in AUDIO_FORMATS:
            raise ValueError(LOGGER.error(f'{file} is an invalid or unsupported audio file format.'))

    def __parse_corpus(self, corpus: Iterable | Corpus, corpora: Iterable = []):
        if not corpus:
            return

        if isinstance(corpus, Iterable):
            # check that corpus features are compatible
            prev_features = set(corpus[0].features)
            for i, c in enumerate(corpus[1:], 1):
                current_features = set(c.features)
                if prev_features != current_features:
                    raise ValueError(
                        LOGGER.error(
                            f'Corpus at index {i} has a different set of features ({c.features}) than corpus at index {i-1} ({corpus[i-1].features}). When using more than one corpus, make sure they are based on the same feature set.'))
                prev_features = current_features
            # recursively unpack corpora
            for c in corpus:
                return self.__parse_corpus(c)

        elif isinstance(corpus, Corpus):
            corpora.append(corpus)

        else:
            raise ValueError(f'{corpus} is not a corpus')
        return corpora

    def __build(self, corpora: Iterable, sr: int | None = None) -> None:
        y, self.sr = load(self.target, sr=sr)
        if self.beat_unit:
            self.hop_length = int((self.sr * 60) / (tempo(y=y, sr=self.sr)[0] / self.beat_unit))
        target_analysis = self._analyze_audio_file(y=y, features=corpora[0].features, sr=self.sr)[0]

        # include separate corpus for target
        self.soundfiles[-1] = {
            'source_root': "",
            'max_duration': None,
            'sources': {
                0: {
                    'file': self.target,
                    'sr': self.sr,
                    'y': y,
                }
            }
        }

        for corpus_id, corpus in enumerate(corpora):
            self.soundfiles[corpus_id] = {
                'source_root': corpus.source_root,
                'max_duration': corpus.max_duration,
                'sources': {}
            }
        for x in target_analysis:
            matches = []
            for corpus_id, corpus in enumerate(corpora):
                nearest_neighbors = corpus.tree.knn(
                    x=x,
                    vector_path='features',
                    first_n=corpus.tree.leaf_size)
                for nn in nearest_neighbors:
                    # get id of source audio file
                    source_id = nn['value']['source']
                    self.soundfiles[corpus_id]['sources'][source_id] = corpus.soundfiles[source_id]
                    nn['value']['corpus'] = corpus_id
                    option = deepcopy(nn)
                    del option['value']['features']
                    matches.append(option)
            self.frames.append([x['value'] for x in sorted(matches, key=lambda x: x['cost'])])

    def _serialize(self, spinner):
        mosaic = deepcopy(vars(self))
        spinner.next()

        # if not portable, delete audio samples from soundfiles on write
        if not self.portable:
            for corpus_id in mosaic['soundfiles']:
                for source_id in mosaic['soundfiles'][corpus_id]['sources']:
                    del mosaic['soundfiles'][corpus_id]['sources'][source_id]['y']
                    spinner.next()
        return mosaic

    def _summarize(self) -> dict:
        return {
            "portable": self.portable,
            "target": self.target,
            "num. of grains": len(self.frames)
        }

    def _preload(self, obj):
        # reload soundfiles if non-portable
        if not obj['portable']:
            self.__load_soundfiles(obj['soundfiles'])
        return obj

    def read(self, file: str) -> None:
        return super().read(file, warn_user=self.frames)

    def __load_soundfiles(self, soundfiles):
        self.counter.message = LOGGER.subprocess('Loading audio files: ')
        for corpus_id in soundfiles:
            corpus = soundfiles[corpus_id]
            sources = corpus['sources']
            for source_id in sources:
                source = sources[source_id]
                path = join(corpus['source_root'], source['file'])
                if 'y' in source:
                    continue
                soundfiles[corpus_id]['sources'][source_id]['y'] = load(path, sr=source['sr'], duration=corpus['max_duration'])[0]
                self.counter.next()
        self.counter.finish()

    def __preprocess_samples(self, soundfiles: dict, n_chans: int, sr: int) -> None:
        c = Counter(LOGGER.subprocess('Preprocessing audio files: '))
        for corpus_id in soundfiles:
            sources = soundfiles[corpus_id]['sources']
            for source_id in sources:
                source = sources[source_id]
                y = source['y']
                sr_ratio = sr/source['sr']
                if source['sr'] != sr:
                    y = resample_array(y, int(len(y) * sr_ratio))
                soundfiles[corpus_id]['sources'][source_id]['y'] = np.repeat(np.array([y]).T, n_chans, axis=1)
                c.next()
        c.finish()

    def to_audio(self,
                 # dynamic control parameters
                 accuracy: float | int | Envelope | Iterable = 1.0,
                 grain_dur: float | int | Envelope | Iterable = 0.1,
                 stretch_factor: float | int | Envelope | Iterable = 1.0,
                 onset_var: float | int | Envelope | Iterable = 0,
                 target_mix: float | int | Envelope | Iterable = 0,
                 pan_depth: float | int | Envelope | Iterable = 5,
                 grain_envelope: Envelope | str | Iterable = Envelope(),

                 # static parameters
                 n_chans: int = 2,
                 sr: int | None = None,
                 win_length_res: int = 512) -> AudioBuffer:
        """
        Returns an audio mosaic as an ``AudioBuffer`` instance.

        accuracy: float | int | Envelope | Iterable = 1.0
            Normalized probablity (0.0 - 1.0) of choosing the best possible match from ``Corpus`` for each grain in ``target``.

        grain_dur: float | int | Envelope | Iterable = 0.1
            Grain duration in seconds.

        stretch_factor: float | int | Envelope | Iterable = 1.0
            Stretch factor of audio output (e.g., 1: original speed, 0.5: twice as fast, 2: twice as slow, etc.)

        onset_var: float | int | Envelope | Iterable = 0
            Grain onset random variation in seconds.

        target_mix: float | int | Envelope | Iterable = 0
            Probabily of choosing grain from audio target instead of one from input ``Corpus``. 

        pan_depth: float | int | Envelope | Iterable = 5
            Depth of contrast for channel panning

        grain_envelope: Envelope | str | Iterable = Envelope()
            Amplitude envelope for all audio grains.

        n_chans: int = 2
            Number of output audio channels.

        sr: int | None = None
            Sampling rate for audio output.

        win_length_res: int = 512
            Grain duration resolution in samples.

        """
        n_segments = len(self.frames)

        def as_points(param, N: int = n_segments) -> Points:
            if isinstance(param, Envelope):
                return param.get_points(N)
            elif isinstance(param, Iterable):
                return Envelope(shape=param).get_points(N)
            else:
                return Points().fill(N, param)

        st = time()
        LOGGER.process(f'Generating audio from mosaic target: {basename(self.target)}...').print()
        # playback ratio
        sr, sr_ratio = (self.sr, 1) if not sr else (sr, sr/self.sr)
        hop_length = int(self.hop_length * sr_ratio)

        soundfiles = deepcopy(self.soundfiles)
        self.__preprocess_samples(soundfiles, n_chans=n_chans, sr=sr)

        # DYNAMIC CONTROL TABLES
        LOGGER.subprocess('Creating parameter envelopes...').print()
        target_mix_table = as_points(target_mix).clip(0.0, 1.0)

        win_length_table = (as_points(grain_dur) * sr).quantize(win_length_res).astype('int64')

        max_win_length = np.amax(win_length_table) + win_length_res
        win_lengths = np.arange(win_length_res, max_win_length, win_length_res, dtype='int64')

        samp_onset_table = (as_points(stretch_factor)
                            * hop_length).quantize().concat([0], prepend=True).astype('int64').cumsum()[:-1]

        # apply onset variation to samp_onset_table
        samp_onset_var_table = (np.random.rand(n_segments) - 0.5) * as_points(onset_var) * (sr // 2)
        samp_onset_table += samp_onset_var_table.astype('int64')
        samp_onset_table[samp_onset_table < 0] = 0

        # compute amplitude windows
        windows = [as_points(grain_envelope, wl).wrap().T.replicate(n_chans, axis=1) for wl in win_lengths]

        # compute panning table
        pan_depth_table = as_points(pan_depth).wrap().T.replicate(n_chans, axis=1)
        pan_table = Points(np.linspace(0, 1, n_chans)).wrap().replicate(n_segments, axis=0) - np.random.rand(n_segments, 1)
        pan_table = 1 / (2**(pan_depth_table * pan_table.abs()))
        pan_table /= pan_table.sum(axis=1)[:, np.newaxis]

        # make buffer array
        buffer = np.empty(shape=(int(np.amax(samp_onset_table) + np.amax(win_length_table)), n_chans))
        buffer.fill(0)

        grain_counter = IncrementalBar(
            LOGGER.subprocess('Concatenating grains: '),
            max=len(self.frames),
            suffix='%(index)d/%(max)d grains')

        accuracy_table = as_points(accuracy).clip(0.0, 1.0)

        for n, (ds, so, fl, p, tm, ac) in enumerate(zip(self.frames,
                                                        samp_onset_table,
                                                        win_length_table,
                                                        pan_table,
                                                        target_mix_table,
                                                        accuracy_table)):
            if random() > tm:
                num_frames = max(1, int(len(ds) * (1 - ac)))
                weights = np.linspace(1.0, 0.0, num_frames)
                f = choices(ds[:num_frames], weights=weights)[0]
                amp = 1.0
            else:
                f = {
                    'corpus': -1,
                    'source': 0,
                    'marker': n * self.hop_length,
                }
                amp = tm
            source_id = f['source']
            corpus_id = f['corpus']
            source = soundfiles[corpus_id]['sources'][source_id]['y']
            source_sr_ratio = sr/soundfiles[corpus_id]['sources'][source_id]['sr']
            max_idx = len(source) - 1
            samp_st = int(f['marker'] * source_sr_ratio)
            samp_end = min(max_idx, samp_st+fl)
            seg_size = round((samp_end-samp_st) / win_length_res) * win_length_res
            samp_end = samp_st+seg_size
            if seg_size > 0 and samp_end <= max_idx:
                idx = int(np.where(win_lengths == seg_size)[0])
                window = windows[idx]
                segment = source[samp_st:samp_end] * window * p * amp
                buffer[so:so+seg_size] = buffer[so:so+seg_size] + segment
            grain_counter.next()

        grain_counter.finish()
        LOGGER.elapsed_time(st).print()

        # return normalized buffer
        return AudioBuffer(y=(buffer / np.amax(np.abs(buffer))) * np.sqrt(0.5), sr=sr)
