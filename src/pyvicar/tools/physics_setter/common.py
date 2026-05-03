import numpy as np
import math
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


# T is the time scale
# U, dx are max velocity and min dx
# set the ntStep, dt, nDump, nRestart
# that is most efficient under cfl constraint
# and the ntStep at a good number, also divisible by number of dumps
# also set the poisson resmax to nearly dt * resmax ~ 1e-6, in scale of div(U)
def set_tstep(
    c,
    U,
    dx,
    T,
    nT=1,
    cfl_max=0.4,
    nsteps_unit=2000,
    nrestart_max=100,
    ndumps=50,
    divu_tol=1e-6,
    step_test=False,
):
    if nsteps_unit % ndumps != 0:
        raise ValueError(
            f"Steps in a unit {nsteps_unit} not divisible by the total number of dumps {ndumps} within the time scale. "
            + f"It is sufficient that steps | dumps if nsteps_unit | dumps. Though not necessary, this is enforced to make sure it works on any case."
        )
    dt_max = cfl_max * dx / U
    unit_dt_max = nsteps_unit * dt_max
    units = int(np.ceil(T / unit_dt_max))
    nsteps = units * nsteps_unit
    ntstep = nT * nsteps
    dt = T / nsteps
    ndump = nsteps // ndumps
    nrestart = min(ndump, nrestart_max)

    resmax = divu_tol / dt
    eps = 1e-3
    k = np.floor(np.log(resmax) / np.log(10) + eps)
    resmax = np.floor(resmax / 10**k + eps) * 10**k

    if step_test:
        ntstep = 1
        ndump = 1
        nrestart = 1

    c.input.timeStep.ntStep = ntstep
    c.input.timeStep.dt = dt
    c.input.timeStep.nDump = ndump
    c.input.timeStep.nRestart = nrestart
    c.input.poisson.resmaxPoisson = resmax


def get_tdt(c, T):
    return T / c.input.timeStep.dt.value


def get_ndmp(c, T):
    return T / c.input.timeStep.dt.value / c.input.timeStep.nDump.value


def get_divu(c):
    return c.input.poisson.resmaxPoisson.value * c.input.timeStep.dt.value


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

    divu_v = get_divu(c)

    header = "Time Step Stat:"

    (
        Table.create()
        .add(print_keys(header, "CFL", cfl_v, cfl, ["U", "dx"]))
        .add(print_keys(header, "T/dt", tdt_v, tdt, ["T"]))
        .add(print_keys(header, "Ndmp", ndmp_v, ndmp, ["T"]))
        .add(print_keys(header, "DivU", divu_v, {}, []))
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


# only set input.parallel
def set_partition_total(c, nproc):
    nxc = c.input.domain.nx.value - 1
    nyc = c.input.domain.ny.value - 1

    # assume npx <= npy, npx <= npy
    flip = False
    if nxc > nyc:
        nxc, nyc = nyc, nxc
        flip = True

    # find the best pair s.t. npx/npy ~ nxc/nyc
    # residual := npx*nyc - npy*nxc

    # candidates
    ncand = int(np.sqrt(nproc))
    cands = np.arange(1, ncand + 1, dtype=int)

    cands = cands[nproc % cands == 0]
    # complementaries
    comps = nproc // cands

    # min residual
    imin = np.argmin(np.abs(cands * nyc - comps * nxc))

    npx, npy = cands[imin], comps[imin]
    if flip:
        npx, npy = npy, npx

    c.input.parallel.npx = int(npx)
    c.input.parallel.npy = int(npy)


# node-based auto calc number of partitions, part_ncell is approx
# since its node-based, also set job file
def set_partition(c, nproc_node=48, ncell_proc=200e3, nnode_max=16):
    nxc = c.input.domain.nx.value - 1
    nyc = c.input.domain.ny.value - 1
    nzc = c.input.domain.nz.value - 1
    ncell_total = nxc * nyc * nzc

    nnode = max(1, min(nnode_max, int(np.round(ncell_total / ncell_proc / nproc_node))))
    nproc = nnode * nproc_node

    set_partition_total(c, nproc)

    c.job.enable()
    c.job.ntasksPerNode = nproc_node
    c.job.nodes = nnode


def get_nproc(c):
    npx = c.input.parallel.npx.value
    npy = c.input.parallel.npy.value
    return npx, npy, c.nproc


def get_ncell(c):
    nxc = c.input.domain.nx.value - 1
    nyc = c.input.domain.ny.value - 1
    nzc = c.input.domain.nz.value - 1
    return nxc, nyc, nzc, nxc * nyc * nzc


def get_nnode(c):
    if c.job:
        return c.job.nodes.value, c.job.ntasksPerNode.value
    else:
        return None, None


def div_or_minmax(ntot, nbin):
    ncell_part = ntot // nbin
    if ntot % nbin == 0:
        return (ncell_part,)
    else:
        return (ncell_part, ncell_part + 1)


def mul_minmax(*minmaxs):
    minv = 1
    maxv = 1
    for minmax in minmaxs:
        if len(minmax) == 1:
            minv *= minmax[0]
            maxv *= minmax[0]
        else:
            minv *= minmax[0]
            maxv *= minmax[1]
    if minv == maxv:
        return (minv,)
    else:
        return (minv, maxv)


def str_minmax(minmax):
    return "~".join(f"{n:,}" for n in minmax)


def stat_partition(c):
    npx, npy, nproc = get_nproc(c)
    nxc, nyc, nzc, ncell = get_ncell(c)
    nnode, nproc_node = get_nnode(c)

    header = "Partition Stat:"

    nxc_proc = div_or_minmax(nxc, npx)
    nyc_proc = div_or_minmax(nyc, npy)

    (
        Table.create()
        .add(
            [
                header,
                f"{nxc} XCells",
                f"/ {npx} XProcs",
                "=",
                str_minmax(nxc_proc),
                "XCells/XProc",
            ]
        )
        .add(
            [
                header,
                f"{nyc} YCells",
                f"/ {npy} YProcs",
                "=",
                str_minmax(nyc_proc),
                "YCells/YProc",
            ]
        )
        .format()
        .log()
    )

    log.log(
        f"{header} {ncell:,} Cells / {nproc} Procs = {str_minmax(mul_minmax(nxc_proc, nyc_proc, (nzc,)))} Cells/Proc"
    )

    if nnode:
        log.log(
            f"{header} {nproc} Procs = {nproc_node} Procs/Node * {nnode} Nodes - {nproc_node*nnode-nproc} Unused Procs"
        )
