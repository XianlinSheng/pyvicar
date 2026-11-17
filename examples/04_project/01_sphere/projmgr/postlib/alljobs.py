import pyvicar
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
import pyvicar.tools.matplotlib as pvmpl
import pyvicar.tools.fp as fp
import pyvicar.tools.post.dump.jobs as jobs
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf
from pyvicar.tools.post.dump.compact_post import compact_post
import numpy as np
import matplotlib.pyplot as plt
from .misc.pflib import make_post_pfs
from .misc.vecmath import rotate_plane, xyz2uv

pyvicar.assert_api_version("1.0.3", "1.1.0")

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())


mpi_async = False


class CalcWingPlane(jobs.PostJob):
    def __init__(self, p, p2):
        self.p = p
        self.p2 = p2

    def name(self):
        return f"calc_wing_plane"

    def global_begin(self, st):
        pass

    def global_end(self, st):
        pass

    def frame_begin(self, st):
        pass

    def frame_proc(self, st):
        p, p2 = self.p, self.p2

        xyz0 = p2.xyz_shdr[0, :]
        uxyz = [1, 0, 0]
        vxyz = [0, 1, 0]

        tstep = st.f["read"]["fields"].tstep
        flap_deg = p2.shdr_flap_deg[tstep, 1]
        aoa_deg = p2.shdr_aoa_deg[tstep, 1]
        sweep_deg = p2.shdr_sweep_deg[tstep, 1]

        pack = xyz0, uxyz, vxyz
        # flap
        flap_axis = uxyz
        pack = rotate_plane(*pack, xyz0, flap_axis, flap_deg)
        # aoa
        aoa_axis = vxyz
        pack = rotate_plane(*pack, xyz0, aoa_axis, aoa_deg)
        # sweep
        sweep_axis = np.cross(*pack[1:])
        pack = rotate_plane(*pack, xyz0, sweep_axis, sweep_deg)

        xyz0_t, uxyz_t, vxyz_t = pack

        st.f.set_outputs(
            self.name(),
            {
                "xyz0_t": xyz0_t,
                "uxyz_t": uxyz_t,
                "vxyz_t": vxyz_t,
            },
        )

    def frame_end(self, st):
        pass

    @staticmethod
    def eta_f(xyz, st):
        plane = st.f["calc_wing_plane"]
        xyz0_t, uxyz_t, vxyz_t = plane["xyz0_t"], plane["uxyz_t"], plane["vxyz_t"]

        uv = xyz2uv(
            uxyz_t[np.newaxis, :], vxyz_t[np.newaxis, :], xyz - xyz0_t[np.newaxis, :]
        )
        vmax = np.max(uv[:, 1])
        st.f.set_outputs("eta_f", {"vmax": vmax})
        return uv[:, 1] / vmax


class CalcEta(jobs.PostJob):
    def __init__(self, case):
        self.case = case

    def name(self):
        return f"calc_eta"

    def global_begin(self, st):
        self.case.report.read()
        st.g.set_outputs(self.name(), {"kin": self.case.report.ib2_wing_kin[1]})

    def global_end(self, st):
        pass

    def frame_begin(self, st):
        pass

    def frame_proc(self, st):
        tstep = st.f["read", "tstep"]
        pitch = st.g[self.name(), "kin"].shdr_aoa_deg[tstep, 1]
        sweep = st.f["sweep_density(read/bodies/point/CDP(SURF_UP))", (0,)]
        vmax = st.f["eta_f", "vmax"]
        eta = sweep["phi"]
        wid = sweep["measure"][1:-1] / vmax
        cdp = sweep["integral"][1:-1] / vmax
        cdpx = cdp * np.sin(np.radians(pitch))
        cdpz = cdp * np.cos(np.radians(pitch))
        st.f.set_outputs(
            self.name(),
            {
                "eta": eta,
                "wid": wid,
                "cdp": cdp,
                "cdpx": cdpx,
                "cdpz": cdpz,
            },
        )

    def frame_end(self, st):
        pass


