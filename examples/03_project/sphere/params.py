import pyvicar
from pyvicar.tools.collections import struct
from pyvicar.grid import GridModel

# params.py is the starting point of a project
# one params struct fully defines a case,
# make_params takes in the minimal degrees of freedom and spawn the rest parameters
# some are set constants like U, d, and do not need to be passed as args
# a complex project may need many more arguments than the example below


pyvicar.assert_api_version("1.0.1", "1.1.0")


def make_params(
    version="common",
    name="test",
    allow_restart=True,
    re=200,  # using inlet U and sphere d
    d_by_dx=40,  # d/dx, grid resolution
    gcss="gcm",
    stage="dev",  # see studies.py
    step_test=False,  # run for only one time step
    body_test=False,  # very lightweight job runnable locally
):
    p = struct()

    p.version = version
    p.name = name
    p.allow_restart = allow_restart
    p.re = re
    p.d_by_dx = d_by_dx
    p.stage = stage
    p.gcss = gcss
    p.step_test = step_test
    p.body_test = body_test

    p.Case = pyvicar.import_case(f"~/opt/ViCar3D/versions/{version}")

    p.d = 1

    # prefer a grid model with explicit parameters in formal projects
    # Note: use 1.5d as downstream length scale as vortex spacing scale
    # Note: 1.02,2.5,5 gives acceptable aspect ratio at outlet and practical grid number.
    #       this parameter set (except l0) is also the pyvicar default.
    #       high aspect ratio gives instability in high-shear region (vortex)
    p.gm = GridModel.create(
        l0=[[p.d, 1.5 * p.d], p.d, p.d],
        doml=[[20, 5], 20, 20],
        refl=[[1, 2.5], 1, 1],
        grow=[[1.4, 1.02], 1.4, 1.4],
    )

    p.U = 1  # inlet velocity
    p.T = p.d / p.U
    p.f = 1 / p.T

    p.dx = p.d / p.d_by_dx

    p.Umax = 2 * p.U

    return p
