from __future__ import annotations
import numpy as np
from time import time
from .utils import resample_array
from progress import bar, counter, Infinite
from typing_extensions import Any


def set_vebosity(verbose: bool) -> None:
    """ Set verbosity of Console class"""
    Console.set_verbose(verbose)


class Console:
    """
    Utility class for logging ANSI-colored text in the console.
    """

    VERBOSE = True
    CALLED = False

    class Log(str):
        """ Dummy subclass of str to include print as method """
        VERBOSE = True

        @classmethod
        def set_verbose(cls, verbose):
            cls.VERBOSE = verbose

        def print(self) -> None:
            if not self.VERBOSE:
                return
            print(self)

    class ProgressMixin(Infinite):
        VERBOSE = True

        def reset(self, message: str) -> None:
            self.index = 0
            self.message = f'{message} '

        def next(self, *args, **kwargs):
            if not self.VERBOSE:
                return
            return super().next(*args, **kwargs)

        def finish(self):
            if not self.VERBOSE:
                return
            return super().finish()

        @classmethod
        def set_verbose(cls, verbose):
            cls.VERBOSE = verbose

    class Counter(counter.Counter, ProgressMixin):
        ...

    class Bar(bar.IncrementalBar, ProgressMixin):
        def reset(self, message: str, max: int | float, item: str = "") -> None:
            self.max = max
            self.suffix = '%(index)d/%(max)d ' + item
            super().reset(message)

    def __init__(self) -> None:
        self.reset = '\033[0m' + Console.rgb(231, 251, 255)
        self.bold = '\033[1m'
        self.italic = '\033[3m'

        self.bar = Console.Bar()
        self.counter = Console.Counter()

        # assign colors to instance as attributes
        for i, c in enumerate([
            (61, 187, 255),  # c1: blue
            (102, 255, 150),  # c2: green
            (126, 229, 252),  # c3: light blue
            (255, 216, 125),  # c4: yellow
            (255, 107, 66),  # c5: red
        ], 1):
            setattr(self, f'c{i}', Console.rgb(*c))

        self.danger = Console.rgb(255, 71, 77)  # red

    def __getattribute__(self, __name: str) -> Any:
        if not Console.CALLED and Console.VERBOSE:
            Console.CALLED = True
            Console.print_header()
        return object.__getattribute__(self, __name)

    @classmethod
    def set_verbose(cls, verbose: bool) -> None:
        cls.VERBOSE = verbose
        cls.Log.set_verbose(verbose)
        cls.Counter.set_verbose(verbose)
        cls.Bar.set_verbose(verbose)

    def log(self, text: str) -> Log:
        return self.Log(f'{text}{self.reset}')

    def reset_bar(self, message: str, max: int | float, item: str) -> None:
        self.bar.reset(self.log_subprocess(message), max, item)

    def reset_counter(self, message: str) -> None:
        self.counter.reset(self.log_subprocess(message))

    def elapsed_time(self, st: float | int) -> Log:
        return self.log(
            f'\t\N{stopwatch} {self.c4}{self.italic}Elapsed time: {self.bold}{self.c5}{round((time()-st) * 100) / 100}s\n')

    def log_process(self, text: str) -> Log:
        return self.log(f'{self.bold}{self.c1}{text}')

    def log_disk_op(self, object_name: str, filename: str, read: bool = False) -> Log:
        return self.log_process(
            f'\N{floppy disk} {"Reading" if read else "Writing"} {self.c2}{object_name.upper()}{self.c1} {"from" if read else "to"} disk: {self.c2}{self.bold}{filename}{self.c1}...')

    def log_subprocess(self, text: str) -> Log:
        return self.log(f'\t{self.c3}{text}')

    def error(self, error_class: Exception, text: str) -> None:
        raise error_class(self.log(f'\n\t\N{skull} {self.danger}{text}\n'))

    def warn(self, text: str) -> None:
        print(f"\n\N{cross mark} {self.danger}Warning: {text}\n")

    @staticmethod
    def rgb(r, g, b):
        return f'\u001b[38;2;{r};{g};{b}m'

    @classmethod
    def print_header(cls):
        spectrum = np.array([
            (246, 90, 62),
            (249, 164, 69),
            (240, 232, 72),
            (130, 230, 96),
            (52, 202, 197),
            (141, 126, 179),
            (246, 90, 62),
        ])

        gamut = "~ GAMuT: Granular Audio Musaicing Toolkit ~"
        spectrum = [cls.rgb(*col) for col in np.array([resample_array(val, len(gamut))
                                                       for val in spectrum.T]).T.astype('int32')]

        print("".join([f'{col}\033[1m{char}' for char, col in zip(gamut, spectrum)]) + "\n")
