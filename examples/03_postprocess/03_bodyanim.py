import pyvicar
import pyvicar.tools.mpi as mpi
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf

# 3. bodyanim
# this script reads the case marker files and generate animation of body surface

# use at least v1.0.2 if only for postprocess because in lower version
# instantiating Case(...) alone would truncate existing input files
pyvicar.assert_api_version("1.0.2", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

# change this to a completed 3d case in 01_geometry, like tut_sphere here
c = Case("tut_sphere")

c.dump.read()

# for 2d cases, change it to [20, 20, dz/2], dz/2 is small can be 0
center = [20, 20, 20]

# bodyanim args are basically the isoq ones
# without iso-related and show_outline since vtk field is not read
a2 = c.create_bodyanim_video(
    c.dump.marker,
    marker_color=lb.Color.uniform("white"),
    marker_texture=lb.Texture.specular(),
    plotter_f=pf.set_cam_compass(center, l0=1, r=8, oclock=2),
    keep_frames=True,
    out_name="body_o2",
)

a10 = c.create_bodyanim_video(
    c.dump.marker,
    marker_color=lb.Color.uniform("white"),
    marker_texture=lb.Texture.specular(),
    plotter_f=pf.set_cam_compass(center, l0=1, r=8, oclock=10),
    keep_frames=True,
    out_name="body_o10",
)


mpi.print_elapsed_time()
