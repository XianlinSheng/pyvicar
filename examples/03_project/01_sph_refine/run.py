from params import gen_params
from gen import gen_case

p40 = gen_params(
    # --- formal options --- #
    name="r40",
    d_by_dx=40,
)

p20 = gen_params(
    # --- formal options --- #
    name="r20",
    d_by_dx=20,
)

# everything that is changed temporarily in test should be in test overrides block,
# so that removing these will give back to EXACTLY THE SAME formal case
p20test = gen_params(
    # --- formal options --- #
    name="r20test",
    d_by_dx=20,
    # --- test overrides --- #
    allow_restart=False,
    npx=4,
    npy=4,
    ntStep=1,
    nDump=1,
)


# to refer to a case outside the script,
# import the p (like in compress), or copy the gen_params call (but will not be synchronized)
# the arch is designed that the p = gen_params(...) call completely defines a case, p is the seed

# python run.py -> generate params, case, run
# from run import p -> only get the p struct
if __name__ == "__main__":
    p = p20test

    # this struct can be directly printed to check the computed parameters
    print(p)

    c = gen_case(p)
    # the c.apply_grid_model(p.gm) in this function will print out grid info

    # this show and stat grid, but generally only use it for the first time
    # c.show_grid(p.gm.center)

    # these make stat for quality checks
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

    # args in these two stat can be removed and the corresponding print will become N/A
    # the required keys in a dict can be inferred from the print info
    # tau in yplus can either be specified or estimated,
    #   using Schlichting formula if given a dict with U and L
    #   same as https://www.cfd-online.com/Tools/yplus.php

    # 00_readme provides the standard operating procedure to check the case

    # c.mpirun()
    # c.sbatch()
