# librosa
from librosa import load

# utils
from os.path import realpath, basename, isdir, splitext, join, commonprefix, relpath
from os import walk
from progress.counter import Counter
from time import time
from copy import deepcopy

# gamut
from .trees import KDTree
from .config import AUDIO_FORMATS, LOGGER
from .base import AudioAnalyzer


class Corpus(AudioAnalyzer):
    """ 
    Audio corpus class 

    Attributes
    ----------
    source: str | list | None = None
        Source file(s) from which to build the corpus. 
        `source` can be either a `str` or a list of `str`, where `str` is an audio file or a directory of audio files. 

    max_duration: str | list | None = None
        Maximum audio file duration to use in corpus. Applies to all audio files found in `source`.

    n_mfcc: int = 13
        Number of MFCC coefficients to use in audio analysis.

    hop_length: int = 512
        hop size in audio samples.

    frame_length: int = 1024
        window size in audio samples.

    n_fft: int = 512
        Number of FFT bins

    leaf_size: int = 10
        Maximum number of data items per leaf, in binary search tree.

    Methods
    ----------
    write(output, portable=False):
        Writes a `.gamut` corpus file to disk. If `portable=True`, it includes all audio files.
        Otherwise, it will reload all audio files when reading file with `read()` method.

    read(source: int)
        Reads a `.gamut` corpus file from disk.
    """

    def __init__(self,
                 source: str | list | None = None,
                 max_duration: int | None = None,
                 leaf_size: int = 10,
                 *args,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.source = source
        self.max_duration = max_duration
        self.portable = False

        self.source_root = ""
        self.tree = KDTree(leaf_size=leaf_size)
        self.counter = Counter(
            message=LOGGER.subprocess('Analyzing audio samples: '))

        self.soundfiles = list()
        if self.source:
            st = time()
            self.__build()
            LOGGER.elapsed_time(st)

    def __build(self):
        """ build corpus from `source` """
        st = time()
        LOGGER.process('Building audio corpus...').print()
        data = self.__compile()
        self.counter.finish()
        self.__set_source_root()
        self.tree.build(data=data, vector_path='features')
        LOGGER.elapsed_time(st).print()

    def __compile(self, source: list | str | None = None, excuded_files: list = list(), data: list = list()) -> None:
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
        analysis, markers = self._analyze_audio_file(y=y, sr=sr)
        self.counter.next()
        data.extend([{
            'source': source_id,
            'marker': marker,
            'features': features,
        } for features, marker in zip(analysis, markers)])
        return data

    def __set_source_root(self):
        """ remove commonprefix from file paths to avoid size overhead when writing corpus to disk """

        if not self.soundfiles:
            raise BufferError('Input source does not contain any audio files')
        if len(self.soundfiles) == 1:
            return
        self.source_root = commonprefix([sf['file'] for sf in self.soundfiles])
        for i, sf in enumerate(self.soundfiles):
            self.soundfiles[i]['file'] = relpath(sf['file'], self.source_root)

    def serialize(self, spinner):
        """ called from within write method """
        corpus = deepcopy({**vars(self), 'tree': vars(self.tree)})

        # if not portable, delete audio samples from soundfiles on write
        if not self.portable:
            for sf in corpus['soundfiles']:
                spinner.next()
                del sf['y']
        return corpus

    def preload(self, obj):
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
