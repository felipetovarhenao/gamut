from scipy.signal import get_window
from collections.abc import Iterable
from .config import LOGGER, ENVELOPE_TYPES
from .points import Points


class Envelope:
    """
    Envelope class 
    """

    def __init__(self, shape: Iterable | str = "cosine") -> None:
        self.type = None
        self._points = None
        if isinstance(shape, Iterable) and type(shape) != str:
            self.__clean_points(shape)
        elif isinstance(shape, str):
            self.type = shape
        else:
            raise TypeError(LOGGER.error(
                'Envelope must be initialized with either a window type (e.g. "hann") or an iterable of envelope points'))

    def __str__(self):
        return f"<Envelope: {self.type if self.type else str(self._points)}{LOGGER.normal}>"

    def __validate_points(self, points):
        if isinstance(points[0], Iterable):
            prev_idx = points[0][0]
            for point in points[1:]:
                if point[0] <= prev_idx:
                    raise ValueError(LOGGER.error(
                        f'Point indices must be in ascending order: {points}'))
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

    def list_types(self):
        return ENVELOPE_TYPES

    def view(self, grid: bool = True) -> None:
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
    def points(self):
        return self._points

    def get_points(self, N):
        if self.type:
            return Points(get_window(self.type, N))
        return self._points.resample(N)
