from __future__ import annotations
import numpy as np
from time import time
from .utils import resample_array
from progress import bar, counter


class Console:
    """ 
    Utility class for logging ANSI-colored text in the console.
    """

    class Log(str):
        """ Dummy subclass of str to include print as method """

        def print(self) -> None:
            print(self)

    class ProgressMixin(object):
        def reset(self, message: str) -> None:
            self.index = 0
            self.message = f'{message} '

    class Counter(counter.Counter, ProgressMixin):
        ...

    class Bar(bar.IncrementalBar, ProgressMixin):
        def reset(self, message: str, max: int | float, item: str = "") -> None:
            self.max = max
            self.suffix = '%(index)d/%(max)d ' + item
            super().reset(message)

    def __init__(self) -> None:
        def rgb(r, g, b): return f'\u001b[38;2;{r};{g};{b}m'

        spectrum = np.array([
            (246, 90, 62),
            (249, 164, 69),
            (240, 232, 72),
            (130, 230, 96),
            (52, 202, 197),
            (141, 126, 179),
            (246, 90, 62),
        ])

        self.gamut = "~ GAMuT: Granular Audio Musaicing Toolkit ~"
        self.spectrum = [rgb(*col) for col in np.array([resample_array(val, len(self.gamut))
                                                        for val in spectrum.T]).T.astype('int32')]

        self.reset = '\033[0m' + rgb(231, 251, 255)
        self.bold = '\033[1m'
        self.italic = '\033[3m'

        self.bar = self.Bar()
        self.counter = self.Counter()

        # assign colors to instance as attributes
        for i, c in enumerate([
            (61, 187, 255),  # c1: blue
            (102, 255, 150),  # c2: green
            (126, 229, 252),  # c3: light blue
            (255, 216, 125),  # c4: yellow
            (255, 107, 66),  # c5: red
        ], 1):
            setattr(self, f'c{i}', rgb(*c))

        self.danger = rgb(255, 71, 77)  # red
        self.log_header().print()

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

    def log_header(self) -> Log:
        header = ""
        for char, col in zip(self.gamut, self.spectrum):
            header += f'{col}{self.bold}{char}'
        return self.log(f'{header}\n')
