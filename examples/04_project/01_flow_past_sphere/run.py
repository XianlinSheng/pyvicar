import sys
import studies
import runlib

# usage  : python run.py <job> ...
# example: python run.py compress re200rec

# one can choose to either take by arg python run.py <code> or specify inside script
code = sys.argv[1]
# code = "re1000devLC"

p = studies.to_params(code)

print(p)

c = runlib.make_case(p)

c.write()

# c.show_grid(gm.center)

c.stat_grid()
c.stat_tstep(
    cfl={"U": p.Umax, "dx": p.dx},
    tdt={"T": p.T},
    ndmp={"T": p.T},
)
c.stat_viscosity(
    re={"U": p.U, "L": p.d},
    yplus={"y": p.dx, "tau": {"U": p.U, "L": p.d}},
)
c.stat_partition()

# c.bash()
# c.sbatch()
