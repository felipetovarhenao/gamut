from .sys import Console

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
