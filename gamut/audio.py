import numpy as np
import sounddevice as sd
from os.path import splitext
from .config import AUDIO_FORMATS, LOGGER
from soundfile import write
from librosa import load


class AudioBuffer:
    """
    Audio Buffer class
    """

    def __init__(self, y: np.ndarray | None = None, sr: int | None = None) -> None:
        self.y = y
        self.sr = sr

    def play(self) -> None:
        LOGGER.process('Playing audio...').print()
        sd.play(self.y, samplerate=self.sr, blocking=True)

    def set_sampling_rate(self, sr: int) -> None:
        self.sr = sr

    def read(self, input_dir, sr: int | None = None) -> None:
        self.y, self.sr = load(input_dir, sr=sr)

    def write(self, output_dir: str, bit_depth: int = 24):
        """Writes an `ndarray` as audio. This function is a simple wrapper of `sf.write()`"""
        ext = splitext(output_dir)[1]
        if ext not in AUDIO_FORMATS:
            raise ValueError(
                f'Output file format must be one of the following: {AUDIO_FORMATS}')
        write(output_dir, self.y, self.sr, 'PCM_{}'.format(bit_depth))
