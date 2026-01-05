import numpy as np
from scipy.signal import butter, filtfilt
from abc import ABC, abstractmethod
from pyvicar.tools.collections import struct
from itertools import product
import pyvicar.tools.log as log


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


class OutputSetter:
    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def set(self, obj, key, val):
        pass


class StructSetter(OutputSetter):
    def create(self):
        return struct()

    def set(self, obj, key, val):
        setattr(obj, key, val)
        return obj


class DictSetter(OutputSetter):
    def create(self):
        return {}

    def set(self, obj, key, val):
        obj[key] = val
        return obj


def proc_body_one_series(out, body, fromname, toname, tslice, tfilter, do_sum):
    if fromname not in body.keys():
        log.log(f"Draglift Proc: {fromname} not in output dataset, skipped")
        return out

    series = getattr(body, fromname).ravel()[tslice]

    if do_sum:
        sum_key = f"{toname}_sum"
        if sum_key in out:
            out[sum_key] += series
        else:
            out[sum_key] = series

    if tfilter is not None:
        series = tfilter.filt(series)

    out[toname] = series

    return out


def proc_body_series(out, body, prefix, suffix_list, tslice, tfilter, do_sum):
    for suffix in suffix_list:
        key = f"{prefix}{suffix}"
        out = proc_body_one_series(out, body, key, key, tslice, tfilter, do_sum)

    return out


def append_body_series(out, bodyout):
    for key, series in bodyout.items():
        if key.endswith("_sum"):
            out[key] = series
        else:
            if key in out:
                out[key].append(series)
            else:
                out[key] = [series]

    return out


def proc_draglift(
    cdraglift,
    cut=None,
    sum_force=False,
    sum_moment=False,
    sum_power=False,
    sum_area=False,
    filter_cutoff_period=None,
    output=StructSetter(),
):
    if not isinstance(output, OutputSetter):
        raise TypeError(f"Expect an OutputSetter for the output policy argument")

    if not cdraglift:
        raise Exception("Case draglift not read yet. Call c.draglift.read()")

    if cut is None:
        cut = [None, None]
    tstart, tend = cut

    out = output.create()

    time = cdraglift[1].time.ravel()
    tslice = slice_by_t(time, tstart, tend)
    time = time[tslice]
    out = output.set(out, "time", time)

    if filter_cutoff_period is not None:
        tfilter = TFilter.butter(time, cutoff_period=filter_cutoff_period)
    else:
        tfilter = None

    xyzs = ["x", "y", "z"]
    psns = ["p", "s", ""]
    xyzpsn = [f"{xyz}{psn}" for xyz, psn in product(xyzs, psns)]

    # this is processed all series, forces[name][idx] or forces[sum_name]
    forces = {}
    # these are processed series for each body
    force_out = {}
    moment_out = {}
    power_out = {}
    area_out = {}

    for body in cdraglift:
        force_out = proc_body_series(
            force_out, body, "c", xyzpsn, tslice, tfilter, sum_force
        )
        forces = append_body_series(forces, force_out)

        moment_out = proc_body_series(
            moment_out, body, "cm", xyzpsn, tslice, tfilter, sum_moment
        )
        forces = append_body_series(forces, moment_out)

        power_out = proc_body_series(
            power_out, body, "cpw", xyzs + [""], tslice, tfilter, sum_power
        )
        forces = append_body_series(forces, power_out)

        area_out = proc_body_one_series(
            area_out, body, "area", "area", tslice, tfilter, sum_area
        )
        forces = append_body_series(forces, area_out)

    for key, val in forces.items():
        if tfilter is not None and key.endswith("_sum"):
            val = tfilter.filt(val)
        out = output.set(out, key, val)

    return out
