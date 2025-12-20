import numpy as np
from pyvicar.grid.segment import Segment, connect_segs
import pyvicar.tools.log as log


def refine_grid(
    case,
    dir,
    keypoints,
    dx,
    lgrow=1.05,
    rgrow=1.05,
    smooth_iter=10,
    resample_n="prime_comb",
    prime_comb=[2, 3],
):
    dir = dir.lower()
    if len(keypoints) != 3:
        raise Exception(
            f"Expected keys have 3 elements: [x1, x2, xout], but encountered {keypoints}"
        )
    x1, x2, l = keypoints
    log.log(
        f"Refine {dir} axis keypoints {[0, x1, x2, l]}, left right growth rate {[lgrow, rgrow]}"
    )

    x2 = Segment.uniform_dx(x1, x2, dx)
    x1 = x2.grow_toward_left(0, lgrow)
    x3 = x2.grow_toward_right(l, rgrow)
    x1.smooth(lslope=x1.lslope(), rslope=x2.lslope(), iter=smooth_iter)
    x3.smooth(lslope=x2.rslope(), rslope=x3.rslope(), iter=smooth_iter)
    x = connect_segs([x1, x2, x3])

    if isinstance(resample_n, str):
        match resample_n.lower():
            case "none":
                pass
            case "prime_comb":
                x.resample(prime_comb=prime_comb)
    elif isinstance(resample_n, int):
        x.resample(resample_n)
    else:
        raise Exception(
            f"Expect resample_n to be either int or string in ['none', 'prime_comb'], but encountered {type(resample_n)} {resample_n}"
        )

    grid = getattr(case, f"{dir}grid")
    if not grid:
        grid.enable()
    grid.nodes = x.grid[:, np.newaxis]

    setattr(case.input.domain, f"{dir}gridUnif", "nonuniform")
    setattr(case.input.domain, f"n{dir}", x.npoint)
    setattr(case.input.domain, f"{dir}out", x.end)


def uniform_grid_n(case, dir, l, n):
    dir = dir.lower()
    setattr(case.input.domain, f"{dir}gridUnif", "uniform")
    setattr(case.input.domain, f"n{dir}", n)
    setattr(case.input.domain, f"{dir}out", l)


def uniform_grid_dx(case, dir, l, dx):
    uniform_grid_n(case, dir, l, l // dx + 1)


def grid_2d(case, dz):
    case.input.domain.nDim = 2
    case.input.domain.zgridUnif = "uniform"
    case.input.domain.nz = 3
    case.input.domain.zout = dz * 2
