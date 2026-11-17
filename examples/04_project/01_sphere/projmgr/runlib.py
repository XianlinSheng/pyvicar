import pyvicar
import numpy as np
import matplotlib.pyplot as plt

pyvicar.assert_api_version("1.0.3", "1.1.0")


def make_case(p):
    c = p.Case(p.name)
    c = init_ib2(p, c)
    c = init_basics(p, c)
    c = init_restart(p, c)

    return c


def init_basics(p, c):

    c.apply_grid_model(p.gm, dx=p.dx)

    c.set_inlet("x1", [p.U, 0, 0])

    c.set_re(p.re, p.U, p.chord)

    c.input.bc.y1.bcy1 = "symmetry"

    c = init_partition(p, c)

    if p.body_test:
        ncycle = 1
        tstep_kwargs = {"nsteps_unit": 100}
    else:
        ncycle = 2
        tstep_kwargs = {}

    # ab2 needs more stable params
    if c.input.timeStep.advecScheme == "ab2":
        tstep_kwargs = {"cfl_max": 0.2}

    c.set_tstep(p.Umax, p.dx, p.T, nT=100, step_test=p.step_test, **tstep_kwargs)

    c.input.misc.stopTime = ncycle * p.T

    c.input.ib.form = p.gcss

    c.input.poisson.itermaxPoisson = 10000

    c.input.ad.resmax = 1e-6

    return c


def init_restart(p, c):
    if p.allow_restart:
        c.restart.read()
        if c.restart:
            c.restart.to_restart_in()
            c.input.domain.iRestart = True
            c.ib2.iRestart = True

    return c


def init_partition(p, c):
    if p.legacy_parallel:
        return init_partition_legacy(p, c)

    c.job.enable()
    c.job.condaDeactivate = True
    c.job.modulePurge = True
    c.job.moduleUse = True
    c.job.moduleLoad = True
    c.job.logfile = ""
    c.job.output = "log.out"
    c.job.error = "log.err"

    match f"{p.platform}&{p.version}":
        case "local&common" | "local&common-0.1.0":
            c.set_partition(nproc_node=16, nnode_max=1, ncell_proc=200e3)
        case "local&gpu":
            c.set_partition(nproc_node=1, nnode_max=1, ncell_proc=20e6)
            # c.input.misc.iComm = "mpi"
        case "rockfish&common" | "rockfish&common-0.1.0":
            c.set_partition(nproc_node=48, nnode_max=16, ncell_proc=200e3)
            c.job.partition = "parallel"
            c.job.account = "rmittal3-condo"
            c.job.time = "3-0:0:0"
        case "rockfish&gpu":
            c.set_partition(nproc_node=4, nnode_max=4, ncell_proc=20e6)
            c.job.partition = "a100"
            c.job.account = "rmittal3_gpu"
            c.job.gres = [f"gpu:{c.nproc}"]
            c.job.time = "3-0:0:0"
        case "blackwell&common" | "blackwell&common-0.1.0":
            raise Exception(f"Blackwell supports only gpu version")
        case "blackwell&gpu":
            c.set_partition(nproc_node=4, nnode_max=1, ncell_proc=20e6)
            c.job.partition = "gpu"
            c.job.account = "fpcl"
            c.job.gres = [f"gpu:{c.nproc}"]
            c.job.qos = "normal"
            c.job.flags = ["--no-requeue"]
            c.job.time = "3-10:0:0"
        case "lenovo&common":
            c.set_partition(nproc_node=32, nnode_max=1, ncell_proc=200e3)
        case "lenovo&gpu":
            c.set_partition(nproc_node=1, nnode_max=1, ncell_proc=20e6)
        case _:
            raise Exception(f"Unrecognized platform-version {p.platform}-{p.version}")

    return c


def init_partition_legacy(p, c):
    c.job.enable()
    c.job.condaDeactivate = True
    c.job.modulePurge = True
    c.job.moduleUse = True
    c.job.moduleLoad = True
    c.job.logfile = ""
    c.job.output = "log.out"
    c.job.error = "log.err"

    match p.version:
        case "common":
            c.input.parallel.npx = 24
            c.input.parallel.npy = 32
            c.job.autofill()
            c.job.partition = "parallel"
            c.job.account = "rmittal3-condo"
            c.job.nodes = 16
            c.job.ntasksPerNode = 48
        case "gpu":
            c.input.parallel.npx = 4
            c.input.parallel.npy = 4
            c.job.autofill()
            c.job.partition = "a100"
            c.job.account = "rmittal3_gpu"
            c.job.nodes = 4
            c.job.ntasksPerNode = 4
            c.job.gres = [f"gpu:{c.nproc}"]
        case _:
            raise Exception(f"Unrecognized solver version {p.version}")

    return c


def init_ib2(p, c):
    body, surf, ib2 = c.append_ib2_membrane(
        type="wing",
        nuv=[p.nu, p.nv],
        xyz0=p.gm.center - np.array([p.ubuffer, p.vbuffer, 0]),
        uxyz=[p.lu, 0, 0],
        vxyz=[0, p.lv, 0],
    )

    ib2.du = p.lu / (p.nu - 1)
    ib2.dv = p.lv / (p.nv - 1)

    ib2.shdr_u = p.ubuffer
    ib2.shdr_v = p.vbuffer

    ib2.hmrs_l = p.hmrs_l
    ib2.ulna_l = p.ulna_l
    ib2.hand_l = p.hand_l

    ib2.hmrs_fth_n = p.hmrs_fth_n
    ib2.ulna_fth_n = p.ulna_fth_n
    ib2.hand_fth_n = p.hand_fth_n

    ib2.f = p.f

    for name in ib2.dofs:
        ib2.set_dof_fourier(name, getattr(p.motion, name))

    ib2.set_fth_kf("l", p.fth_ls)
    ib2.set_fth_kf("w", p.fth_ws)
    for name in ib2.joints[:4]:
        ib2.set_fth_joint_fourier(name, getattr(p.motion, f"{name}_fth"))

    ib2.camber_max = p.camber
    ib2.twist_mode = p.twist
    ib2.twist_atan_coeff = p.twist_k

    fth_shape_uv = fth_outline()
    # outline_plot(fth_shape_uv)

    ib2.fth_shape_npoint = fth_shape_uv.shape[0]
    ib2.fth_shape_uv = fth_shape_uv

    return c


def fth_outline(
    length=1.0,
    max_width=0.2,
    n_points=10,
):
    a = length / 2
    b = max_width / 2

    # Ellipse centered at (a, 0)
    # Top -> tip -> bottom
    t = np.linspace(np.pi / 2, -np.pi / 2, n_points)

    x_ellipse = a * np.cos(t) + a
    y_ellipse = b * np.sin(t)

    # Root vertical face (bottom -> top to close CCW)
    x_root = np.array([0.0, 0.0])
    y_root = np.array([-b, b])

    # Assemble CCW outline
    x_outline = np.concatenate(
        [
            [0.0],  # upper-left root
            x_ellipse,  # ellipse top → tip → bottom
            x_root,  # root bottom → top
        ]
    )

    y_outline = np.concatenate([[b], y_ellipse, y_root])

    return np.column_stack([x_outline, y_outline])


def outline_plot(outline):
    plt.figure(figsize=(8, 2))
    plt.plot(outline[:, 0], outline[:, 1], "-k", linewidth=2)
    plt.fill(outline[:, 0], outline[:, 1], alpha=0.3)

    plt.gca().set_aspect("equal", adjustable="box")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Outline")
    plt.grid(True)

    plt.tight_layout()
    plt.show()
