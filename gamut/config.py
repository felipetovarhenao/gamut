from __future__ import annotations
from time import time
from .sys import Console
from typing import Any, Callable

FILE_EXT = '.gamut'
AUDIO_FORMATS = ['.wav', '.aif', '.aiff', '.mp3']
MIME_TYPES = ['audio/x-wav', 'audio/x-aiff', 'audio/mpeg']
CONSOLE = Console()
ANALYSIS_TYPES = ['timbre', 'pitch']
ENVELOPE_TYPES = [
    'barthann',
    'bartlett',
    'blackman',
    'blackmanharris',
    'bohman',
    'boxcar',
    'chebwin',
    'cosine',
    'dpss',
    'exponential',
    'flattop',
    'gaussian',
    'general_cosine',
    'general_gaussian'
    'general_hamming'
    'hamming'
    'hann'
    'kaiser_bessel_derived'
    'lanczos'
    'nuttall',
    'parzen',
    'taylor',
    'triang',
    'tukey',
]


def get_elapsed_time(func: Callable) -> Callable:
    """ Decorator to log how long a given function takes to run """
    def decorator(*args, **kwargs) -> Any:
        st = time()
        output = func(*args, **kwargs)
        CONSOLE.elapsed_time(st).print()
        return output
    return decorator