class SaveReports(jobs.PostJob):
    def __init__(self, case):
        self.case = case

    def name(self):
        return f"save_reports"

    def global_begin(self, st):
        pass

    def global_end(self, st):
        c = self.case
        c.post.enable()
        c.post.reports.enable()

        wid = st.g["time_avg(eta_wid)", "v_avg"]
        cdp = st.g["time_avg(eta_cdp)", "v_avg"]
        cdpx = st.g["time_avg(eta_cdpx)", "v_avg"]
        cdpz = st.g["time_avg(eta_cdpz)", "v_avg"]
        eta = st.f["calc_eta", "eta"]

        fig = plt.figure()
        plt.plot(eta, wid, "k-")
        plt.axis([0, 1, 0, 1.5])
        plt.grid(True)
        plt.title("Time Avg Area Density (Chord)")
        plt.ylabel("darea / dv")
        plt.xlabel("eta = v / vmax")
        fig.tight_layout()
        report = c.post.reports.get_or_create("eta_wid_tavg")
        report.table_visual_by_matplotlib(fig)

        fig = plt.figure()
        plt.plot(eta, cdp, "k-", label="Mag")
        plt.plot(eta, cdpz, "r-", label="Lift")
        plt.plot(eta, cdpx, "b-", label="Drag")
        plt.axis([0, 1, -1.5, 1.5])
        plt.grid(True)
        plt.title("Time Avg CDP Density")
        plt.ylabel("dCDP / dv")
        plt.xlabel("eta = v / vmax")
        plt.legend()
        fig.tight_layout()
        report = c.post.reports.get_or_create("eta_cdp_tavg")
        report.table_visual_by_matplotlib(fig)

    def frame_begin(self, st):
        pass

    def frame_proc(self, st):
        pass

    def frame_end(self, st):
        pass


def post_alljobs(p):
    p2 = make_post_pfs(p)

    c = p.Case(p.name)

    c.read()

    st = compact_post(
        *make_data(p, p2, c),
        *make_eta(p, p2, c),
        *make_extracts(p, p2, c),
        *make_body_copies(p, p2, c),
        *make_bodyanim(p, p2, c),
        *make_isoq(p, p2, c),
        *make_slice(p, p2, c),
    )


def make_data(p, p2, c):
    mpath = jobs.ObjPath("read", "mesh")
    bpath = jobs.ObjPath("read", "bodies")
    bpath0 = jobs.ObjPath("read", "bodies", 0)

    return [
        jobs.Read(fields=c.dump.cgns, markers=c.dump.marker),
        # jobs.PrintFields("After read mesh", mesh=mpath),
        # jobs.PrintFields("After read body", mesh=bpath),
        jobs.Keep(mesh=jobs.ObjPath("read", "mesh"), cells=["VEL", "P"]),
        jobs.CalcNondimP("CP", vel0=p.U),  # , p0_xyz=p.gm.corners.reshape((-1, 3))),
        # PrintNondimP(),
        jobs.VolToSurf(
            {
                "cell_fields": ["CP"],
                "neg": True,
                "pos": True,
                "double": False,
            },
            mesh_vol=mpath,
            mesh_surf=bpath,
        ),
        jobs.CalcFunc(
            "CDP(SURF_UP)",
            ["CP(SURF_POS)", "CP(SURF_NEG)"],
            lambda pos, neg: neg - pos,
            mesh=bpath,
        ),
        jobs.Keep(mesh=jobs.ObjPath("read", "mesh"), cells=["VEL", "CP"]),
        jobs.ToPoints(mpath, keep=False),
        jobs.CalcNabla(field="VEL", grad=None, div=None, curl="VOR", q="Q"),
        jobs.CalcNondimVec("CVEL", vec_name="VEL", mag0=p.U),
        jobs.Keep(mesh=jobs.ObjPath("read", "mesh"), points=["CVEL", "CP", "VOR", "Q"]),
        # jobs.PrintFields("After calc mesh", mesh=mpath),
        # jobs.PrintFields("After calc body", mesh=bpath),
    ]


