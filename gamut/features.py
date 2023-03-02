from __future__ import annotations
# librosa
from librosa import magphase, stft, samples_like, load
from librosa.feature import mfcc, chroma_stft, rms
from librosa.beat import tempo

# gamut
from .controls import Points, Envelope, object_to_points
from .utils import resample_array
from .audio import AudioBuffer
from .config import FILE_EXT, CONSOLE, ANALYSIS_TYPES, MIME_TYPES, get_elapsed_time
from .data import KDTree

# os
from os.path import realpath, basename, isdir, splitext, join, commonprefix, relpath, dirname
from os import walk, rename

# misc utils
import filetype
from random import choices, random
from copy import deepcopy
from time import time

# typing
from typing_extensions import Self
from collections.abc import Iterable
from abc import ABC, abstractmethod

# numpy
import numpy as np


class Analyzer(ABC):
    """ 
    Abstract base class from which the ``Corpus`` and ``Mosaic`` classes inherit. 
    It provides the base methods for feature extraction and reading/writing ``.gamut`` files.

    n_mfcc: int = 13
        Number of mel frequency cepstral coefficients to use in mfcc analysis.

    hop_length: int = 512
        Size in audio samples of space between windowing frames.

    win_length: int = 1024
        Size in audio samples of windowing frames.

    n_fft: int = 1024
        Number of FFT bins
    """

    def __init__(self,
                 n_mfcc: int = 13,
                 hop_length: int = 512,
                 win_length: int = 1024,
                 n_fft: int = 1024) -> None:
        self.n_mfcc = n_mfcc
        self.hop_length = hop_length
        self.n_fft = n_fft
        self.win_length = win_length
        self.type = self.__get_type()
        self.name = None
        self.portable = False

    @abstractmethod
    def _serialize(self):
        raise NotImplementedError

    @abstractmethod
    def _preload(self):
        raise NotImplementedError

    @abstractmethod
    def _summarize(self):
        raise NotImplementedError

    def summarize(self) -> None:
        """ Prints a summary of the current structure of the object """
        summary = self._summarize()
        if self.name:
            summary = {'name': self.name, **summary}
        line = "".join("-" for _ in range(90))
        CONSOLE.log_process(f"*** {self.type.upper()} SUMMARY ***\n{CONSOLE.c3}{line}").print()
        for key in summary:
            val = summary[key]
            print(f"{CONSOLE.c4}{key.upper()}: {CONSOLE.reset}{val}")
        print(f'{CONSOLE.c3}{line}{CONSOLE.reset}')

    @get_elapsed_time
    def write(self, output: str, portable: bool = False) -> None:
        """ Writes a ``.gamut`` file to disk """
        self.portable = portable
        self.name = splitext(basename(output))[0]
        output_dir = splitext(output)[0]
        CONSOLE.log_disk_op(f'{"" if portable else "non-"}portable {self.type}', f'{realpath(output_dir)}{FILE_EXT}').print()
        serialized_object = self._serialize()

        # write file and set correct file extension
        np.save(output_dir, serialized_object)
        rename(output_dir + '.npy', output_dir+FILE_EXT)
        return self

    @get_elapsed_time
    def read(self, file: str, warn_user=False) -> Self:
        """ Reads a ``.gamut`` file from disk """
        if warn_user:
            CONSOLE.warn(f"This {self.type} already has a source")

        # validate file
        if splitext(file)[1] != FILE_EXT:
            CONSOLE.error(ValueError, 'Wrong file extension. Provide a directory for a {} file'.format(FILE_EXT))

        serialized_object = np.load(file, allow_pickle=True).item()
        if serialized_object['type'] != self.type:
            CONSOLE.error(TypeError, 'The specified file .gamut file is a {}, not a {}.'.format(
                serialized_object['type'], self.type))
        is_portable = serialized_object['portable']
        CONSOLE.log_disk_op(f'{"" if is_portable else "non-"}portable {self.type}', basename(file), read=True).print()

        serialized_object = self._preload(serialized_object)

        # assign attributes to self
        for attr in serialized_object:
            if hasattr(self, attr):
                setattr(self, attr, serialized_object[attr])

        return self

    def __get_type(self) -> str:
        """ Helper function to get subclass name """
        return self.__class__.__name__.lower()

    def _analyze_audio_file(self, y: np.ndarray, features: Iterable, sr: int | None = None) -> tuple:
        """ Extracts audio features from an ``ndarray`` of audio samples """
        S = magphase(stft(y=y,
                          n_fft=self.n_fft,
                          win_length=self.win_length,
                          hop_length=self.hop_length))[0]

        analysis = []
        if 'timbre' in features:
            mfcc_features = mfcc(S=S,
                                 sr=sr,
                                 n_mfcc=self.n_mfcc,
                                 hop_length=self.hop_length)

            analysis.extend(mfcc_features)

        if 'pitch' in features:
            loudness = rms(S=S,
                           frame_length=self.win_length,
                           hop_length=self.hop_length)
            chroma_features = chroma_stft(S=S,
                                          sr=sr,
                                          n_fft=self.n_fft,
                                          win_length=self.win_length,
                                          hop_length=self.hop_length)
            analysis.extend(np.concatenate([chroma_features, loudness]))

        analysis = np.array(analysis).T[:-1]

        markers = samples_like(X=analysis,
                               hop_length=self.hop_length,
                               n_fft=self.n_fft,
                               axis=0)

        return analysis, markers


