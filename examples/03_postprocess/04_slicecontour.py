import pyvicar
import pyvicar.tools.mpi as mpi
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf

# 4. slice contour
# this script reads the case vtk dump and generate a quick animation of contour on a slice

# use at least v1.0.2 if only for postprocess because in lower version
# instantiating Case(...) alone would truncate existing input files
pyvicar.assert_api_version("1.0.3", "1.1.0")  # compact post is v1.0.3 feature

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

# this is also workable for 2d cases in 01_geometry because we are posting z-normal slice
c = Case("tut_sphere")

# for 2d cases, change it to [20, 20, dz/2], dz/2 is small can be 0
cam_f = pf.set_cam_compass([20, 20, 20], l0=1, r=8, oclock=3, pitch=90)

c.dump.read()

vel_mid = c.create_slicecontour_video(
    c.dump.vtm,
    c.dump.marker,
    normal="z",
    # origin=[None, None, None], # pass None to take midplane in the corresponding axis
    contour_color=lb.Color.field(lb.Field.vector("VEL", "mag"), clim=[0, 1.5]),
    # contour_color=lb.Color.field(lb.Field.scalar("P"), clim=[-0.5, 0.5]),
    # contour_color=lb.Color.field(lb.Field.vor_from_vel("VEL", "z"), clim=[-1, 1]),
    marker_color=lb.Color.uniform("white"),
    marker_opacity=1,
    marker_texture=lb.Texture.specular(),
    plotter_f=cam_f,
    keep_frames=False,
    out_name=f"vel_mid",
)

vor_mid = c.create_slicecontour_video(
    c.dump.vtm,
    c.dump.marker,
    normal="z",
    contour_color=lb.Color.field(lb.Field.vor_from_vel("VEL", "z"), clim=[-1, 1]),
    marker_color=lb.Color.uniform("white"),
    marker_opacity=1,
    marker_texture=lb.Texture.specular(),
    plotter_f=cam_f,
    keep_frames=False,
    out_name=f"vor_mid",
)

# compact post, same as isoq, all arguments except vtks and markers can be list for multiple render
vor_mid = c.create_slicecontour_video(
    c.dump.vtm,
    c.dump.marker,
    normal="z",
    contour_color=[
        lb.Color.field(lb.Field.vector("VEL", "mag"), clim=[0, 1.5]),
        lb.Color.field(lb.Field.vor_from_vel("VEL", "z"), clim=[-1, 1]),
    ],
    marker_color=lb.Color.uniform("white"),
    marker_opacity=1,
    marker_texture=lb.Texture.specular(),
    plotter_f=cam_f,
    keep_frames=False,
    out_name=[f"vel_mid", f"vor_mid"],
)

mpi.print_elapsed_time()
