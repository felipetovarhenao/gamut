from __future__ import annotations
import sounddevice as sd
import numpy as np
from librosa import load
from soundfile import write
from os.path import splitext, basename
from scipy import signal
from typing_extensions import Self
from collections.abc import Iterable

from .config import AUDIO_FORMATS, CONSOLE, get_elapsed_time
from .utils import resample_array
from .controls import Envelope
from .controls import Points
from . import catch_keyboard_interrupt


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

    @catch_keyboard_interrupt(lambda: CONSOLE.log_process("\N{speaker with cancellation stroke} Audio stopped").print())
    def play(self, blocking: bool = True) -> None:
        """ Plays back inner audio buffer """
        CONSOLE.log_process('\N{speaker}Playing audio...').print()
        try:
            sd.play(self.y, samplerate=self.sr, blocking=blocking)
        except sd.PortAudioError:
            CONSOLE.error(
                sd.PortAudioError,
                f'Unable to play audio stream. It\'s possible the number of output channels in the audio source ({self.chans}) is greater than what your device supports.')

    def stop(self) -> None:
        """ Stops audio buffer when using ``blocking=True`` in play method """
        sd.stop()

    def set_sampling_rate(self, sr: int) -> None:
        """ Sampling rate setter method """
        if self.sr != sr:
            self.y = resample_array(self.y, int(round(len(self.y) * sr/self.sr)))
        self.sr = sr

    def read(self, input_dir: str, sr: int | None = None, mono: bool = False) -> Self:
        """ Reads a ``.wav`` or ``.aif`` audio file from disk """
        self.y, self.sr = load(input_dir, sr=sr, mono=mono)
        self.y = self.y.T if len(self.y.shape) > 1 else self.y[:, np.newaxis]
        return self

    @property
    def chans(self) -> int:
        return self.y.shape[1]

    @property
    def samps(self) -> int:
        return self.y.shape[0]

    @get_elapsed_time
    def write(self, output_dir: str) -> None:
        """Writes audio to disk. This function is a simple wrapper of `sf.write()`"""
        ext = splitext(output_dir)[1]
        if ext not in AUDIO_FORMATS:
            CONSOLE.error(ValueError, f'Output file format must be one of the following: {AUDIO_FORMATS}')
        CONSOLE.log_disk_op('audio file', basename(output_dir)).print()
        write(output_dir, self.y, self.sr, f'PCM_{self.bit_depth}')

    def to_mono(self) -> None:
        """ Converts audio channels to mono """
        if self.chans == 1:
            return
        self.y = (self.y.sum(axis=1)[: np.newaxis] / self.chans).reshape((self.samps, 1))

    def convolve(self, impulse_response: Self | str, mix: int | float | Iterable | Envelope = 0.125, normalize: bool = True) -> None:
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
