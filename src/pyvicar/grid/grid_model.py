import numpy as np
from dataclasses import dataclass
from collections.abc import Iterable


# listlist
def fill_ll_broadcast(ll, ndim):
    if not isinstance(ll, Iterable):
        ll = [[ll] * 2] * ndim

    ll = [l1[:2] if isinstance(l1, Iterable) else [l1] * 2 for l1 in ll]

    ll = ll[:ndim]

    return ll


def fill_ll_default(ll, d):
    if ll is None:
        return d

    return [list(d1) if l1 is None else l1 for l1, d1 in zip(ll, d)]


@dataclass
class GridModel:
    dim2: bool
    ndim: int
    l0: np.ndarray
    doml: np.ndarray
    refl: np.ndarray
    grow: np.ndarray

    @classmethod
    def create_default(cls, len_scales, dim2=False):
        ndim = 2 if dim2 else 3

        len_scales = fill_ll_broadcast(len_scales, ndim)

        domlx = [[20, 10]]
        domly = [[20, 20]]
        reflx = [[2, 7]]
        refly = [[2, 2]]
        growx = [[1.05, 1.01]]
        growy = [[1.05, 1.05]]

        domls = domlx + domly
        refls = reflx + refly
        grows = growx + growy
        if not dim2:
            domls += domly
            refls += refly
            grows += growy

        return cls(
            dim2,
            ndim,
            np.array(len_scales, dtype=float),
            np.array(domls, dtype=float),
            np.array(refls, dtype=float),
            np.array(grows, dtype=float),
        )

    def copy(self):
        return GridModel(
            self.dim2,
            self.ndim,
            self.l0.copy(),
            self.doml.copy(),
            self.refl.copy(),
            self.grow.copy(),
        )

    def center(self):
        xyz = self.l0[:, 0] * self.doml[:, 0]
        if self.dim2:
            xyz = xyz[:2]
        return xyz
