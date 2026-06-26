# runlib.py is the detail code to setup a case from params struct
# typically one first copy an example in 01_geometry section and change to the desired geometry
# then the front part that computes variables goes to params.py, studies.py is modified accordingly
# the middle part that setup the case goes here
# and the end part that writes and prints stat goes into run.py
# it would be wise to first stick to such a simple script when handling an unknown case
# once the behavior is clear enough for a param space batch study, transfer into a project structure
# the project structure would be always changing to add/change/integrate functionalities during analysis
# so these scripts are not hard-coded in the lib but free to be tailored as needed


def make_case(p):
    c = p.Case(p.name)

    c.apply_grid_model(p.gm, dx=p.dx)

    body, surf = c.append_sphere(p.d / 2, p.dx, p.gm.center)

    c.set_inlet("x1", [p.U, 0, 0])

    c.set_re(p.re, U=p.U, L=p.d)

    match p.stage:
        case "dev":
            # start from 100T y/z starts to become anisotropic
            # one can change it to 80T to record the transition process
            # for an unknown case, this number is concluded before making a batch project lke this
            # or concluded from an existing study and decide to make a new branch of params space to analyze
            # like here, to further study the transition process,
            # one can choose to add another study seg .add_optional_int("start", "s", off_value=100)
            # so as to change the starting position of recording to run new study batches
            # and also backward compatible with existing cases
            # there are add_optional_int, ..._choice, ..._branch available for further compatible extensions
            # but remember open a new project once the existing features become irrelevent and messy
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

    # partition and job are coupled so are configured together
    c.job.enable()
    match f"{p.platform}-{p.version}":
        case "local-common":
            c.set_partition(nproc_node=16, nnode_max=1)
        case "local-gpu":
            c.set_partition(nproc_node=1, nnode_max=1)
        case "remote-common":
            c.set_partition(nproc_node=48, nnode_max=16, ncell_proc=100e3)
            c.job.partition = "partition"
            c.job.account = "jsmith01"
        case "remote-gpu":
            c.set_partition(nproc_node=4, nnode_max=4, ncell_proc=5e6)
            c.job.partition = "partition"
            c.job.account = "jsmith01"
        case _:
            raise Exception(f"Unrecognized platform-version {p.platform}-{p.version}")

    c.job.condaDeactivate = True
    c.job.modulePurge = True
    c.job.moduleUse = True
    c.job.moduleLoad = True
    c.job.logfile = ""
    c.job.output = "log.out"
    c.job.error = "log.err"

    c.input.ib.form = p.gcss

    if p.allow_restart:
        c.restart.read()
        if c.restart:
            c.restart.to_restart_in()
            c.input.domain.iRestart = True

    return c
