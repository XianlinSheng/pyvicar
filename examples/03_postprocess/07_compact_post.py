import pyvicar
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
import pyvicar.tools.post.dump.jobs as jobs
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf
from pyvicar.tools.post.dump.compact_post import compact_post
import numpy as np

# 7. compact post
# compact post can read in the files only once and produce all neede frames
# (which is the normal procedure in software)

# if calling multiple create_xxx_video functions repeatedly:
# isoq angle 1: [read -> isoq -> angle 1 -> frame 1 -> video isoq1]
# isoq angle 2: [read -> isoq -> angle 2 -> frame 2 -> video isoq2]
# body angle 1: [read -> body -> angle 1 -> frame 1 -> video body1]
# body angle 2: [read -> body -> angle 2 -> frame 2 -> video body2]
# file io and common data filter are processed repeatedly

# compact post is to transpose this array traverse:
# isoq angle 1: [read |  isoq |  angle 1 |  frame 1 |  video isoq1 | ]
# isoq angle 2: [read |  isoq |  angle 2 |  frame 2 |  video isoq2 | ]
# body angle 1: [read |  body |  angle 1 |  frame 1 |  video body1 | ]
# body angle 2: [read |/ body |/ angle 2 |/ frame 2 |/ video body2 |/]
# the heaviest read and isoq steps are needed only once and is merged

# each job can define these functions that fit in the overall pipeline:
# global_begin for all_jobs
# for frame in frames:
#     frame_begin for all_jobs
#     frame_proc for all_jobs
#     frame_end for all_jobs
# global_end for all_jobs

pyvicar.assert_api_version("1.0.3", "1.1.0")  # compact post is 1.0.3 feature

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

c = Case("tut_sphere")

c.read()

U = 1
center = [20, 20, 20]
isoq_cam_f = pf.set_cam_compass(center, l0=1, r=10, oclock=2)
midy_cam_f = pf.set_cam_compass(center, l0=1, r=8, oclock=3, pitch=0)


# add job objects to compact_post args, each job may write data in the internal status space
# this status space will eventually be returned to the 'st' below
# st.g -> global status, st.f -> frame status
# st.g|f.jobname -> job output dict
# st.g|f[jobname], same as st.g|f.jobname
# st.g|f.jobname[objname] -> an output obj of job
# st.g|f[jobs.ObjPath(jobname, objname)], same as st.g|f.jobname[objname]


# one can also define customized jobs in the pipeline
class PrintFields(jobs.PostJob):
    def __init__(self, header):
        self.header = header

    def name(self):
        return f"echo_fields({self.header})"

    def global_begin(self, st):
        pass

    def global_end(self, st):
        pass

    def frame_begin(self, st):
        pass

    def frame_proc(self, st):
        print(f"{self.header}: {st.f.read["mesh"].cell_data.keys() = }")
        print(f"{self.header}: {st.f.read["mesh"].point_data.keys() = }")
        print(f"{self.header}: {st.f.read["bodies"][0].cell_data.keys() = }")
        print(f"{self.header}: {st.f.read["bodies"][0].point_data.keys() = }")

    def frame_end(self, st):
        pass