class Corpus(Analyzer):
    """ 
    A ``Corpus`` represents a collection of one or more audio sources, from which a ``Mosaic`` can be built.
    Internally, the audio sources are analyzed and decomposed into grains.\n
    Based on the audio features of these grains (e.g., timbre or pitch content), a k-dimensional search tree is built, 
    which helps to optimize the process of finding the best matches for a given audio target.

    source: str | list | None = None
        Source file(s) from which to build the ``Corpus``. ``source`` can be either a ``str`` or a list of ``str``, where 
        ``str`` is an audio file path or a directory of audio files. Note that, for any directory path, ``Corpus`` will recursively look for
        any ``.wav``, ``.aif``, or ``.mp3`` audio files in folders and subfolders.

    max_duration: str | list | None = None
        Maximum audio file duration to use in ``Corpus``. Applies to all audio files found in ``source``.

    n_mfcc: int = 13
        Number of mel frequency cepstral coefficients to use in audio analysis.

    hop_length: int = 512
        hop size in audio samples.

    win_length: int = 1024
        window size in audio samples.

    n_fft: int = 512
        Number of FFT bins

    features: Iterable = ['timbre']
        List of ``str``, specifying audio feature(s) to use for audio source analysis. The options are ``"timbre"`` and/or ``"pitch"``.

    leaf_size: int = 10
        Maximum number of data items per leaf in the k-dimensional binary search tree.
    """

    def __init__(self,
                 source: str | list | None = None,
                 max_duration: int | None = None,
                 leaf_size: int | None = 15,
                 features: Iterable = ['timbre'],
                 *args,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = source
        self.max_duration = max_duration
        self.features = features
        self.source_root = ""
        self.tree = KDTree(leaf_size=leaf_size)
        CONSOLE.reset_counter('Analyzing audio samples: ')

        for f in self.features:
            if f in ANALYSIS_TYPES:
                continue
            CONSOLE.error(
                ValueError,
                f'"{f}" is not a valid feature option. To see the list of valid features, use the {self.type.capitalize()}.print_feature_choices() class method.')
        if len(self.features) == 0:
            CONSOLE.error(
                ValueError, f'You must specify at least one audio feature to instantiate a {self.type.capitalize()} instance')

        self.soundfiles = []
        if self.source:
            self.__build()

    @get_elapsed_time
    def __build(self) -> None:
        """ build corpus from `source` """
        CONSOLE.log_process('\N{brain} Building audio corpus...').print()
        data = self.__compile(source=None, data=[], excluded_files=[])
        CONSOLE.counter.finish()
        self.__set_source_root()
        self.tree.build(data=data, vector_path='features')

    def _summarize(self) -> dict:
        filenames = "\n"
        for i, sf in enumerate(self.soundfiles):
            fn = basename(sf['file'])
            filenames += [f'\t{fn}', f', {fn}', f', {fn}\n'][[0, 1, 1, 2][i % 4]]
        return {
            "source root": self.source_root,
            "portable": self.portable,
            "max. duration per source": f'{self.max_duration}' + ("s" if self.max_duration else ""),
            "max. tree leaf size": self.tree.leaf_size,
            "analysis features": f'[{", ".join(self.features)}, ]',
            f'sources ({len(self.soundfiles)})': filenames,
        }

    def __compile(self, source: list | str | None = None, excluded_files: list = [], data: list = []) -> None:
        """ recursively collects and extracts features from all audio files in `source` """
        source = source or self.source
        source_type = type(source or self.source)
        if source_type == list:
            for x in source:
                self.__compile(x, excluded_files=excluded_files, data=data)
            return data

        source_path = realpath(source)
        if isdir(source_path):
            for root, _, files in walk(source_path):
                for f in files:
                    self.__compile(join(root, f), excluded_files=excluded_files, data=data)
            return data

        filename = splitext(basename(source))[0]
        kind = filetype.guess(source_path)
        if kind is None or kind.mime not in MIME_TYPES or filename in excluded_files:
            return data

        excluded_files.append(filename)

        y, sr = load(path=source, sr=None, mono=True,
                     duration=self.max_duration)
        source_id = len(self.soundfiles)
        self.soundfiles.append({
            'file': source,
            'sr': sr,
            'y': y
        })
        analysis, markers = self._analyze_audio_file(y=y, features=self.features, sr=sr)
        CONSOLE.counter.next()
        data.extend([{
            'source': source_id,
            'marker': marker,
            'features': features,
        } for features, marker in zip(analysis, markers)])

        return data

    @classmethod
    def print_feature_choices(cls) -> None:
        print(f'feature choices: {ANALYSIS_TYPES}')

    def __set_source_root(self) -> None:
        """ remove commonprefix from file paths to avoid size overhead when writing corpus to disk """

        if not self.soundfiles:
            CONSOLE.error(ValueError, 'Corpus does not contain any source audio files')
        if len(self.soundfiles) == 1:
            return
        self.source_root = dirname(commonprefix([sf['file'] for sf in self.soundfiles]))
        for i, sf in enumerate(self.soundfiles):
            self.soundfiles[i]['file'] = relpath(sf['file'], self.source_root)

    def _serialize(self) -> dict:
        """ called from within write method """
        corpus = deepcopy({**vars(self), 'tree': vars(self.tree)})

        # if not portable, delete audio samples from soundfiles on write
        if not self.portable:
            for sf in corpus['soundfiles']:
                del sf['y']
        return corpus

    def _preload(self, obj: object) -> dict:
        """ called from within read method """
        gamut_type = obj['type']
        if gamut_type != self.type:
            CONSOLE.error(ValueError, f'source file should be a {self.type}, not a {gamut_type}')
        tree = KDTree()
        tree.read(obj['tree'])
        obj['tree'] = tree

        # re-load audio files if corpus file is not portable
        if not obj['portable']:
            CONSOLE.counter.message = CONSOLE.log_subprocess('Loading audio files: ')
            for sf in obj['soundfiles']:
                path = join(obj['source_root'], sf['file'])
                sf['y'] = load(path, sr=sf['sr'])[0]
                CONSOLE.counter.next()
            CONSOLE.counter.finish()
        return obj

    def read(self, file: str) -> None:
        return super().read(file, warn_user=self.source)


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
                 corpus: Iterable | Corpus | None = None,
                 sr: int | None = None,
                 beat_unit: float | int | None = None,
                 *args,
                 **kwargs) -> None:
        self.__validate(target, corpus)
        super().__init__(*args, **kwargs)

        self.target = target
        self.sr = sr
        self.frames = []
        self.beat_unit = beat_unit
        self.features = []
        self.duration = None

        corpora = self.__parse_corpus(corpus, [])
        self.soundfiles = {i: {} for i in range(-1, len(corpora or []))}

        if self.target and corpora:
            self.features = corpora[0].features
            self.__build(corpora=corpora, sr=sr)

    def __validate(self, target: str | None, corpus: Iterable | Corpus | None) -> None:
        if any([target, corpus]) and not all([target, corpus]):
            CONSOLE.error(
                ValueError,
                f'You must either provide both target and corpus attributes, or leave them blank to build Mosaic from {FILE_EXT} file')
        if not target:
            return
        target_path = realpath(target)
        if isdir(target_path):
            CONSOLE.error(ValueError, f'{target} is not a valid audio file path')
        kind = filetype.guess(target_path)
        if kind is None or kind.mime not in MIME_TYPES:
            CONSOLE.error(ValueError, f'{basename(target)} seems to be an invalid or unsupported audio file format.')

    def __parse_corpus(self, corpus: Iterable | Corpus, corpora: Iterable) -> Iterable:
        if not corpus:
            return

        if isinstance(corpus, Iterable):
            # check that corpus features are compatible
            prev_features = set(corpus[0].features)
            for i, c in enumerate(corpus[1:], 1):
                current_features = set(c.features)
                if prev_features != current_features:
                    CONSOLE.error(
                        ValueError,
                        f'Corpus at index {i} has a different set of features ({", ".join(c.features)}) than corpus at index {i-1} ({", ".join(corpus[i-1].features)}). When using more than one corpus, make sure they are based on the same feature set.')
                prev_features = current_features
            # recursively unpack corpora
            for c in corpus:
                self.__parse_corpus(c, corpora=corpora)
        elif isinstance(corpus, Corpus):
            corpora.append(corpus)
        else:
            CONSOLE.error(ValueError, f'{corpus} is not a corpus')
        return corpora

    @get_elapsed_time
    def __build(self, corpora: Iterable, sr: int | None = None) -> None:
        num_corpora = len(corpora)
        CONSOLE.log_process(
            f'\N{brain} Building mosaic for {basename(self.target)} from {"corpus" if num_corpora == 1 else f"{num_corpora} corpora"}...').print()
        CONSOLE.log_subprocess('Loading target...').print()
        y, self.sr = load(self.target, sr=sr)

        self.duration = len(y) / self.sr

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
        CONSOLE.reset_bar('Finding matches for target segments:', max=len(target_analysis), item='segments')
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
            CONSOLE.bar.next()
        CONSOLE.bar.finish()

    def _serialize(self) -> dict:
        mosaic = deepcopy(vars(self))

        # if not portable, delete audio samples from soundfiles on write
        if not self.portable:
            for corpus_id in mosaic['soundfiles']:
                for source_id in mosaic['soundfiles'][corpus_id]['sources']:
                    del mosaic['soundfiles'][corpus_id]['sources'][source_id]['y']
        return mosaic

    def _summarize(self) -> dict:
        return {
            "target": basename(self.target) if self.target else None,
            "num. of corpora": len([x for x in self.soundfiles]),
            "analysis features": self.features,
            "portable": self.portable,
            "duration": f'{round(self.duration * 10) / 10}s' if self.duration else None,
            "num. of grains": len(self.frames)
        }

    def _preload(self, obj: dict) -> dict:
        # reload soundfiles if non-portable
        if not obj['portable']:
            self.__load_soundfiles(obj['soundfiles'])
        return obj

    def read(self, file: str) -> Self:
        return super().read(file, warn_user=self.frames)

    def __load_soundfiles(self, soundfiles: Iterable) -> None:
        CONSOLE.counter.message = CONSOLE.log_subprocess('Loading audio files: ')
        for corpus_id in soundfiles:
            corpus = soundfiles[corpus_id]
            sources = corpus['sources']
            for source_id in sources:
                source = sources[source_id]
                if 'y' not in source:
                    path = join(corpus['source_root'], source['file'])
                    soundfiles[corpus_id]['sources'][source_id]['y'] = load(
                        path, sr=source['sr'], duration=corpus['max_duration'])[0]
                CONSOLE.counter.next()
        CONSOLE.counter.finish()

    @get_elapsed_time
    def to_audio(self,
                 # dynamic control parameters
                 fidelity: float | int | Envelope | Iterable = 1.0,
                 grain_dur: float | int | Envelope | Iterable = 0.1,
                 stretch_factor: float | int | Envelope | Iterable = 1.0,
                 onset_var: float | int | Envelope | Iterable = 0,
                 pan_depth: float | int | Envelope | Iterable = 5,
                 grain_env: str | Envelope | Iterable = "cosine",
                 corpus_weights: float | int | Envelope | Iterable = 1.0,

                 # static parameters
                 n_chans: int = 2,
                 sr: int | None = None,
                 win_length_res: int = 512) -> AudioBuffer:
        """
        Returns an *audio mosaic* as an ``AudioBuffer`` instance, based on several audio control parameters, such as `grain duration`, `onset variation`, `panning depth`, `grain envelope`, `grain duration`, `number of channels`, and more.

        fidelity: float | int | Envelope | Iterable = 1.0
            Normalized probablity (0.0 - 1.0) of choosing the best possible match from ``Corpus`` for each grain in ``target``.

        grain_dur: float | int | Envelope | Iterable = 0.1
            Grain duration in seconds.

        stretch_factor: float | int | Envelope | Iterable = 1.0
            Stretch factor of audio output (e.g., 1: original speed, 0.5: twice as fast, 2: twice as slow, etc.)

        onset_var: float | int | Envelope | Iterable = 0
            Grain onset variation in seconds.

        corpus_weights: float | int | Envelope | Iterable = 1.0,
            Probability of choosing grain from input ``Corpus`` (or ``list`` thereof) vs. from original audio ``target``.\n 
            Here are some examples that demonstrate the different ways in which this parameter can be specified:

                * ``int | float``: probability of choosing a grain from ``Corpus``. If more than one ``Corpus`` is given, the probability is equally distributed among them.
                * ``Envelope | List[float | int | tuple, ...]``: envelope of probabilities of choosing a grain from ``Corpus``. If a ``list`` of ``Corpus`` instances is given, the probability is equally distributed among them.
                * ``List[List[float | int | tuple, ...] | Envelope | (int | float), ...]``: ``list`` of envelopes of probabilities for chosing a grain from element at index ``i``, where ``i = 0`` is the ``target`` and the rest are all ``Corpus`` instances passed to ``corpus`` argument.

        pan_depth: float | int | Envelope | Iterable = 5
            Depth of contrast for channel panning

        grain_env: Envelope | str | Iterable = Envelope()
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
            """ resolve parameter into a ``Points`` instance based on type """
            return object_to_points(param, N)

        def parse_corpus_weights_param(param: Envelope | float | int) -> np.ndarray:
            """ Generates corpus weights table based on param type """
            even_weights = True
            num_corpora = len(self.soundfiles.keys()) - 1
            # when weigths are meant to control target vs all corpora
            # NOTE: tuple instance used here for backwards typing compatibility, needed for non-native classes
            if isinstance(param, (Envelope, float, int)) or (
                    isinstance(param, Iterable) and all([isinstance(p, int | float | tuple) for p in param])):
                wet_mix = as_points(param).clip(min=0.0, max=1.0)
                mix_table = np.array([1.0-wet_mix] + [wet_mix for _ in range(num_corpora)]).T
            # when weights are meant to control target and corpora individually
            else:
                if len(param) != num_corpora + 1:
                    CONSOLE.error(
                        ValueError,
                        f'The number of items in corpus_weights argument must be {num_corpora + 1}, where the first element is the target')
                mix_table = np.array([as_points(env).clip(min=0.0, max=1.0) for env in param]).T
                even_weights = False
            return mix_table / mix_table.sum(axis=1)[:, np.newaxis], even_weights

        def preprocess_samples(n_chans: int, sr: int) -> None:
            """ resamples files with conflicting sampling rates """
            soundfiles = deepcopy(self.soundfiles)
            CONSOLE.reset_counter('Preprocessing audio files: ')
            for corpus_id in soundfiles:
                sources = soundfiles[corpus_id]['sources']
                for source_id in sources:
                    source = sources[source_id]
                    y = source['y']
                    sr_ratio = sr/source['sr']
                    if source['sr'] != sr:
                        y = resample_array(y, int(len(y) * sr_ratio))
                    soundfiles[corpus_id]['sources'][source_id]['y'] = np.repeat(np.array([y]).T, n_chans, axis=1)
                    CONSOLE.counter.next()
            CONSOLE.counter.finish()
            return soundfiles

        CONSOLE.log_process(f'\N{brain} Generating audio from mosaic target: {basename(self.target)}...').print()
        # playback ratio
        sr, sr_ratio = (self.sr, 1) if not sr else (sr, sr/self.sr)
        hop_length = int(self.hop_length * sr_ratio)

        soundfiles = preprocess_samples(n_chans=n_chans, sr=sr)

        # DYNAMIC CONTROL TABLES
        CONSOLE.log_subprocess('Creating parameter envelopes...').print()

        corpus_weights_table, even_weights = parse_corpus_weights_param(corpus_weights)

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
        windows = [as_points(grain_env, wl).wrap().T.replicate(n_chans, axis=1) for wl in win_lengths]

        # compute panning table
        pan_depth_table = as_points(pan_depth).wrap().T.replicate(n_chans, axis=1)
        pan_table = Points(np.linspace(0, 1, n_chans)).wrap().replicate(n_segments, axis=0) - np.random.rand(n_segments, 1)
        pan_table = 1 / (2**(pan_depth_table * pan_table.abs()))
        pan_table /= pan_table.sum(axis=1)[:, np.newaxis]

        # make buffer array
        buffer = np.empty(shape=(int(np.amax(samp_onset_table) + np.amax(win_length_table)), n_chans))
        buffer.fill(0)

        CONSOLE.reset_bar('Concatenating grains:', max=len(self.frames), item='grains')

        fidelity_table = as_points(fidelity).clip(0.0, 1.0)

        for n, (frames, grain_onset, win_length, pan_value, corpora_weights, fidelity_value) in enumerate(
                zip(self.frames, samp_onset_table, win_length_table, pan_table, corpus_weights_table, fidelity_table)):
            target_weight = corpora_weights[0]
            if random() > target_weight:
                # use choices from a single corpus if corpora_mix was provided
                amp = 1.0
                candidates = frames
                if not even_weights:
                    corpus_id = choices([x for x in self.soundfiles.keys() if x != -1], weights=corpora_weights[1:])[0]
                    candidates = [x for x in candidates if x['corpus'] == corpus_id]

                num_candidates = max(1, int(len(candidates) * (1 - fidelity_value)))
                weights = np.linspace(1.0, 0.0, num_candidates)
                f = choices(candidates[:num_candidates], weights=weights)[0]
            else:
                f = {
                    'corpus': -1,
                    'source': 0,
                    'marker': n * self.hop_length,
                }
                amp = target_weight
            source_id = f['source']
            corpus_id = f['corpus']
            source = soundfiles[corpus_id]['sources'][source_id]['y']
            source_sr_ratio = sr/soundfiles[corpus_id]['sources'][source_id]['sr']
            max_idx = len(source) - 1
            grain_start = int(f['marker'] * source_sr_ratio)
            grain_end = min(max_idx, grain_start+win_length)
            grain_size = round((grain_end-grain_start) / win_length_res) * win_length_res
            grain_end = grain_start+grain_size
            if grain_size > 0 and grain_end <= max_idx:
                idx = int(np.where(win_lengths == grain_size)[0])
                window = windows[idx]
                grain = source[grain_start:grain_end] * window * pan_value * amp
                buffer[grain_onset:grain_onset+grain_size] = buffer[grain_onset:grain_onset+grain_size] + grain
            CONSOLE.bar.next()

        CONSOLE.bar.finish()

        # return normalized buffer
        return AudioBuffer(y=(buffer / np.amax(np.abs(buffer))) * np.sqrt(0.5), sr=sr)
