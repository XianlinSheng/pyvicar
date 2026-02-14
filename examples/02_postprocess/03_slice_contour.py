import pyvicar as pvc
import pyvicar.tools.mpi as mpi
from pyvicar.tools.post.dump import Color, Field

# 3. slice contour
# this script reads the case vtk dump and generate a quick animation of contour on a slice

Case = pvc.case.import_version("~/opt/Vicar3D/common")

c = Case("tut_slice_contour")
c.dump.read()

full = c.create_slicecontour_video(
    c.dump.vtm,
    c.dump.marker,
    normal="z",
    # origin=[None, None, None],
    contour_color=Color.field(Field.vector("VEL", "mag"), clim=[0, 1.5]),
    # contour_color=Color.field(Field.scalar("P"), clim=[-0.5, 0.5]),
    # contour_color=Color.field(Field.vor_from_vel("VEL", "z"), clim=[-1, 1]),
    keep_frames=True,
    out_name=f"vel_full",
)

clip = c.create_slicecontour_video(
    c.dump.vtm,
    c.dump.marker,
    normal="z",
    # origin=[None, None, None],
    clip=[17, 27, 17, 23, 17, 23],
    contour_color=Color.field(Field.vector("VEL", "mag"), clim=[0, 1.5]),
    keep_frames=True,
    out_name=f"vel_clip",
)

mpi.print_elapsed_time()