st = compact_post(
    jobs.Read(
        # read the dump files, frames aligned
        # store f/read/fields: fields dump handle, /marker: marker dump handle
        #             /mesh: fields_combined_mesh, /bodies: bodies_multiblock_mesh
        fields=c.dump.cgns,  # remove if no need to read
        markers=c.dump.marker,  # remove if no need to read
    ),
    PrintFields("after read"),
    jobs.Keep(mesh=jobs.ObjPath("read", "mesh"), cells=["VEL", "P"]),
    PrintFields("after keep"),
    jobs.VolToSurf(
        # interpolate vol cell fields to surf point field, can specify which side to use the vol data
        # needs vol cell fields so must be used before ToPoints keep=False (default), or specify keep=True
        # modifies surf mesh inplace, add XX(SURF_NEG) XX(SURF_POS) XX(SURF) for all cell fields XX
        mesh_vol=jobs.ObjPath("read", "mesh"),
        mesh_surf=jobs.ObjPath("read", "bodies"),
        neg=True,  # use data on negative normal side, create XX(SURF_NEG), default False if removed
        pos=False,  # ... positive side, ... XX(SURF_POS), default False
        double=False,  # ... both sides, use when vol continuous across surf, ... XX(SURF), default False
    ),
    PrintFields("after vol_to_surf"),
    # CalcXXX works on point field, surf interp comes from vol cell field
    jobs.CalcNondimP(
        "CP(SURF_NEG)",
        mesh=jobs.ObjPath("read", "bodies"),
        p_name="P(SURF_NEG)",
        vel0=U,
    ),
    PrintFields("after calc_nondim_p"),
    jobs.Translate(
        # translate a mesh, can be done either inplace or create a new mesh
        # store f/out_name/mesh: output mesh, if copy=True
        [0, -2, 0],  # xyz vector
        mesh=jobs.ObjPath("read", "bodies"),  # input
        copy=True,  # dont change the input, create a new mesh
        out_name="bodies_trans",  # valid when copy=True
    ),
    jobs.Reflect(
        # reflect a mesh, can be done either inplace or create a new mesh
        # store f/out_name/mesh: output mesh, if copy=True
        [20, 21, 20],  # reflect center xyz
        [0, 1, 0],  # reflect direction vector
        mesh=jobs.ObjPath("read", "bodies"),
        copy=True,
        out_name="bodies_refl",
    ),
    jobs.Rotate(
        # rotate a mesh, can be done either inplace or create a new mesh
        # store f/out_name/mesh: output mesh, if copy=True
        [19, 20, 20],  # rotation center xyz
        [0, 0, 1],  # rotation axis vector
        90,  # rotation angle deg
        mesh=jobs.ObjPath("read", "bodies"),
        copy=True,
        out_name="bodies_rot",
    ),
    jobs.ToPoints(jobs.ObjPath("read", "mesh"), keep=False),
    PrintFields("after to_points"),
    # these CalcXXX default mesh=jobs.ObjPath("read", "mesh") and output inplace
    jobs.CalcNondimVec("CVEL", vec_name="VEL", vec0=U),
    # CalcNabla computes GRAD DIV VOR Q in one run faster, can replace multiple calls
    jobs.CalcNabla(field="CVEL", grad=None, div=None, curl="CVOR", q="Q"),
    # jobs.CalcVor("VOR", vel_name="VEL"),
    # jobs.CalcNondimVec("CVOR", vec_name="VOR", vec0=U),
    # jobs.CalcQ("Q", vel_name="CVEL"),
    jobs.CalcNondimP("CP", vel0=U),
    jobs.CalcFunc("WXU", ["CVOR", "CVEL"], lambda w, u: np.cross(w, u, axis=-1)),
    PrintFields("after all calc_xxx"),
    jobs.IsoSurf(
        # create iso surface mesh
        # store f/first_arg/mesh: iso surface mesh
        "isoq",
        mesh=jobs.ObjPath("read", "mesh"),
        iso_field="Q",
        iso_value=0.1,
    ),
    jobs.Plot(
        c,
        # one dict is one mesh to render,
        # these are only labels so one can also generate a list of dict outside and expand here
        {"mesh": jobs.ObjPath("read", "bodies")},
        {
            "mesh": jobs.ObjPath("bodies_trans", "mesh"),
            "color": lb.Color.field(lb.Field.scalar("CP(SURF_NEG)"), clim=[-1, 1]),
        },
        {
            "mesh": jobs.ObjPath("bodies_refl", "mesh"),
            "color": lb.Color.field(lb.Field.scalar("CP(SURF_NEG)"), clim=[-1, 1]),
        },
        {
            "mesh": jobs.ObjPath("bodies_rot", "mesh"),
            "color": lb.Color.field(lb.Field.scalar("CP(SURF_NEG)"), clim=[-1, 1]),
        },
        {
            "mesh": jobs.ObjPath("isoq", "mesh"),
            "color": lb.Color.field(lb.Field.scalar("CP"), clim=[-1, 1]),
        },
        plotter_f=isoq_cam_f,
    ),
    # generate a frame for the recent Plot (render f/plot/plotter)
    jobs.SaveCaseAnim(c, "isoq_bodies", keep_frames=False),
    # one can remove a job output early to save some memory, if no longer used
    jobs.Clear("isoq", "bodies_trans", "bodies_refl", "bodies_rot"),
    jobs.Plot(
        c,
        {
            "mesh": jobs.ObjPath("read", "bodies"),
            # defualt uniform white, so one can simply remove this line in that case
            "color": lb.Color.field(lb.Field.scalar("CP(SURF_NEG)"), clim=[-1, 1]),
        },
        plotter_f=isoq_cam_f,
    ),
    jobs.SaveCaseAnim(c, "body", keep_frames=False),
    jobs.Slice("midy", mesh=jobs.ObjPath("read", "mesh"), normal="y"),
    jobs.Plot(
        c,
        {
            "mesh": jobs.ObjPath("midy", "mesh"),
            "color": lb.Color.field(lb.Field.vector("CVOR", "y"), clim=[-0.1, 0.1]),
        },
        {"mesh": jobs.ObjPath("read", "bodies")},
        plotter_f=midy_cam_f,
    ),
    jobs.SaveCaseAnim(c, "midy_cvor", keep_frames=False),
    jobs.Plot(
        c,
        {
            "mesh": jobs.ObjPath("midy", "mesh"),
            "color": lb.Color.field(lb.Field.vector("CVEL", "mag"), clim=[0, 1.5]),
        },
        {"mesh": jobs.ObjPath("read", "bodies")},
        plotter_f=midy_cam_f,
    ),
    jobs.SaveCaseAnim(c, "midy_cvel", keep_frames=False),
    jobs.Plot(
        c,
        {
            "mesh": jobs.ObjPath("midy", "mesh"),
            "color": lb.Color.field(lb.Field.scalar("CP"), clim=[-1, 1]),
        },
        {"mesh": jobs.ObjPath("read", "bodies")},
        plotter_f=midy_cam_f,
    ),
    jobs.SaveCaseAnim(c, "midy_cp", keep_frames=False),
)

# this is generally used to checkout total processing time
mpi.print_elapsed_time()
