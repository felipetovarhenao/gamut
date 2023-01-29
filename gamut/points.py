import numpy as np


class Points(np.ndarray):
    """ Points class """

    def __array_finalize__(self, obj):
        return obj

    def __new__(cls, array: np.ndarray | list = []):
        return np.asarray(array).view(cls)

    def fill(self, shape, value):
        tmp = np.empty(shape=shape)
        tmp.fill(value)
        return Points(tmp)

    def concat(self, x):
        return Points(np.concatenate([self, x]))

    def resample(self, N):
        if len(self) == N:
            return self
        return Points(np.interp(np.linspace(0, len(self) - 1, N), np.arange(0, len(self)), self))

    def scale(self, out_min: float | int = 0.0, out_max: float | int = 1.0):
        amin, amax = np.amin(self), np.amax(self)
        return Points(((self - amin) / (amax - amin)) * (out_max - out_min) + out_min)

    def replicate(self, n, axis: int = 0):
        return Points(np.repeat(self, repeats=n, axis=axis))

    def wrap(self, n: int = 1):
        out = self
        for _ in range(n):
            out = Points([out])
        return out

    def quantize(self, n):
        return Points(np.round(self / n) * n)

    def perturb(self, jitter, uniform: bool = True):
        if jitter == 0:
            return self
        return self + Points(np.random.rand(*((self.shape[0], 1) if uniform else self.shape))).scale(-jitter, jitter)

    def abs(self):
        return Points(np.abs(self))
