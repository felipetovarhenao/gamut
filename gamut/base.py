from abc import ABC, abstractmethod
from librosa import magphase, stft
from librosa.feature import mfcc, chroma_stft
from librosa import samples_like
import numpy as np
from os import rename
from progress.spinner import PieSpinner
from os.path import basename, splitext
from time import time
from collections.abc import Iterable

from .config import FILE_EXT, LOGGER
import numpy.typing as npt


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

    @abstractmethod
    def _serialize(self):
        raise NotImplementedError

    @abstractmethod
    def _preload(self):
        raise NotImplementedError

    def write(self, output: str, portable: bool = False) -> None:
        """ Writes a ``.gamut`` file to disk """
        st = time()
        self.portable = portable
        output_dir = splitext(output)[0]
        spinner = PieSpinner(
            LOGGER.disk(f'{"" if portable else "non-"}portable {self.type}', f'{basename(output_dir)}{FILE_EXT}'))
        spinner.next()
        serialized_object = self._serialize(spinner=spinner)

        # write file and set correct file extension
        np.save(output_dir, serialized_object)
        spinner.next()
        rename(output_dir + '.npy', output_dir+FILE_EXT)
        spinner.finish()
        LOGGER.elapsed_time(st).print()
        return self

    def read(self, file: str, warn_user=False) -> None:
        """ Reads a ``.gamut`` file from disk """
        if warn_user:
            raise UserWarning(f"This {self.type} already has a source")

        # validate file
        if splitext(file)[1] != FILE_EXT:
            raise ValueError(
                'Wrong file extension. Provide a directory for a {} file'.format(FILE_EXT))
        st = time()
        serialized_object = np.load(file, allow_pickle=True).item()
        is_portable = serialized_object['portable']
        LOGGER.disk(f'{"" if is_portable else "non-"}portable {self.type}',
                    basename(file), read=True).print()

        serialized_object = self._preload(serialized_object)

        # assign attributes to self
        for attr in serialized_object:
            if hasattr(self, attr):
                setattr(self, attr, serialized_object[attr])

        LOGGER.elapsed_time(st).print()
        return self

    def __get_type(self):
        """ Helper function to get subclass name """
        return self.__class__.__name__.lower()

    def _analyze_audio_file(self, y: npt.NDArray, features: Iterable, sr: int | None = None) -> tuple:
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
            chroma_features = chroma_stft(S=S,
                                          sr=sr,
                                          n_fft=self.n_fft,
                                          win_length=self.win_length,
                                          hop_length=self.hop_length)
            analysis.extend(chroma_features)

        analysis = np.array(analysis).T[:-1]

        markers = samples_like(X=analysis,
                               hop_length=self.hop_length,
                               n_fft=self.n_fft,
                               axis=0)

        return analysis, markers
