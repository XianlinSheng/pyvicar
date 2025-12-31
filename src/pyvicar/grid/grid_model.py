import numpy as np
from dataclasses import dataclass
from collections.abc import Iterable


# listlist
def fill_ll_broadcast(ll, shape):

    if len(shape) == 0:
        return ll

    if isinstance(ll, Iterable):
        ll = ll[: shape[0]]
    else:
        ll = [ll] * shape[0]

    return [fill_ll_broadcast(l1, shape[1:]) for l1 in ll]


# d (default) should be broadcasted already
def fill_ll_default(ll, d):
    if ll is None:
        return d

    if not isinstance(ll, Iterable):
        return ll

    return [fill_ll_default(l1, d1) for l1, d1 in zip(ll, d)]


@dataclass
class GridModel:
    dim2: bool
    ndim: int
    l0: np.ndarray
    doml: np.ndarray
    refl: np.ndarray
    grow: np.ndarray

    @classmethod
    def create(cls, l0=None, doml=None, refl=None, grow=None, dim2=False):
        """
        create GridModel

        :param l0: length scales
        :param doml: domain length before, after object center
        :param refl: refined region length ...
        :param grow: growth rate ...
        :param dim2: a 2d domain, no z axis

        l0, doml, refl, grow accepts:
        [[x1,x2],[y1,y2],[z1,z2]], without [z1,z2] if 2d
        replace [x1,x2] with single x for [x,x], same for y z
        replace entire [[],...] with single x for isotropic [[x,x],...]
        replace anything (x1 or [x1,x2] or entire [[],...]) with None for default value(s) at the place
        """
        ndim = 2 if dim2 else 3

        l0d = fill_ll_broadcast(1, [ndim, 2])
        domlx = [[20, 5]]
        domly = [[20, 20]]
        reflx = [[1, 2.5]]
        refly = [[1, 1]]
        growx = [[1.4, 1.02]]
        growy = [[1.4, 1.4]]

        domld = domlx + domly
        refld = reflx + refly
        growd = growx + growy
        if not dim2:
            domld += domly
            refld += refly
            growd += growy

        l0 = fill_ll_default(l0, l0d)
        doml = fill_ll_default(doml, domld)
        refl = fill_ll_default(refl, refld)
        grow = fill_ll_default(grow, growd)

        l0 = fill_ll_broadcast(l0, [ndim, 2])
        doml = fill_ll_broadcast(doml, [ndim, 2])
        refl = fill_ll_broadcast(refl, [ndim, 2])
        grow = fill_ll_broadcast(grow, [ndim, 2])

        return cls(
            dim2,
            ndim,
            np.array(l0, dtype=float),
            np.array(doml, dtype=float),
            np.array(refl, dtype=float),
            np.array(grow, dtype=float),
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

    @property
    def center(self):
        xyz = self.l0[:, 0] * self.doml[:, 0]
        if self.dim2:
            xyz = xyz[:2]
        return xyz
