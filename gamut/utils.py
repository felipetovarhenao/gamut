import numpy as np
from time import time
from typing import Any


def get_nested_value(obj: object, path: str | None, separator: str = ".") -> Any:
    """
    Helper function to get an a nested value from an ``object`` of aribirary depth

    obj: object
        Object to extract value from.

    path: str | None
        path to traverse ``obj``, separated by ``separator``.

    separator: str
        substring by which to parse ``path``
    """
    output = obj
    for key in path.split(separator):
        t = type(output)
        if t == list:
            output = output[int(key)]
        elif t == dict:
            output = output[key]
        else:
            output = getattr(output, key)
    return output


def __set_nested_value(obj, paths, replace):
    if not paths:
        obj = replace
        return obj
    k = paths[0]
    if isinstance(obj, list) or isinstance(obj, np.ndarray):
        obj[int(k)] = __set_nested_value(obj[int(k)], paths[1:], replace)
    elif isinstance(obj, dict):
        obj[k] = __set_nested_value(obj[k], paths[1:], replace)
    else:
        setattr(obj, k, __set_nested_value(getattr(obj, k), paths[1:], replace))
    return obj


def set_nested_value(obj, path, replace, separator: str = '.') -> Any:
    """
    Helper function to update an a nested value from an ``object`` of aribirary depth

    obj: object
        Object to extract value from.

    replace:

    path: str | None
        path to traverse ``obj``, separated by ``separator``.

    separator: str
        substring by which to parse ``path``
    """
    return __set_nested_value(obj, path.split(separator), replace)


def resample_array(array, N):
    return np.interp(np.linspace(0, len(array) - 1, N), np.arange(0, len(array)), array)


class Logger:
    """ 
    Utility class for logging ANSI-colored text in the console.
    """

    class Log(str):
        def print(self):
            print(self)

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

        self.reset = 'u\u001b[0m'

        self.normal = '\033[0m' + rgb(231, 251, 255)
        self.bold = '\033[1m'
        self.italic = '\033[3m'

        # assign colors to instance as attributes
        for i, c in enumerate([
            (61, 187, 255),  # c1: blue
            (102, 255, 150),  # c2: green
            (126, 229, 252),  # c3: light blue
            (255, 216, 125),  # c4: yellow
            (255, 107, 66),  # c5: red
        ], 1):
            setattr(self, f'c{i}', rgb(*c))

        self.err = rgb(255, 71, 77)  # red
        self.header().print()

    def elapsed_time(self, st):
        return self.Log(
            f'\t{self.c4}{self.italic}Elapsed time: {self.bold}{self.c5}{round((time()-st) * 100) / 100}s{self.normal}\n')

    def process(self, text):
        return self.Log(f'{self.bold}{self.c1}{text}{self.normal}')

    def disk(self, object_name, filename, read=False):
        return self.process(
            f'{"Reading" if read else "Writing"} {self.c2}{object_name.upper()}{self.c1} {"from" if read else "to"} disk: {self.c2}{self.bold}{filename}{self.c1}...{self.normal} ')

    def subprocess(self, text):
        return self.Log(f'\t{self.c3}{text}{self.normal}')

    def error(self, text):
        return self.Log(f'\n\t{self.err}{self.bold}{text}{self.normal}\n')

    def header(self):
        header = ""
        for char, col in zip(self.gamut, self.spectrum):
            header += f'{col}{self.bold}{char}'
        return self.Log(f'{header}{self.normal}\n')
