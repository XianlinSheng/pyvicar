import pyvicar as pvc
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi


# 4. compress
# this script reads the case vtk dump and compress to vtr binary

Case = pvc.case.import_version("~/opt/Vicar3D/common")

name = "tut_compress"
npx, npy = 4, 4

log.log_host(f"Compress Case: {name}")
c = Case(name)
c.dump.vtm.read()
# default keep_vtm=True in case of mistakes
c.dump.vtm.to_vtrs(npx=npx, npy=npy, keep_vtms=True)

# # or to single unstruc vtk, for gp version
# c.dump.vtm.to_vtks(keep_vtms=True)

# Versions except gp might use vtr because of full structuredness.
# In this case vtr can compress > 50% space but vtk may introduce additional 30%
# because the output vtm is already made up with multiple ascii vtr


mpi.print_elapsed_time()
