from params import gen_params
from gen import gen_case

p = gen_params(
    # --- formal options --- #
    name="test",
    # --- test overrides --- #
    npx=4,
    npy=4,
    d_by_dx=10,
)

# to refer to a case outside the script, copy the p = gen_params(...) call or import the p (like compress)
# the arch is designed that the p = gen_params(...) call completely defines a case, p is the seed
# and one can copy the formal gen_params call to params.py to access all p easily

# python run_test.py -> generate params, case, run
# from run_test import p -> only get the p struct
if __name__ == "__main__":

    # this struct can be directly printed to check the computed parameters
    print(p)

    c = gen_case(p)
    # the c.apply_grid_model(p.gm) in this function will print out grid info

    # this show and stat grid, but generally only use it for the first time
    c.show_grid(p.gm.center)

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

    # then follow these standard operating procedures in 00_readme to check the case:

    # c.mpirun()
    # c.sbatch()

    # once all checks pass, one can copy this test script to a formal run script and remove the overrides
