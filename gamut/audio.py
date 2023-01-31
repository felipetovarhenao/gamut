import sounddevice as sd
import numpy as np
from librosa import load
from soundfile import write
from os.path import splitext

from .config import AUDIO_FORMATS, LOGGER

class AudioBuffer:
    """
    Audio buffer class to read, write, and play back audio files.

    y: np.array
        numpy array of audio samples.

    sr: int | None
        audio sampling rate

    bit_depth: int
        audio bit depth
    """

    def __init__(self, y: np.ndarray | None = None, sr: int | None = None, bit_depth: int = 24) -> None:
        self.y = y
        self.sr = sr
        self.bit_depth = bit_depth

    def play(self) -> None:
        """ Plays back inner audio buffer """
        LOGGER.process('Playing audio...').print()
        sd.play(self.y, samplerate=self.sr, blocking=True)

    def set_sampling_rate(self, sr: int) -> None:
        """ Sampling rate setter method """
        self.sr = sr

    def read(self, input_dir, sr: int | None = None) -> None:
        """ Reads a `.wav` or `.aif` audio file from disk """
        self.y, self.sr = load(input_dir, sr=sr)

    def write(self, output_dir: str) -> None:
        """Writes audio to disk. This function is a simple wrapper of `sf.write()`"""
        ext = splitext(output_dir)[1]
        if ext not in AUDIO_FORMATS:
            raise ValueError(
                f'Output file format must be one of the following: {AUDIO_FORMATS}')
        write(output_dir, self.y, self.sr, f'PCM_{self.bit_depth}')
