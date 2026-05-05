# runlib.py is the detail code to setup a case from params struct
# typically one first copy an example in 01_geometry section and change to the desired geometry
# then the front part that computes variables goes to params.py, studies.py is modified accordingly
# the middle part that setup the case goes here
# and the end part that writes and prints stat goes into run.py


def make_case(p):
    c = p.Case(p.name)

    c.apply_grid_model(p.gm, dx=p.dx)

    body, surf = c.append_sphere(p.d / 2, p.dx, p.gm.center)

    c.set_inlet("x1", [p.U, 0, 0])

    c.set_re(p.re, U=p.U, L=p.d)

    match p.stage:
        case "dev":
            T = 100 * p.T
            nT = 1
            ndumps = 1
        case "rec":
            # 10 T is approx. a cycle of vortex
            # one can analyze it by posting draglift of dev. sim.
            T = p.T
            nT = 5 * 10
            ndumps = 1

    c.set_tstep(
        U=p.Umax,
        dx=p.dx,
        T=T,
        nT=nT,
        nsteps_unit=10,
        ndumps=ndumps,
        step_test=p.step_test,
    )

    if p.body_test:
        c.set_partition(nproc_node=16, nnode_max=1)
    else:
        c.set_partition(nproc_node=48, nnode_max=16)

    c.input.ib.form = p.gcss

    c.job.enable()
    c.job.partition = "partition"
    c.job.account = "account"

    if p.allow_restart:
        c.restart.read()
        if c.restart:
            c.restart.to_restart_in()
            c.input.domain.iRestart = True

    return c