def make_eta(p, p2, c):
    bpath = jobs.ObjPath("read", "bodies")

    def wid_f(st):
        calc_eta = st.f.calc_eta
        eta = calc_eta["eta"]
        wid = calc_eta["wid"]
        fig = plt.figure()
        plt.plot(eta, wid, "k-")
        plt.axis([0, 1, 0, 1.5])
        plt.grid(True)
        plt.title("Area Density (Chord)")
        plt.ylabel("darea / dv")
        plt.xlabel("eta = v / vmax")
        fig.tight_layout()
        return fig

    def cdp_f(st):
        calc_eta = st.f.calc_eta
        eta = calc_eta["eta"]
        cdp = calc_eta["cdp"]
        cdpx = calc_eta["cdpx"]
        cdpz = calc_eta["cdpz"]
        fig = plt.figure()
        plt.plot(eta, cdp, "k-", label="Mag")
        plt.plot(eta, cdpz, "r-", label="Lift")
        plt.plot(eta, cdpx, "b-", label="Drag")
        plt.axis([0, 1, -2.5, 3.5])
        plt.grid(True)
        plt.title("CDP(SURF_ON) Density")
        plt.ylabel("dCDP / dv")
        plt.xlabel("eta = v / vmax")
        plt.legend()
        fig.tight_layout()
        return fig

    tmax = p2.ts[-1]
    tmin = tmax - p.T
    tclamp = {"tmin": tmin, "tmax": tmax}
    return [
        CalcWingPlane(p, p2),
        jobs.SweepDensity(
            CalcWingPlane.eta_f,
            mesh=bpath,
            point_field="CDP(SURF_UP)",
            phi_n=50,
        ),
        CalcEta(c),
        jobs.TimeAvg(c, "eta_wid", jobs.ObjPath("calc_eta", "wid"), **tclamp),
        jobs.TimeAvg(c, "eta_cdp", jobs.ObjPath("calc_eta", "cdp"), **tclamp),
        jobs.TimeAvg(c, "eta_cdpx", jobs.ObjPath("calc_eta", "cdpx"), **tclamp),
        jobs.TimeAvg(c, "eta_cdpz", jobs.ObjPath("calc_eta", "cdpz"), **tclamp),
        jobs.Matplotlib(c, "eta_wid", wid_f, keep_frames=False),
        jobs.Matplotlib(c, "eta_cdp", cdp_f, keep_frames=False),
        SaveReports(c),
    ]


def make_extracts(p, p2, c):
    return [
        jobs.IsoSurf(
            "isoq",
            mesh=jobs.ObjPath("read", "mesh"),
            iso_field="Q",
            iso_value=0.1,
        ),
        jobs.Slice(
            "wrst_y",
            mesh=jobs.ObjPath("read", "mesh"),
            normal="y",
            origin_f=p2.xyz_wrst_f,
        ),
        jobs.Slice(
            "wtip_y",
            mesh=jobs.ObjPath("read", "mesh"),
            normal="y",
            origin_f=p2.xyz_wtip_f,
        ),
        jobs.Slice(
            "ftip_y",
            mesh=jobs.ObjPath("read", "mesh"),
            normal="y",
            origin_f=p2.xyz_ftip_f,
        ),
        jobs.Clear(jobs.ObjPath("read", "mesh")),
    ]


