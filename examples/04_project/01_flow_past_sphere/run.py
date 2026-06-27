import sys
import projmgr as mgr

# usage  : python run.py <job> ...
# example: python run.py re1000devr120LC

code = sys.argv[1]
# code = "re1000devr120LC"

p = mgr.studies.to_params(code)

print(p)

c = mgr.runlib.make_case(p)

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
