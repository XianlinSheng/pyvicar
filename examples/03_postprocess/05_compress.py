import pyvicar
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi

# 5. compress
# this script reads the case vtm dump and compress the sub vtr to binary

# use at least v1.0.2 if only for postprocess because in lower version
# instantiating Case(...) alone would truncate existing input files
pyvicar.assert_api_version("1.0.2", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

c = Case("tut_sphere")

c.dump.vtm.read()

# specify inplace=False to create fields.x/fields.x.y.bin.vtr without overwrite original
# binary sub vtr takes ~ 45% space of ascii
# vtm is not changed, only replace the heavy vtr files it points to
c.dump.vtm.to_binary()

# # or to a single unstruc vtk, but may take even larger space
# c.dump.vtm.to_vtks(keep_vtms=True)

mpi.print_elapsed_time()

# similar, mpirun -np x python compress.py to compress in parallel
