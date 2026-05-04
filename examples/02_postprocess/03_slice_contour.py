import pyvicar
import pyvicar.tools.mpi as mpi
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf

# 3. slice contour
# this script reads the case vtk dump and generate a quick animation of contour on a slice

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

c = Case("tut_sphere")

c.dump.read()

vel_mid = c.create_slicecontour_video(
    c.dump.vtm,
    c.dump.marker,
    normal="y",
    # origin=[None, None, None], # pass None to take midplane in the corresponding axis
    plotter_f=pf.set_cam_compass([20, 20, 20], l0=1, oclock=3),
    contour_color=lb.Color.field(lb.Field.vector("VEL", "mag"), clim=[0, 1.5]),
    # contour_color=lb.Color.field(lb.Field.scalar("P"), clim=[-0.5, 0.5]),
    # contour_color=lb.Color.field(lb.Field.vor_from_vel("VEL", "z"), clim=[-1, 1]),
    keep_frames=False,
    out_name=f"vel_mid",
)

vor_mid = c.create_slicecontour_video(
    c.dump.vtm,
    c.dump.marker,
    normal="y",
    plotter_f=pf.set_cam_compass([20, 20, 20], l0=1, oclock=3),
    contour_color=lb.Color.field(lb.Field.vor_from_vel("VEL", "y"), clim=[-1, 1]),
    keep_frames=False,
    out_name=f"vor_mid",
)

mpi.print_elapsed_time()
