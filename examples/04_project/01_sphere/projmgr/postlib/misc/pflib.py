import pyvicar
import pyvicar.tools.fp as fp
import pyvicar.tools.post.dump as dump
import pyvicar.tools.post.dump.plotter_fs as pf
import pyvicar.tools.post.dump.labels as lb
from pyvicar.tools.collections import struct
import numpy as np

pyvicar.assert_api_version("1.0.3", "1.1.0")


def make_vlist_f(time_f, ts, vlist):
    def vlist_f(c, i, v, m):
        t = time_f(c, i, v, m)
        return np.array([np.interp(t, ts, vlist[:, i]) for i in range(vlist.shape[1])])

    return vlist_f


def get_xyz(report, prefix):
    x = getattr(report, f"{prefix}_x").value
    y = getattr(report, f"{prefix}_y").value
    z = getattr(report, f"{prefix}_z").value
    return np.hstack((x, y, z))


def glyph_f(plotter, c, i, v, m):
    bodies = m.to_pyvista_multiblocks()
    color = lb.Color.field(lb.Field.scalar("P"))
    for body in bodies:
        body = body.cell_data_to_point_data(pass_cell_data=False)
        glyphs = body.glyph(orient="NORM", scale="P", factor=1)
        plotter.add_mesh(glyphs, **color.add_mesh_kwargs())
    return plotter


def diff(xyz, ts):
    uvw = np.zeros_like(xyz)
    uvw[1:-1, :] = (xyz[2:, :] - xyz[:-2, :]) / (
        ts[2:, np.newaxis] - ts[:-2, np.newaxis]
    )
    return uvw


def calc_inflow(vxyz, U):
    return -vxyz + np.array([U, 0, 0])[np.newaxis, :]


