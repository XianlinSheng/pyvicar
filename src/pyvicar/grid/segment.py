import numpy as np
from dataclasses import dataclass


def newton_iter(f, x0, maxiter=50, tol=1e-6):
    x = x0
    for i in range(maxiter):
        fx, dfx = f(x)
        if np.abs(fx) < tol:
            break
        x = x - fx / dfx

    return x


# a0 + a0q + a0q^2 + ... + a0q^{n-1} = a0(1-q^n)/(1-q) = length
def find_n_growth_rate(a0, length, q0):
    # n = log_q(length / a0 * (q-1) + 1)
    N = np.ceil(np.log(length / a0 * (q0 - 1) + 1) / np.log(q0))

    # solve q in (q^N-1)/(q-1) - length/a0 == 0
    def fdf(q):
        fx = (q**N - 1) / (q - 1) - length / a0
        dfx = N * q**N / q / (q - 1) - (q**N - 1) / (q - 1) ** 2

        return fx, dfx

    return int(N), newton_iter(fdf, q0)


@dataclass
class Segment:
    grid: np.array

    @property
    def start(self):
        return self.grid[0]

    @property
    def end(self):
        return self.grid[-1]

    @property
    def startdx(self):
        return self.grid[1] - self.grid[0]

    @property
    def enddx(self):
        return self.grid[-1] - self.grid[-2]

    @property
    def npoint(self):
        return self.grid.shape[0]

    def uniform_dx(start, end, dx):
        return Segment(grid=np.arange(start, end + dx, dx))

    def uniform_N(start, end, N):
        dx = (end - start) / N
        return Segment(grid=np.arange(start, end + dx, dx))

    def grow_toward_left(rterminal, lend, growthrate):
        length = rterminal.start - lend
        a0 = rterminal.startdx

        # N of segment
        N, q = find_n_growth_rate(a0, length, growthrate)

        seg = Segment(np.zeros(N + 1))
        seg.grid[0] = lend
        seg.grid[-1] = rterminal.start
        dx = a0
        # |--+--+--+--|
        # ^           ^
        # lend        rterminal
        # N = 4, set 3(-2) to 1(-4), total 3 points
        for i in range(N - 1):
            seg.grid[-i - 2] = seg.grid[-i - 1] - dx
            dx *= q

        return seg

    def grow_toward_right(lterminal, rend, growthrate):
        length = rend - lterminal.end
        a0 = lterminal.enddx

        # N of segment
        N, q = find_n_growth_rate(a0, length, growthrate)

        seg = Segment(np.zeros(N + 1))
        seg.grid[0] = lterminal.end
        seg.grid[-1] = rend
        dx = a0
        # |--+--+--+--|
        # ^           ^
        # lterminal   rend
        # N = 4, set 1 to 3, total 3 points
        for i in range(N - 1):
            seg.grid[i + 1] = seg.grid[i] + dx
            dx *= q

        return seg

    def lslope(self):
        x = self.grid
        return (-11 * x[0] + 18 * x[1] - 9 * x[2] + 2 * x[3]) / 6

    def rslope(self):
        x = self.grid
        return (11 * x[-1] - 18 * x[-2] + 9 * x[-3] - 2 * x[-4]) / 6

    def smooth(self, lslope=None, rslope=None, iter=5, relax=0.74):
        padded = np.pad(self.grid, 1)
        C = slice(2, -2, None)
        W1 = slice(1, -3, None)
        W2 = slice(None, -4, None)
        E1 = slice(3, -1, None)
        E2 = slice(4, None, None)

        def set_left_d2(x):
            x[0] = (20 * x[1] - 6 * x[2] - 4 * x[3] + x[4]) / 11

        def set_left_d1(x):
            x[0] = (12 * lslope + 10 * x[1] - 18 * x[2] + 6 * x[3] - x[4]) / -3

        if lslope is None:
            set_left = set_left_d2
        else:
            set_left = set_left_d1

        def set_right_d2(x):
            x[-1] = (20 * x[-2] - 6 * x[-3] - 4 * x[-4] + x[-5]) / 11

        def set_right_d1(x):
            x[-1] = (12 * rslope - 10 * x[-2] + 18 * x[-3] - 6 * x[-4] + x[-5]) / 3

        if rslope is None:
            set_right = set_right_d2
        else:
            set_right = set_right_d1

        for _ in range(iter):
            set_left(padded)
            set_right(padded)
            padded[C] = (1 - relax) * padded[C] + relax * (
                4 * (padded[W1] + padded[E1]) - padded[W2] - padded[E2]
            ) / 6

        self.grid[1:-1] = padded[C]
        return self

    def __add__(self, rseg):
        return Segment(np.concatenate((self.grid, rseg.grid[1:])))


def connect_segs(segs):
    arrs = [seg.grid[1:] for seg in segs]
    arrs = [segs[0].start] + arrs
    return Segment(np.concatenate(arrs))
