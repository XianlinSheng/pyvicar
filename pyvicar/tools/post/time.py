import numpy as np


def slice_by_t(x, x1, x2):
    if x1 is None:
        i1 = None
    else:
        for i, val in enumerate(x):
            if val >= x1:
                i1 = i
                break

    if x2 is None:
        i2 = None
    else:
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