def make_post_pfs(p):
    c = p.Case(p.name)

    p2 = struct()

    c.report.read()

    ib2report = c.report.ib2_wing_kin[1]

    p2.positions = [
        "shdr",
        "elbw",
        "wrst",
        "wtip",
        "ftip",
        "wf1",
        "wf2",
        "wf3",
        "ww2",
        "ew2",
        "se2",
    ]

    p2.ts = ib2report.time.ravel()
    for pos in p2.positions[:5]:
        setattr(p2, f"xyz_{pos}", get_xyz(ib2report, pos))
        setattr(p2, f"xyz_{pos}_lead", get_xyz(ib2report, f"{pos}_lead"))
        setattr(p2, f"xyz_{pos}_trail", get_xyz(ib2report, f"{pos}_trail"))

    p2.xyz_wf1 = p2.xyz_wtip * 0.75 + p2.xyz_ftip * 0.25
    p2.xyz_wf2 = p2.xyz_wtip * 0.50 + p2.xyz_ftip * 0.50
    p2.xyz_wf3 = p2.xyz_wtip * 0.25 + p2.xyz_ftip * 0.75
    p2.xyz_ww2 = p2.xyz_wrst * 0.50 + p2.xyz_wtip * 0.50
    p2.xyz_ew2 = p2.xyz_elbw * 0.50 + p2.xyz_wrst * 0.50
    p2.xyz_se2 = p2.xyz_shdr * 0.50 + p2.xyz_elbw * 0.50

    p2.xyz_wf1_lead = p2.xyz_wtip_lead * 0.75 + p2.xyz_ftip_lead * 0.25
    p2.xyz_wf2_lead = p2.xyz_wtip_lead * 0.50 + p2.xyz_ftip_lead * 0.50
    p2.xyz_wf3_lead = p2.xyz_wtip_lead * 0.25 + p2.xyz_ftip_lead * 0.75
    p2.xyz_ww2_lead = p2.xyz_wrst_lead * 0.50 + p2.xyz_wtip_lead * 0.50
    p2.xyz_ew2_lead = p2.xyz_elbw_lead * 0.50 + p2.xyz_wrst_lead * 0.50
    p2.xyz_se2_lead = p2.xyz_shdr_lead * 0.50 + p2.xyz_elbw_lead * 0.50

    p2.xyz_wf1_trail = p2.xyz_wtip_trail * 0.75 + p2.xyz_ftip_trail * 0.25
    p2.xyz_wf2_trail = p2.xyz_wtip_trail * 0.50 + p2.xyz_ftip_trail * 0.50
    p2.xyz_wf3_trail = p2.xyz_wtip_trail * 0.25 + p2.xyz_ftip_trail * 0.75
    p2.xyz_ww2_trail = p2.xyz_wrst_trail * 0.50 + p2.xyz_wtip_trail * 0.50
    p2.xyz_ew2_trail = p2.xyz_elbw_trail * 0.50 + p2.xyz_wrst_trail * 0.50
    p2.xyz_se2_trail = p2.xyz_shdr_trail * 0.50 + p2.xyz_elbw_trail * 0.50

    for pos in p2.positions:
        xyz_lead = getattr(p2, f"xyz_{pos}_lead")
        xyz_trail = getattr(p2, f"xyz_{pos}_trail")
        vxyz_lead = diff(xyz_lead, p2.ts)
        vxyz_trail = diff(xyz_trail, p2.ts)
        inflow = calc_inflow(vxyz_lead, p.U)
        outflow = calc_inflow(vxyz_trail, p.U)
        dx = xyz_trail[:, 0] - xyz_lead[:, 0]
        dz = xyz_trail[:, 2] - xyz_lead[:, 2]
        gaoa = -np.degrees(np.arctan2(dz, dx))
        effaoa = gaoa + np.degrees(np.arctan2(inflow[:, 2], inflow[:, 0]))
        setattr(p2, f"inflow_{pos}", inflow)
        setattr(p2, f"outflow_{pos}", outflow)
        setattr(p2, f"gaoa_{pos}", gaoa)
        setattr(p2, f"effaoa_{pos}", effaoa)

    def time_f(c, i, v, m):
        if v is not None:
            return p2.ts[v.tstep - 1]
        else:
            return p2.ts[m.tstep - 1]

    p2.time_f = time_f

    for pos in p2.positions:
        xyz = getattr(p2, f"xyz_{pos}")
        setattr(p2, f"xyz_{pos}_f", make_vlist_f(p2.time_f, p2.ts, xyz))
        xyz_lead = getattr(p2, f"xyz_{pos}_lead")
        setattr(p2, f"xyz_{pos}_lead_f", make_vlist_f(p2.time_f, p2.ts, xyz_lead))
        xyz_trail = getattr(p2, f"xyz_{pos}_trail")
        setattr(p2, f"xyz_{pos}_trail_f", make_vlist_f(p2.time_f, p2.ts, xyz_trail))
        inflow = getattr(p2, f"inflow_{pos}")
        setattr(p2, f"inflow_{pos}_f", make_vlist_f(p2.time_f, p2.ts, inflow))

    def clear_xz_f(xyz, *args, **kwargs):
        return [p.gm.center[0], xyz[1], p.gm.center[2]]

    p2.clear_xz_f = clear_xz_f

    for pos in p2.positions:
        xyz_f = getattr(p2, f"xyz_{pos}_f")
        setattr(p2, f"xyz_{pos}_y_f", fp.send_pipe_f(xyz_f, [p2.clear_xz_f]))

    p2.shdr_flap_deg = ib2report.shdr_flap_deg
    p2.shdr_aoa_deg = ib2report.shdr_aoa_deg
    p2.shdr_sweep_deg = ib2report.shdr_sweep_deg

    p2.cube_a_f = fp.uniform_f([p.chord / 20] * 3)
    p2.plane_normal_f = fp.uniform_f("y")

    p2.plane_fs = [
        pf.make_plane_plotter_f(p2.xyz_elbw_y_f, p2.plane_normal_f, color="red"),
        pf.make_plane_plotter_f(p2.xyz_wrst_y_f, p2.plane_normal_f, color="green"),
        pf.make_plane_plotter_f(p2.xyz_wtip_y_f, p2.plane_normal_f, color="blue"),
    ]

    p2.cube_lead_fs = []
    p2.cube_tral_fs = []
    p2.cube_skel_fs = []
    p2.arrow_fs = []
    for n, c in zip(
        p2.positions[1:],
        ["red", "green", "blue", "magenta"] + ["black"] * 6,
    ):
        xyz_f = getattr(p2, f"xyz_{n}_f")
        xyz_lead_f = getattr(p2, f"xyz_{n}_lead_f")
        xyz_trail_f = getattr(p2, f"xyz_{n}_trail_f")
        p2.cube_skel_fs.append(pf.make_cube_plotter_f(xyz_f, p2.cube_a_f, c))
        p2.cube_lead_fs.append(pf.make_cube_plotter_f(xyz_lead_f, p2.cube_a_f, c))
        p2.cube_tral_fs.append(pf.make_cube_plotter_f(xyz_trail_f, p2.cube_a_f, c))
        inflow_f = getattr(p2, f"inflow_{n}_f")
        p2.arrow_fs.append(
            pf.make_arrow_plotter_f(xyz_lead_f, inflow_f, color=c, scale=0.5)
        )

    p2.polyline_skel_fs = [
        pf.make_polyline_plotter_f(
            (p2.xyz_shdr_f, p2.xyz_elbw_f, p2.xyz_wrst_f, p2.xyz_wtip_f, p2.xyz_ftip_f),
            "black",
            line_width=10,
        )
    ]
    p2.polyline_lead_fs = [
        pf.make_polyline_plotter_f(
            (
                p2.xyz_shdr_lead_f,
                p2.xyz_elbw_lead_f,
                p2.xyz_wrst_lead_f,
                p2.xyz_wtip_lead_f,
                p2.xyz_ftip_lead_f,
            ),
            "black",
            line_width=10,
        )
    ]
    p2.polyline_tral_fs = [
        pf.make_polyline_plotter_f(
            (
                p2.xyz_shdr_trail_f,
                p2.xyz_elbw_trail_f,
                p2.xyz_wrst_trail_f,
                p2.xyz_wtip_trail_f,
                p2.xyz_ftip_trail_f,
            ),
            "black",
            line_width=10,
        ),
    ]
    p2.area_fs = [
        pf.make_polyline_plotter_f(
            (
                p2.xyz_shdr_lead_f,
                p2.xyz_elbw_lead_f,
                p2.xyz_wrst_lead_f,
                p2.xyz_wtip_lead_f,
                p2.xyz_ftip_lead_f,
                p2.xyz_ftip_trail_f,
                p2.xyz_wtip_trail_f,
                p2.xyz_wrst_trail_f,
                p2.xyz_elbw_trail_f,
                p2.xyz_shdr_trail_f,
                p2.xyz_shdr_lead_f,
            ),
            "black",
            line_width=10,
        ),
        pf.make_cube_plotter_f(p2.xyz_shdr_lead_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_elbw_lead_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_wrst_lead_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_wtip_lead_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_ftip_lead_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_shdr_trail_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_elbw_trail_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_wrst_trail_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_wtip_trail_f, p2.cube_a_f),
        pf.make_cube_plotter_f(p2.xyz_ftip_trail_f, p2.cube_a_f),
    ]

    def create_curve_fs(name, color):
        setattr(
            p2,
            f"{name}_curve_fs",
            [
                pf.make_curve_plotter_f(
                    fp.uniform_f(getattr(p2, f"xyz_{name}")), color
                ),
            ],
        )

    for n, c in zip(
        p2.positions[1:],
        ["red", "green", "blue", "magenta"] + ["black"] * 6,
    ):
        create_curve_fs(n, c)

    p2.isoq_fs = (
        p2.polyline_skel_fs
        + p2.cube_skel_fs
        # + p2.plane_fs
        # + p2.arrow_fs
        # + p2.elbw_curve_fs
        # + p2.wrst_curve_fs
        # + p2.wtip_curve_fs
        # + p2.ftip_curve_fs
    )

    p2.mirror_center = p.gm.center - np.array([0, p.span / 6, 0])

    def mirror_wing_f(plotter, c, i, v, m):
        body = m.to_pyvista_multiblocks()[0]
        dump.calc_surf_data(body)
        # choose to mirror or simply copy and translate
        mirrored = body.reflect((0, 1, 0), point=p2.mirror_center)
        dp = lb.Field.compute_scalar(
            "DP", ["P(SURF_POS)", "P(SURF_NEG)"], lambda pos, neg: neg - pos
        )
        plotter.add_mesh(
            dump.prep_field(mirrored, dp),
            **lb.Color.field(dp, clim=[-0.5, 1]).add_mesh_kwargs(),
            **lb.Texture.specular().add_mesh_kwargs(),
        )
        return plotter

    p2.mirror_wing_f = mirror_wing_f

    def create_contour_fs(name):
        setattr(
            p2,
            f"{name}_contour_fs",
            p2.polyline_skel_fs
            + p2.cube_skel_fs,  # + getattr(p2, f"{name}_curve_fs") + p2.arrow_fs,
        )

    for n in p2.positions[1:]:
        create_contour_fs(n)

    return p2
