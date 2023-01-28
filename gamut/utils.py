import numpy as np
from time import time


def inspect_object(obj, path: str | None, separator: str = "."):
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


def __deep_update(obj, paths, replace):
    if not paths:
        obj = replace
        return obj
    k = paths[0]
    if isinstance(obj, list):
        obj[int(k)] = __deep_update(obj[int(k)], paths[1:], replace)
    elif isinstance(obj, dict):
        obj[k] = __deep_update(obj[k], paths[1:], replace)
    else:
        setattr(obj, k, __deep_update(getattr(obj, k), paths[1:], replace))
    return obj


def deep_update(obj, path, replace, separator: str = '.'):
    return __deep_update(obj, path.split(separator), replace)


def resample_array(array, N):
    return np.interp(np.linspace(0, len(array) - 1, N), np.arange(0, len(array)), array)


class Logger:
    """ utility class for logging colored messages"""

    class Log(str):

        def print(self):
            print(self)

    def __init__(self) -> None:
        def f(c): return u'\u001b[38;5;' + f'{c}m'

        self.normal = '\033[0m' + f(153)
        self.bold = '\033[1m'
        self.italic = '\033[3m'

        self.c1 = f(39)
        self.c2 = f(75)
        self.c3 = f(111)
        self.c4 = f(213)
        self.c5 = f(196)

        self.err = f(160)

    def elapsed_time(self, st):
        return self.Log(f'\t{self.c3}{self.italic}Elapsed time: {self.bold}{self.c5}{round((time()-st) * 100) / 100}s{self.normal}\n')

    def process(self, text):
        return self.Log(f'{self.bold}{self.c2}{text}{self.normal}')

    def disk(self, object_name, filename, read=False):
        return self.process(f'{"Reading" if read else "Writing"} {self.c4}{object_name.upper()}{self.c2} {"from" if read else "to"} disk: {self.c4}{self.bold}{filename}{self.c2}...{self.normal} ')

    def subprocess(self, text):
        return self.Log(f'\t{self.c1}{text}{self.normal}')

    def error(self, text):
        return self.Log(f'\n\t{self.err}{self.bold}{text}{self.normal}\n')