def make_body_copies(p, p2, c):
    p.front_center = p.gm.center - [p.span, 0, 0]
    p.refl_center = p.gm.center - [0, p.span / 6, 0]
    p.front_refl_center = p.gm.center - [p.span, p.span / 6, 0]
    p.b4_center = p.gm.center - [p.span / 2, p.span / 6, 0]
    return [
        jobs.Translate(
            [-p.span, 0, 0],  # xyz vector
            mesh=jobs.ObjPath("read", "bodies"),
            copy=True,
            out_name="bcopy_front",
        ),
        jobs.Reflect(
            p.refl_center,  # reflect center xyz
            [0, 1, 0],  # reflect direction vector
            mesh=jobs.ObjPath("read", "bodies"),
            copy=True,
            out_name="bcopy_refl",
        ),
        jobs.Reflect(
            p.front_refl_center,  # reflect center xyz
            [0, 1, 0],  # reflect direction vector
            mesh=jobs.ObjPath("bcopy_front", "mesh"),
            copy=True,
            out_name="bcopy_front_refl",
        ),
    ]


def make_bodyanim(p, p2, c):
    plot_kwargs = {
        "add_axes": False,
        "show_grid": False,
    }
    center = p.gm.center + np.array([0, p.span / 4, 0])
    cam_common_kwargs = {
        "target": center,
        "l0": p.span,
        "downstream_shift": 0.5 * p.chord / p.span,
    }
    body_plain = {
        "mesh": jobs.ObjPath("read", "bodies"),
        "color": lb.Color.uniform("gray"),
    }
    angles = []
    for clock in [2, 5, 7, 10]:
        angles += [
            jobs.Plot(
                c,
                body_plain,
                plotter_f=fp.pipeline_f(
                    pf.set_cam_compass(
                        pitch=45,
                        oclock=clock,
                        r=4,
                        **cam_common_kwargs,
                    ),
                    *p2.area_fs,
                ),
                **plot_kwargs,
            ),
            jobs.SaveCaseAnim(c, f"body_o{clock}", keep_frames=False),
        ]

    top_cam_f = pf.set_cam_compass(
        pitch=90,
        oclock=3,
        r=8,
        **cam_common_kwargs,
    )

    angles += [
        jobs.Plot(
            c,
            body_plain,
            plotter_f=fp.pipeline_f(
                top_cam_f,
                *p2.area_fs,
            ),
            **plot_kwargs,
        ),
        jobs.SaveCaseAnim(c, f"body_top", keep_frames=False),
        jobs.Plot(
            c,
            {
                "mesh": jobs.ObjPath("read", "bodies"),
                "color": lb.Color.field(lb.Field.scalar("CDP(SURF_UP)"), clim=[-1, 1]),
            },
            plotter_f=fp.pipeline_f(
                top_cam_f,
                *p2.area_fs,
            ),
            **plot_kwargs,
        ),
        jobs.SaveCaseAnim(c, f"body_cdp_top", keep_frames=False),
    ]

    return angles


