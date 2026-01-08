from pyvicar.tools.collections import struct  # for containers, like python collections
from pyvicar.grid import GridModel
from pyvicar.geometry import create_sphere


# the default kwargs are for formal running, but can be overriden like in test
# only pass the ones that might need special overriding, directly specify in function if fixed, like U
def gen_params(
    # --- case --- #
    name="test",
    allow_restart=False,
    # --- device --- #
    npx=12,
    npy=8,
    # --- geometry --- #
    d=1,  # sphere diameter
    # --- physics --- #
    re=200,  # by inlet U and sphere d
    st=0.2,  # by inlet U, sphere d, vortex street freq
    # --- discrete --- #
    d_by_dx=40,  # d/dx, grid resolution
    T_by_dt=400,  # T/dt, time resolution
    ntStep=400 * 20,
    nDump=10,
    nRestart=100,
    gcss="gcm",
):

    p = struct()

    # --- case --- #

    p.name = name
    p.allow_restart = allow_restart

    # --- device --- #

    p.npx = npx
    p.npy = npy

    # prefer a grid model with explicit parameters in formal projects
    # Note: use 1.5d as downstream length scale as vortex spacing scale
    # Note: 1.02,2.5,5 gives acceptable aspect ratio at outlet and practical grid number.
    #       this parameter set (except l0) is also the pyvicar default.
    #       high aspect ratio gives instability in high-shear region (vortex)
    p.gm = GridModel.create(
        l0=[[d, 1.5 * d], d, d],
        doml=[[20, 5], 20, 20],
        refl=[[1, 2.5], 1, 1],
        grow=[[1.4, 1.02], 1.4, 1.4],
    )

    # --- geometry --- #

    p.d = 1

    # --- physics --- #

    p.re = re
    p.st = st
    p.U = 1  # inlet velocity
    p.f = p.U / d
    p.T = 1 / p.f

    # --- discrete --- #

    p.dx = d / d_by_dx
    p.dt = p.T / T_by_dt
    p.ntStep = ntStep
    p.nDump = nDump
    p.nRestart = nRestart
    p.gcss = gcss

    return p
