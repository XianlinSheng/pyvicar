import pyvicar

pyvicar.assert_api_version("1.0.2", "1.1.0")

import pyvicar.tools.matplotlib as pvmpl
from pyvicar.tools.post.time import TFilter, stat
import numpy as np
import matplotlib.pyplot as plt
from .misc.pflib import get_xyz, diff, calc_inflow

mpi_async = True

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())


def post_kin(p):
    c = p.Case(p.name)
    c.draglift.read()
    c.report.read()
    kin = c.report.ib2_wing_kin[1]

    # ===== prescribed kin plot ===== #

    fig = plt.figure()
    ax = fig.add_subplot()

    time = kin.time.ravel() / p.T
    ax.plot(time, kin.shdr_flap_deg.ravel(), label="Flap")
    ax.plot(time, kin.shdr_aoa_deg.ravel(), label="Pitch")
    ax.plot(time, kin.wrst_sweep_deg.ravel(), label="Wrist Sweep")
    ax.plot(time, kin.wrst_flex_deg.ravel(), label="Wrist Flex")

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time / T")
    ax.set_ylabel("Deg")
    ax.set_title("Kinematics")
    fig.tight_layout()

    c.create_matplotlib_fig(fig, "kin")

    # ===== eff aoa plot, series, stat  ===== #

    fig = plt.figure()
    ax = fig.add_subplot()

    pitch = kin.shdr_aoa_deg.ravel()

    def make_eff_aoa(pos):
        xyz_lead = get_xyz(kin, f"{pos}_lead")
        vxyz_lead = diff(xyz_lead, c.draglift.time1)
        inflow_lead = calc_inflow(vxyz_lead, p.U)
        inflow_lead[:, 1] = 0  # first project to xz plane

        inflow_lead_U = inflow_lead.copy()
        inflow_lead_U[:, 0] = p.U

        # u = inflow_lead[:, 0]
        # vw = np.linalg.norm(inflow_lead[:, 1:], axis=-1)
        # flow_pitch = np.degrees(np.atan(vw / u)) * np.sign(inflow_lead[:, 2])
        flow_pitch = np.degrees(np.atan(inflow_lead[:, 2] / inflow_lead[:, 0]))
        flow_pitch_U = np.degrees(np.atan(inflow_lead_U[:, 2] / inflow_lead_U[:, 0]))

        xyz_tral = get_xyz(kin, f"{pos}_trail")
        xyz_sect = xyz_tral - xyz_lead
        xyz_sect[:, 1] = 0
        sect_pitch = -np.degrees(np.atan(xyz_sect[:, 2] / xyz_sect[:, 0]))

        return sect_pitch, flow_pitch, flow_pitch + sect_pitch, flow_pitch_U + sect_pitch
        # return TFilter.butter(time, cutoff_period=0.01 * p.T).filt(aoas)

    eff_aoas = {}
    for pos in ["elbw", "wrst", "wtip", "ftip"]:
        sect, flow, effa, effau = make_eff_aoa(pos)
        eff_aoas[f"{pos}_sect"] = sect
        eff_aoas[f"{pos}_flow"] = flow
        eff_aoas[f"{pos}_effa"] = effa
        eff_aoas[f"{pos}_effau"] = effau

    ax.plot(time, pitch, "k--", label="Pitch")
    ax.plot(time, eff_aoas["elbw_effa"], "r-", label="Eff AOA Elbow")
    ax.plot(time, eff_aoas["wrst_effa"], "g-", label="Eff AOA Wrist")
    ax.plot(time, eff_aoas["wtip_effa"], "b-", label="Eff AOA Hand Tip")
    ax.plot(time, eff_aoas["ftip_effa"], "m-", label="Eff AOA Tip")
    # ax.plot(time, eff_aoas["elbw_flow"], "r--", label="Flow Pitch Elbow")
    # ax.plot(time, eff_aoas["wrst_flow"], "g--", label="Flow Pitch Wrist")
    # ax.plot(time, eff_aoas["wtip_flow"], "b--", label="Flow Pitch Hand Tip")
    # ax.plot(time, eff_aoas["ftip_flow"], "m--", label="Flow Pitch Tip")
    # ax.plot(time, eff_aoas["elbw_sect"], "r--.", label="Sect Pitch Elbow")
    # ax.plot(time, eff_aoas["wrst_sect"], "g--.", label="Sect Pitch Wrist")
    # ax.plot(time, eff_aoas["wtip_sect"], "b--.", label="Sect Pitch Hand Tip")

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time / T")
    ax.set_ylabel("Deg")
    ax.set_title("Kinematics AOA")
    fig.tight_layout()

    c.create_matplotlib_fig(fig, "kin_aoa")

    c.create_csv_dataframe(eff_aoas, "kin_aoa")

    c.create_json_dict(
        {
            "elbw_effa": stat(eff_aoas["elbw_effa"]),
            "wrst_effa": stat(eff_aoas["wrst_effa"]),
            "wtip_effa": stat(eff_aoas["wtip_effa"]),
            "ftip_effa": stat(eff_aoas["ftip_effa"]),
            "elbw_flow": stat(eff_aoas["elbw_flow"]),
            "wrst_flow": stat(eff_aoas["wrst_flow"]),
            "wtip_flow": stat(eff_aoas["wtip_flow"]),
            "ftip_flow": stat(eff_aoas["ftip_flow"]),
        },
        "kin_aoa",
    )

    fig = plt.figure()
    ax = fig.add_subplot()

    def make_z(pos):
        return getattr(kin, f"{pos}_lead_z").ravel()

    z_elbw = make_z("elbw")
    z_wrst = make_z("wrst")
    z_wtip = make_z("wtip")
    z_ftip = make_z("ftip")
    ax.plot(time, (z_elbw - p.gm.center[2]) / p.chord, label="Z Elbow")
    ax.plot(time, (z_wrst - p.gm.center[2]) / p.chord, label="Z Wrist")
    ax.plot(time, (z_wtip - p.gm.center[2]) / p.chord, label="Z Hand Tip")
    ax.plot(time, (z_ftip - p.gm.center[2]) / p.chord, label="Z Tip")

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time / T")
    ax.set_ylabel("(Z - Z0) / Chord")
    ax.set_title("Kinematics Z")
    fig.tight_layout()

    c.create_matplotlib_fig(fig, "kin_z")

    def stat_st(d):
        st = p.f * d["p2p"] / p.U
        d["st"] = st
        d["flow_pitch"] = np.degrees(np.atan(st * np.pi))
        return d

    d = {
        "elbw": stat_st(stat(z_elbw)),
        "wrst": stat_st(stat(z_wrst)),
        "wtip": stat_st(stat(z_wtip)),
        "ftip": stat_st(stat(z_ftip)),
    }

    c.create_json_dict(d, "kin_z")
