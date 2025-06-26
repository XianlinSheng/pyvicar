import numpy as np


def slice_by_t(x, x1, x2):
    i1 = None

    if not x1 is None:
        for i, val in enumerate(x):
            if val >= x1:
                i1 = i
                break

    i2 = None
    if not x2 is None:
        for i, val in enumerate(x):
            if val >= x2:
                i2 = i
                break

    return slice(i1, i2, None)


# f(t) series and dt -> amp(freq), freq
def tfourier(ft, dt, mag=True):
    if len(ft.shape) != 1:
        raise ValueError(
            f"Expect input f(t) series as a 1D array, but encountered {ft.shape}"
        )
    N = ft.shape[0]

    amps = np.fft.rfft(ft) / N
    if mag:
        amps = np.abs(amps)

    freqs = np.fft.rfftfreq(N, d=dt)

    return amps, freqs


def tfilter(ft, window_size=5, mode="same"):
    if window_size < 0:
        raise ValueError(f"filter window size cannot < 0, encountered {window_size}")
    if window_size == 0:
        return ft
    kernel = np.ones(window_size) / window_size
    return np.convolve(ft, kernel, mode=mode)
