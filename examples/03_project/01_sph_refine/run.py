from params import gen_params
from gen import gen_case

p40 = gen_params(
    # --- formal options --- #
    name="r40",
    d_by_dx=40,
)

p40 = gen_params(
    # --- formal options --- #
    name="r20",
    d_by_dx=20,
)


if __name__ == "__main__":
    p = p40

    print(p)

    c = gen_case(p)

    # c.show_grid(p.gm.center)
    c.stat_grid()
    c.stat_tstep(
        cfl={"U": 2 * p.U, "dx": p.dx},
        tdt={"T": p.T},
        ndmp={"T": p.T},
    )
    c.stat_viscosity(
        re={"U": p.U, "L": p.d},
        yplus={"y": p.dx, "tau": {"U": p.U, "L": p.d}},
    )

    c.write()

    # c.mpirun()
    c.sbatch()
