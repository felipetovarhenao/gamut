# librosa
from librosa import load

# utils
from os.path import realpath, basename, isdir, splitext, join, commonprefix, relpath
from os import walk
from progress.counter import Counter
from time import time
from copy import deepcopy
import re
from collections.abc import Iterable

# gamut
from .trees import KDTree
from .config import AUDIO_FORMATS, LOGGER, ANALYSIS_TYPES
from .base import Analyzer


class Corpus(Analyzer):
    """ 
    A ``Corpus`` represents a collection of one or more audio sources, from which a ``Mosaic`` can be built.
    Internally, the audio sources are analyzed and decomposed into grains.\n
    Based on the audio features of these grains (e.g., timbre or pitch content), a k-dimensional search tree is built, 
    which helps to optimize the process of finding the best matches for a given audio target.

    source: str | list | None = None
        Source file(s) from which to build the ``Corpus``.\n 
        ``source`` can be either a ``str`` or a list of ``str``, where ``str`` is an audio file path or a directory of audio files. 

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

    leaf_size: int = 10
        Maximum number of data items per leaf in the k-dimensional binary search tree.
    """

    def __init__(self,
                 source: str | list | None = None,
                 max_duration: int | None = None,
                 leaf_size: int | None = 10,
                 features: Iterable = ['timbre'],
                 *args,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = source
        self.max_duration = max_duration
        self.features = features
        self.source_root = ""
        self.tree = KDTree(leaf_size=leaf_size)
        self.counter = Counter(message=LOGGER.subprocess('Analyzing audio samples: '))

        for f in self.features:
            if f in ANALYSIS_TYPES:
                continue
            raise ValueError(
                LOGGER.error(
                    f'"{f}" is not a valid feature option. To see the list of valid features, use the {self.type.capitalize()}.print_feature_choices() class method.'))
        if len(self.features) == 0:
            raise ValueError(f'You must specify at least one audio feature to instantiate a {self.type.capitalize()} instance')

        self.soundfiles = []
        if self.source:
            st = time()
            self.__build()
            LOGGER.elapsed_time(st)

    def __build(self) -> None:
        """ build corpus from `source` """
        st = time()
        LOGGER.process('Building audio corpus...').print()
        data = self.__compile()
        self.counter.finish()
        self.__set_source_root()
        self.tree.build(data=data, vector_path='features')
        LOGGER.elapsed_time(st).print()

    def _summarize(self) -> dict:
        filenames = "\n"
        for i, sf in enumerate(self.soundfiles):
            fn = basename(sf['file'])
            filenames += [f'\t{fn}', f', {fn}', f', {fn}\n'][[0, 1, 1, 2][i % 4]]
        return {
            "portable": self.portable,
            "source root": self.source_root,
            "max. used source duration": f'{self.max_duration}' + ("s" if self.max_duration else ""),
            "max. tree leaf size": self.tree.leaf_size,
            "analysis features": f'[{", ".join(self.features)}, ]',
            f'sources ({len(self.soundfiles)})': filenames,
        }

    def __compile(self, source: list | str | None = None, excuded_files: list = [], data: list = []) -> None:
        """ recursively collects and extracts features from all audio files in `source` """
        source = source or self.source
        source_type = type(source or self.source)
        if source_type == list:
            for x in source:
                self.__compile(x, excuded_files)
            return data

        source_path = realpath(source)
        if isdir(source_path):
            for root, _, files in walk(source_path):
                for f in files:
                    self.__compile(join(root, f), excuded_files)
            return data

        filename, ext = splitext(basename(source))
        if ext.lower() not in AUDIO_FORMATS or filename in excuded_files:
            return data

        excuded_files.append(excuded_files)
        y, sr = load(path=source, sr=None, mono=True,
                     duration=self.max_duration)
        source_id = len(self.soundfiles)
        self.soundfiles.append({
            'file': source,
            'sr': sr,
            'y': y
        })
        analysis, markers = self._analyze_audio_file(y=y, features=self.features, sr=sr)
        self.counter.next()
        data.extend([{
            'source': source_id,
            'marker': marker,
            'features': features,
        } for features, marker in zip(analysis, markers)])
        return data

    @classmethod
    def print_feature_choices(cls) -> None:
        print(f'feature choices: {ANALYSIS_TYPES}')

    def __set_source_root(self):
        """ remove commonprefix from file paths to avoid size overhead when writing corpus to disk """

        if not self.soundfiles:
            raise ValueError(LOGGER.error('Corpus does not contain any source audio files'))
        if len(self.soundfiles) == 1:
            return
        pattern = re.compile(r'(\/.*)*/')
        self.source_root = pattern.search(commonprefix([sf['file'] for sf in self.soundfiles])).group()
        for i, sf in enumerate(self.soundfiles):
            self.soundfiles[i]['file'] = relpath(sf['file'], self.source_root)

    def _serialize(self, spinner: object) -> dict:
        """ called from within write method """
        corpus = deepcopy({**vars(self), 'tree': vars(self.tree)})

        # if not portable, delete audio samples from soundfiles on write
        if not self.portable:
            for sf in corpus['soundfiles']:
                spinner.next()
                del sf['y']
        return corpus

    def _preload(self, obj: object) -> dict:
        """ called from within read method """
        gamut_type = obj['type']
        if gamut_type != self.type:
            raise ValueError(
                f'source file should be a {self.type}, not a {gamut_type}')
        tree = KDTree()
        tree.read(obj['tree'])
        obj['tree'] = tree

        # re-load audio files if corpus file is not portable
        if not obj['portable']:
            self.counter.message = LOGGER.subprocess('Loading audio files: ')
            for sf in obj['soundfiles']:
                path = join(obj['source_root'], sf['file'])
                sf['y'] = load(path, sr=sf['sr'])[0]
                self.counter.next()
            self.counter.finish()
        return obj

    def read(self, file: str) -> None:
        return super().read(file, warn_user=self.source)
