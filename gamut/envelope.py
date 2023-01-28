import numpy as np
from scipy.signal import get_window
from collections.abc import Iterable
from .config import LOGGER, ENVELOPE_TYPES
import matplotlib.pyplot as plt


class Points:

    def __init__(self, array: np.ndarray = np.array([])) -> None:
        self._array = array

    def concat(self, item):
        self._array = np.concatenate([self._array, item])
        return self

    def resample(self, N):
        if len(self._array) != N:
            self._array = np.interp(np.linspace(
                0, len(self._array) - 1, N), np.arange(0, len(self._array)), self._array)
        return self

    def cumsum(self, *args, **kwargs):
        self._array = self.array.cumsum(*args, **kwargs)
        return self

    def astype(self, *args, **kwargs):
        self._array = self._array.astype(*args, **kwargs)
        return self

    def quantize(self, res):
        self._array = np.round(self._array * res) / res
        return self

    def T(self):
        self._array = self._array.T
        return self

    def expand(self, times):
        self._array = np.repeat(np.array([self._array]).T, times, axis=1)
        return self

    def normalize(self):
        amin, amax = np.amin(self._array), np.amax(self._array)
        norm = amax - amin
        self._array = (self._array - amin) / norm
        return self

    @property
    def array(self):
        return self._array


class Envelope:
    """
    Envelope class 
    """

    def __init__(self, y: Iterable | str = "cosine") -> None:
        self.type = None
        self.points = None
        if isinstance(y, Iterable) and type(y) != str:
            self.__clean_points(y)
        elif isinstance(y, str):
            self.type = y
        else:
            raise TypeError(LOGGER.error(
                'Envelope must be initialized with either a window type (e.g. "hann") or an iterable of envelope points'))

    def __str__(self):
        return f"<Envelope: {self.type if self.type else str(self.points)}{LOGGER.normal}>"

    def __validate_points(self, points):
        if isinstance(points[0], Iterable):
            prev_idx = points[0][0]
            for point in points[1:]:
                if point[0] <= prev_idx:
                    raise ValueError(LOGGER.error(
                        f'Point indices must be in ascending order: {points}'))
                prev_idx = point[0]
            return np.array(points)
        return np.array(list(enumerate(points)))

    def __clean_points(self, points: Iterable) -> None:
        pts = self.__validate_points(points)
        y = np.array([])
        for i in range(len(pts) - 1):
            segment = pts[i:i+2, 1]
            size = int(pts[i+1, 0] - pts[i, 0] + 1)
            tmp = Envelope.__resample_array(segment, size)[:-1]
            y = np.concatenate([y, tmp])
        self.points = np.concatenate([y, [pts[-1][1]]])

    def list_types(self):
        return ENVELOPE_TYPES

    @classmethod
    def __resample_array(cls, y, N: int):
        if len(y) == N:
            return y
        return np.interp(np.linspace(0, len(y) - 1, N), np.arange(0, len(y)), y)

    def view(self, grid: bool = True) -> None:
        y = get_window(self.type, Nx=64) if self.type else self.points
        plt.plot(y)
        plt.title(f"Envelope{f' ({self.type})' if self.type else ''}")
        plt.xlabel('time')
        plt.ylabel('control value')
        if self.type:
            plt.xticks([])
        if grid:
            plt.grid()
        plt.show()
