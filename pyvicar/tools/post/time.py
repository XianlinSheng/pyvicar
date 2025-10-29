import numpy as np
from scipy.signal import butter, filtfilt
from abc import ABC, abstractmethod


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


class TFilter(ABC):
    @abstractmethod
    def filt(self, ft):
        return filtfilt(self._b, self._a, ft)

    def butter(time, cutoff_period, order=4):
        order = 4
        cutoff_freq = 1 / cutoff_period
        fs = (time.shape[0] - 1) / (time[-1] - time[0])
        nyq = fs / 2
        b, a = butter(order, cutoff_freq / nyq, btype="low")
        return TFilterBA(b, a)


class TFilterNone(TFilter):
    def filt(self, ft):
        return ft


class TFilterBA(TFilter):
    def __init__(self, b, a):
        self._b = b
        self._a = a

    def filt(self, ft):
        return filtfilt(self._b, self._a, ft)


def tfilter_mean(ft, window_size=5, mode="same"):
    if window_size < 0:
        raise ValueError(f"filter window size cannot < 0, encountered {window_size}")
    if window_size == 0:
        return ft
    kernel = np.ones(window_size) / window_size
    return np.convolve(ft, kernel, mode=mode)
