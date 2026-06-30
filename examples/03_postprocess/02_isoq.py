import pyvicar
import pyvicar.tools.mpi as mpi
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf

# 2. isoq
# this script reads the case vtk dump and generate a quick animation of Q criterion iso surfaces

# use at least v1.0.2 if only for postprocess because in lower version
# instantiating Case(...) alone would truncate existing input files
pyvicar.assert_api_version("1.0.3", "1.1.0")  # compact post is 1.0.3 feature

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

c = Case("tut_sphere")

c.dump.read()

# this is the typical center generated in the 3d geometry tutorial so will work on all 3d cases
# for 2d cases, change it to [20, 20, dz/2], dz/2 is small can be 0
# see the 04_project section to see how to manage these data in detail
center = [20, 20, 20]

# set l0 to the case length scale. 3d tutorials are 1 so this will work well on all of them
a2 = c.create_isoq_video(
    c.dump.vtm,
    c.dump.marker,
    plotter_f=pf.set_cam_compass(center, r=8, l0=1),  # the default values are below
    # plotter_f=set_cam_compass(center, l0=1, r=3, oclock=2, pitch=30, downstream_shift=1),
    # iso_color=lb.Color.field(lb.Field.vector("VEL", "z"), clim=[-0.5, 0.5]),
    # iso_color=lb.Color.field(lb.Field.vector("VEL", "mag"), clim=[0, 1.5]),
    iso_color=lb.Color.field(lb.Field.scalar("P"), clim=[-0.5, 0.5]),
    keep_frames=True,
    # resolution="4k",
    out_name="q_p_o2",
)

# or change a view angle if you want
a10 = c.create_isoq_video(
    c.dump.vtm,
    c.dump.marker,
    plotter_f=pf.set_cam_compass(center, l0=1, r=8, oclock=10),
    iso_color=lb.Color.field(lb.Field.scalar("P"), clim=[-0.5, 0.5]),
    keep_frames=True,
    out_name="q_p_o10",
)

# better rendered
a2t = c.create_isoq_video(
    c.dump.vtm,
    c.dump.marker,
    plotter_f=pf.set_cam_compass(center, l0=1, r=8, oclock=2),
    iso_color=lb.Color.field(lb.Field.scalar("P"), clim=[-0.5, 0.5]),
    marker_color=lb.Color.uniform("white"),
    iso_texture=lb.Texture.specular(),  # default will work just fine
    marker_texture=lb.Texture.specular(),
    iso_opacity=0.9,
    show_outline=False,
    add_axes=False,
    show_grid=False,
    # anti_alising is default off, turning on sometimes creates render issues on complex iso surface topologies
    # simply remove this line for a stable rendering
    enable_anti_aliasing=True,
    keep_frames=False,
    out_name="q_p_o2_textured",
)

# compact post, reduce repeated file io and partition topology cleanup
# specify a list for out_name to render multiple configs in one read,
# most of the arguments (except vtks, markers, q_name, iso_value, surf_interp, surf_interp_radius)
# are supported and can be their corresponding lists
# the larger dump files are, the more significant this can reduce the io and cleanup overhead
# e.g., 4 view angles need 4T if posted separately, but compact post needs likely only 150%T
# simply specify regular non-list if its unchanged across all variations
a_all = c.create_isoq_video(
    c.dump.vtm,
    c.dump.marker,
    plotter_f=[
        pf.set_cam_compass(center, l0=1, r=8, oclock=3),
        pf.set_cam_compass(center, l0=1, r=8, oclock=9),
    ],
    iso_color=[
        lb.Color.field(lb.Field.scalar("P"), clim=[-0.5, 0.5]),
        lb.Color.field(lb.Field.vector("VEL", "mag"), clim=[0, 1.5]),
    ],
    marker_color=lb.Color.uniform("white"),
    iso_texture=lb.Texture.specular(),
    marker_texture=lb.Texture.specular(),
    iso_opacity=0.9,
    show_outline=False,
    add_axes=False,
    show_grid=False,
    keep_frames=False,
    out_name=["q_p_o3", "q_vel_o9"],
)

# this is generally used to checkout total processing time
mpi.print_elapsed_time()

# mpi is not needed to be imported, get_isoq_video has mpi support internally,
# simply mpirun -np x python xxx.py will

# c.dump.vtm is what the solver dumps, use c.dump.vtr/vtk if one has compressed (example 4)
# c.dump.marker is optional, it will not plot bodies if not specified or not exists
# plotter_f is a plotter setter, using default iso view angle if not specified,
#           set_cam_compass generates a plotter setter that calculates cam position using compass direction,
#           set_cam_compass(target, l0=..., r=..., oclock=..., pitch=..., downstream_shift=...)
#                       target: the position of object, if using GridModel, can be gm.center
#                       l0: the length scale of object, default 1
#                       r: distance between cam and target (radius of compass), default 4x l0
#                       oclock: cam direction on compass, x+ downstream is 12 o'clock, default cam at 2
#                       pitch: pitch degree of camera above xy plane, default at 30deg
#                       downstream_shift: shift focus to downstream for more view space in wake, default 1x l0
#           the default values are the best view angle for flow past sphere with l0=diameter
# iso_color is the surface coloring option, default is to color by VEL magnitude if not specified.
#           Color is the base class of coloring style tag (derived class),
#           .field(...) factory creates a ColorField tag that tells the function to color by field.
#           Field is the base class of field type tag (derived class),
#           .vector(...) factory creates a FieldVector tag that tells the function to use vector field's component to color.
#           "VEL" is the field name to use, "z"/"mag" is the component, default mag if not specified
#           clim=[l,h] sets the colorbar limits, default None for auto scale at every frame
#           clim is recommended to set explicitly since auto scale has no global knowledge and it changes thru time
# keep_frames will keep the generated frame images, set to False to keep only the mp4, default True
# resolution is the output frame size, accpet [w, h], or single w int for square, or string in 'hd720', 'hd1080', '4k', '8k',
#            default '4k', note that fontsize needs to be changed accordingly if changing frame size
# out_name is the frames and animation name, output to Post/Animations.
#          file structure is in pyvicar post standard, readable and manageable with other post results
