import sounddevice as sd
import numpy as np
from librosa import load
from soundfile import write
from os.path import splitext
from scipy import signal
from typing_extensions import Self
from collections.abc import Iterable

from .config import AUDIO_FORMATS, CONSOLE
from .utils import resample_array
from .controls import Envelope
from .controls import Points


class AudioBuffer:
    """
    Audio buffer class to read, write, and play back audio files.

    y: np.array
        numpy array of audio samples.

    sr: int | None
        audio sampling rate.

    bit_depth: int
        audio bit depth.
    """

    def __init__(self, y: np.ndarray | None = None, sr: int | None = None, bit_depth: int = 24) -> None:
        self.y = y
        self.sr = sr
        self.bit_depth = bit_depth

    def play(self) -> None:
        """ Plays back inner audio buffer """
        CONSOLE.log_process('\N{speaker}Playing audio...').print()
        try:
            sd.play(self.y, samplerate=self.sr, blocking=True)
        except sd.PortAudioError:
            CONSOLE.error(
                sd.PortAudioError,
                f'Unable to play audio stream. It\'s possible the number of output channels in the audio source ({self.chans}) is greater than what your device supports.')

    def set_sampling_rate(self, sr: int) -> None:
        """ Sampling rate setter method """
        if self.sr != sr:
            self.y = resample_array(self.y, int(round(len(self.y) * sr/self.sr)))
        self.sr = sr

    def read(self, input_dimpulse_response, sr: int | None = None, mono: bool = False) -> None:
        """ Reads a ``.wav`` or ``.aif`` audio file from disk """
        self.y, self.sr = load(input_dimpulse_response, sr=sr, mono=mono)
        self.y = self.y.T if len(self.y.shape) > 1 else self.y[:, np.newaxis]
        return self

    @property
    def chans(self):
        return self.y.shape[1]

    @property
    def samps(self):
        return self.y.shape[0]

    def write(self, output_dimpulse_response: str) -> None:
        """Writes audio to disk. This function is a simple wrapper of `sf.write()`"""
        ext = splitext(output_dimpulse_response)[1]
        if ext not in AUDIO_FORMATS:
            CONSOLE.error(ValueError, f'Output file format must be one of the following: {AUDIO_FORMATS}')
        write(output_dimpulse_response, self.y, self.sr, f'PCM_{self.bit_depth}')

    def to_mono(self):
        """ Converts audio channels to mono """
        if self.chans == 1:
            return
        self.y = (self.y.sum(axis=1)[: np.newaxis] / self.chans).reshape((self.samps, 1))

    def convolve(self, impulse_response: Self | str, mix: int | float | Iterable | Envelope = 0.125, normalize: bool = True):
        """ Applies impulse response convolution to audio """
        def parse_mix_param(mix, N):
            if isinstance(mix, Envelope):
                mix_param = mix.get_points(N)
            elif isinstance(mix, Iterable):
                mix_param = Envelope(mix).get_points(N)
            else:
                mix_param = Points().fill(N, mix)
            return mix_param[:, np.newaxis]

        y_samps = self.samps

        # prepare impulse response and generate convolved signal
        ir = impulse_response if isinstance(impulse_response, AudioBuffer) else AudioBuffer().read(impulse_response, mono=True)
        ir.to_mono()
        y_wet = signal.convolve(in1=self.y, in2=ir.y, method='auto')

        # reshape to match convolved signal
        y_dry = np.zeros(shape=y_wet.shape)
        y_dry[:self.samps] = self.y
        self.y = y_dry

        # normalize
        if normalize:
            y_wet = (y_wet / np.max(np.abs(y_wet))) * np.sqrt(0.5)

        # parse wet/dry mix control parameter
        mix_param = np.zeros(shape=(y_wet.shape[0], 1))
        tmp = parse_mix_param(mix, y_samps)
        mix_param[:y_samps] = tmp
        mix_param[y_samps:] = tmp[-1]

        # mix both signals
        self.y = y_dry * (1 - mix_param) + y_wet * mix_param
