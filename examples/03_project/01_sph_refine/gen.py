from pyvicar.case.common import Case


def gen_case(p):
    c = Case(p.name)

    if p.allow_restart:
        # restart simulation if there are restart files
        c.allow_restart()

    c.apply_grid_model(p.gm, dx=p.dx)

    body, surf = c.append_sphere(p.d / 2, p.dx, p.gm.center)

    c.set_inlet("x1", [p.U, 0, 0])

    c.set_re(p.re, p.U, p.d)

    c.input.parallel.npx = p.npx
    c.input.parallel.npy = p.npy

    c.input.timeStep.ntStep = p.ntStep
    c.input.timeStep.nDump = p.nDump
    c.input.timeStep.nRestart = p.nRestart
    c.input.timeStep.dt = p.dt

    c.input.poisson.itSolverType = "pbicgstab"
    c.input.poisson.itermaxPoisson = 10000
    c.input.poisson.resmaxPoisson = 1e-4

    c.input.hybridization.upwindWeight = "central"

    c.input.ib.form = p.gcss

    c.job.enable()
    c.job.jobName = p.name
    # change to the account to use, or pass it into gen_params(...)
    c.job.account = "jsmith01"

    c.write()

    return c
