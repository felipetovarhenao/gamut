from __future__ import annotations
from scipy.signal import get_window
from collections.abc import Iterable
import numpy as np

from .config import CONSOLE, ENVELOPE_TYPES
from math import ceil
from typing_extensions import Self


class Points(np.ndarray):
    """ 
    A subclass of a numpy array, mostly to allow inline method concatenation — e.g. x.a().b().c()
    """

    def __array_finalize__(self, obj) -> Self:
        return obj

    def __new__(cls, array: np.ndarray | list = []) -> Self:
        return np.asarray(array).view(cls)

    def fill(self, shape: Iterable, value: int | float) -> Self:
        tmp = np.empty(shape=shape)
        tmp.fill(value)
        return Points(tmp)

    def concat(self, x: Points | np.ndarray, prepend: bool = False) -> Points:
        return Points(np.concatenate([x, self] if prepend else [self, x]))

    def resample(self, N: int) -> Points:
        if len(self) == N:
            return self
        return Points(np.interp(np.linspace(0, len(self) - 1, N), np.arange(0, len(self)), self))

    def scale(self, out_min: float | int = 0.0, out_max: float | int = 1.0) -> Points:
        amin, amax = np.amin(self), np.amax(self)
        return Points(((self - amin) / (amax - amin)) * (out_max - out_min) + out_min)

    def replicate(self, n: int, axis: int = 0) -> Points:
        return Points(np.repeat(self, repeats=n, axis=axis))

    def wrap(self, n: int = 1) -> Self:
        out = self
        for _ in range(n):
            out = Points([out])
        return out

    def quantize(self, n: float | int = 1) -> Self:
        return Points(np.round(self / n) * n)

    def abs(self) -> Self:
        return Points(np.abs(self))

    def clip(self, min: float | int | None = None, max: float | int | None = None) -> Self:
        if min:
            self[self < min] = min
        if max:
            self[self > max] = max
        return self


class Envelope:
    """
    ``Envelope`` instances are meant to be used as dynamic audio control parameters, when calling the ``Mosaic.to_audio()`` method.
    For instance, to temporally change audio parameters such as grain duration, panning, playback speed, etc.
    """

    def __init__(self, shape: Iterable | str = "cosine") -> None:
        self.type = None
        self._points = None
        if isinstance(shape, Iterable) and type(shape) != str:
            self.__clean_points(shape)
        elif isinstance(shape, str):
            self.type = shape
        else:
            CONSOLE.error(
                TypeError,
                'Envelope must be initialized with either a window type (e.g. "hann") or an iterable of envelope points')

    def __str__(self) -> str:
        return f"<{self.__class__.__name__.capitalize()}: {self.type if self.type else str(self._points)}>"

    def __validate_points(self, points: Iterable) -> Points:
        if isinstance(points[0], Iterable):
            prev_idx = points[0][0]
            for point in points[1:]:
                if point[0] <= prev_idx:
                    CONSOLE.error(ValueError, f'Point indices must be in ascending order: {points}')
                prev_idx = point[0]
            return Points(points)
        return Points(list(enumerate(points)))

    def __clean_points(self, points: Iterable) -> None:
        pts = self.__validate_points(points)
        y = Points()
        for i in range(len(pts) - 1):
            segment = pts[i:i+2, 1]
            size = int(pts[i+1, 0] - pts[i, 0] + 1)
            y = y.concat(segment.resample(size)[:-1])
        self._points = y.concat([pts[-1][1]])

    def print_shape_choices(self) -> None:
        """ Prints all supported envelope shape types """
        print(f'shape choices: {ENVELOPE_TYPES}')

    def view(self, grid: bool = True) -> None:
        """ Helper method to visualize the shape of the envelope """
        import matplotlib.pyplot as plt
        y = get_window(self.type, Nx=64) if self.type else self._points
        plt.plot(y)
        plt.title(f"Envelope{f' ({self.type})' if self.type else ''}")
        plt.xlabel('time')
        plt.ylabel('control value')
        if self.type:
            plt.xticks([])
        if grid:
            plt.grid()
        plt.show()

    @property
    def points(self) -> Points:
        return self._points

    def get_points(self, N: int) -> Points:
        if self.type:
            return Points(get_window(self.type, N))
        return self._points.resample(N)


def object_to_points(param, N: int) -> Points:
    """ resolve parameter into a ``Points`` instance based on type """
    if isinstance(param, Envelope):
        return param.get_points(N)
    elif isinstance(param, Iterable):
        return Envelope(shape=param).get_points(N)
    else:
        return Points().fill(N, param)


def plot_envelope_list(env_list: Iterable, rows: int = 1) -> None:
    from matplotlib import pyplot as plt

    envs = np.array([object_to_points(x, 100) for x in env_list]).T
    cumsum = envs.sum(axis=1)[:, np.newaxis]
    envs = (envs / cumsum).T
    plt.figure(1)

    for i in range(len(env_list)):
        plt.subplot(int(f'{rows}{max(1, ceil(len(env_list)/rows))}{i+1}'),
                    ylim=[0, 1],
                    xlabel='time',
                    ylabel='value',
                    xticks=[],
                    yticks=np.round(np.linspace(0, 1, 10), 1),
                    title=f'Envelope {i + 1}'
                    )
        plt.plot(envs[i], color=['dodgerblue', 'tomato', 'coral', 'salmon'][i % 4],)
    plt.tight_layout()
    plt.show()
