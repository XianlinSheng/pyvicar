import numpy as np
from dataclasses import dataclass


@dataclass
class Fourier:
    n: int
    ab: np.ndarray
    c: float

    # phase=0 => min val, phase=pi => max val
    # make_sine_minmax(-1, 1, 0) => -cos(phase)
    # make_sine_minmax(-1, 1, pi) => -cos(phase+pi) = cos(phase)
    # make_sine_minmax(-1, 1, pi/2) => -cos(phase+pi/2) = sin(phase)
    @classmethod
    def make_sine_minmax(cls, minv, maxv, phase0):
        c = (minv + maxv) / 2
        amp = (maxv - minv) / 2
        a = -amp * np.cos(phase0)
        b = amp * np.sin(phase0)
        return cls(1, np.array([[a], [b]]), c)

    @classmethod
    def make_constant(cls, c):
        return cls(1, np.array([[0], [0]]), c)

    def minmax(self, resolution=200):
        N = resolution

        a = np.asarray(self.ab[0, :])
        b = np.asarray(self.ab[1, :])

        x = np.linspace(0, 2 * np.pi, N, endpoint=False)

        n = np.arange(1, self.n + 1)

        cos_part = a[:, None] * np.cos(n[:, None] * x[None, :])
        sin_part = b[:, None] * np.sin(n[:, None] * x[None, :])

        f = self.c + np.sum(cos_part + sin_part, axis=0)

        return f.min(), f.max()

    def __mul__(self, k):
        return Fourier(self.n, self.ab * k, self.c * k)

    def __add__(self, k):
        return Fourier(self.n, self.ab, self.c + k)