def make_isoq(p, p2, c):
    plot_kwargs = {
        "add_axes": False,
        "show_grid": False,
    }
    body_plain = {"mesh": jobs.ObjPath("read", "bodies")}
    isoq_cp = {
        "mesh": jobs.ObjPath("isoq", "mesh"),
        "color": lb.Color.field(
            lb.Field.scalar("CP"),
            clim=[-1, 1],
            cmap="viridis",
        ),
    }
    isoq_cv = {
        "mesh": jobs.ObjPath("isoq", "mesh"),
        "color": lb.Color.field(
            lb.Field.vector("CVEL", "y"),
            clim=[-1, 1],
            cmap="viridis",
        ),
    }

    center = p.gm.center + np.array([0, p.span / 2, 0])
    simples = []
    for clock in [2, 5, 7, 10]:
        cam_f = pf.set_cam_compass(
            target=center,
            l0=p.span,
            downstream_shift=1,
            r=5,
            oclock=clock,
            pitch=45,
        )
        simples += [
            jobs.Plot(c, body_plain, isoq_cp, plotter_f=cam_f, **plot_kwargs),
            jobs.SaveCaseAnim(c, f"q_cp_o{clock}", keep_frames=False),
            jobs.Plot(c, body_plain, isoq_cv, plotter_f=cam_f, **plot_kwargs),
            jobs.SaveCaseAnim(c, f"q_cv_o{clock}", keep_frames=False),
        ]

    cam_f = pf.set_cam_compass(
        target=center,
        l0=p.span,
        downstream_shift=0.8,
        r=8,
        oclock=3,
        pitch=90,
    )
    simples += [
        jobs.Plot(c, body_plain, isoq_cp, plotter_f=cam_f, **plot_kwargs),
        jobs.SaveCaseAnim(c, "q_cp_top", keep_frames=False),
        jobs.Plot(c, body_plain, isoq_cv, plotter_f=cam_f, **plot_kwargs),
        jobs.SaveCaseAnim(c, "q_cv_top", keep_frames=False),
    ]

    cam_f = pf.set_cam_compass(
        pitch=-60,
        oclock=7,
        r=4,
        target=center,
        l0=p.span,
        downstream_shift=0.5 * p.chord / p.span,
    )
    simples += [
        jobs.Plot(c, body_plain, isoq_cp, plotter_f=cam_f, **plot_kwargs),
        jobs.SaveCaseAnim(c, "q_cp_o7_bel", keep_frames=False),
        jobs.Plot(c, body_plain, isoq_cv, plotter_f=cam_f, **plot_kwargs),
        jobs.SaveCaseAnim(c, "q_cv_o7_bel", keep_frames=False),
    ]

    duplicates = []
    for clock in [2, 5, 7, 10]:
        cam_f = pf.set_cam_compass(
            target=p.refl_center,
            l0=p.span,
            downstream_shift=0.5,
            r=6,
            oclock=clock,
            pitch=45,
        )
        body_cdp = {
            "mesh": jobs.ObjPath("bcopy_refl", "mesh"),
            "color": lb.Color.field(lb.Field.scalar("CDP(SURF_UP)"), clim=[-1, 1]),
        }
        duplicates += [
            jobs.Plot(c, body_plain, isoq_cp, body_cdp, plotter_f=cam_f, **plot_kwargs),
            jobs.SaveCaseAnim(c, f"qdup_cp_o{clock}", keep_frames=False),
            jobs.Plot(c, body_plain, isoq_cv, body_cdp, plotter_f=cam_f, **plot_kwargs),
            jobs.SaveCaseAnim(c, f"qdup_cv_o{clock}", keep_frames=False),
        ]

    return [
        *simples,
        *duplicates,
    ]


def make_slice(p, p2, c):
    plot_kwargs = {
        "add_axes": False,
        "show_grid": False,
    }
    cam_f = pf.set_cam_compass(p.gm.center, l0=p.span, r=3, oclock=3, pitch=0)
    body_plain = {
        "mesh": jobs.ObjPath("read", "bodies"),
        "opacity": 0.5,
    }
    slices = []
    for pos in ["wrst", "wtip", "ftip"]:
        spath = jobs.ObjPath(f"{pos}_y", "mesh")
        slices += [
            jobs.Plot(
                c,
                {
                    "mesh": spath,
                    "color": lb.Color.field(
                        lb.Field.vector("VOR", "y"), clim=[-0.1, 0.1]
                    ),
                },
                body_plain,
                plotter_f=cam_f,
                **plot_kwargs,
            ),
            jobs.SaveCaseAnim(c, f"{pos}_vor", keep_frames=False),
            jobs.Plot(
                c,
                {
                    "mesh": spath,
                    "color": lb.Color.field(
                        lb.Field.vector("CVEL", "mag"), clim=[0, 1.5]
                    ),
                },
                body_plain,
                plotter_f=cam_f,
                **plot_kwargs,
            ),
            jobs.SaveCaseAnim(c, f"{pos}_cvel", keep_frames=False),
            jobs.Plot(
                c,
                {
                    "mesh": spath,
                    "color": lb.Color.field(lb.Field.scalar("CP"), clim=[-1, 1]),
                },
                body_plain,
                plotter_f=cam_f,
                **plot_kwargs,
            ),
            jobs.SaveCaseAnim(c, f"{pos}_cp", keep_frames=False),
        ]

    return slices
