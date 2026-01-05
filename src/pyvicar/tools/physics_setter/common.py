import numpy as np
from pyvicar._format import Table
import pyvicar.tools.log as log


def set_inlet(c, inlet, vel):
    u, v, w = vel
    bc = getattr(c.input.bc, inlet)
    setattr(bc, f"bc{inlet}", "dirichlet")
    setattr(bc, f"u{inlet}", u)
    setattr(bc, f"v{inlet}", v)
    setattr(bc, f"w{inlet}", w)

    c.input.domain.uinit = u
    c.input.domain.vinit = v
    c.input.domain.winit = w


def set_scalar_inlet(var, inlet, val):
    setattr(var, f"bc{inlet}", "dirichlet")
    setattr(var, f"tbc{inlet}", val)
    var.icVal = val


def set_cfl(c, cfl, U, dx):
    c.input.timeStep.dt = cfl * dx / U


def set_tdt(c, tdt, T):
    c.input.timeStep.dt = T / tdt


def get_cfl(c, U, dx):
    return c.input.timeStep.dt.value * U / dx


def get_tdt(c, T):
    return T / c.input.timeStep.dt.value


def get_ndmp(c, T):
    return T / c.input.timeStep.dt.value / c.input.timeStep.nDump.value


def print_keys(header, name, v, d, keys):
    if v is None:
        v = "N/A"

    if d is None:
        d = {}
        for key in keys:
            d[key] = "N/A"

    line = [header, name, "=", v, "@"]

    for key in keys:
        line += [key, "=", d[key]]

    return line


def stat_tstep(c, cfl=None, tdt=None, ndmp=None):
    if cfl is not None:
        cfl_v = get_cfl(c, **cfl)
    else:
        cfl_v = None

    if tdt is not None:
        tdt_v = get_tdt(c, **tdt)
    else:
        tdt_v = None

    if ndmp is not None:
        ndmp_v = get_ndmp(c, **ndmp)
    else:
        ndmp_v = None

    header = "Time Step Stat:"

    (
        Table.create()
        .add(print_keys(header, "CFL", cfl_v, cfl, ["U", "dx"]))
        .add(print_keys(header, "T/dt", tdt_v, tdt, ["T"]))
        .add(print_keys(header, "Ndmp", ndmp_v, ndmp, ["T"]))
        .format()
        .log()
    )


def set_re(c, re, U, L):
    c.input.timeStep.re = re / (U * L)


def get_re(c, U, L):
    return c.input.timeStep.re.value * U * L


# Schlichting turbulent BL skin friction coefficient estimate
def get_tau(c, U, L):
    nu_inv = c.input.timeStep.re.value
    re = nu_inv * U * L
    Cf = (2 * np.log(re) / np.log(10) - 0.65) ** -2.3
    return 0.5 * U**2 * Cf


# tau is divided by rho already
def get_yplus(c, y, tau):
    nu_inv = c.input.timeStep.re.value
    if isinstance(tau, dict):
        tau = get_tau(c, **tau)
    return np.sqrt(tau) * y * nu_inv


def stat_viscosity(c, re=None, yplus=None):
    if re is not None:
        re_v = get_re(c, **re)
    else:
        re_v = None

    if yplus is not None:
        yplus_v = get_yplus(c, **yplus)
    else:
        yplus_v = None

    header = "Viscosity Stat:"

    (
        Table.create()
        .add(print_keys(header, "Re", re_v, re, ["U", "L"]))
        .add(print_keys(header, "Y+", yplus_v, yplus, ["y", "tau"]))
        .format()
        .log()
    )
