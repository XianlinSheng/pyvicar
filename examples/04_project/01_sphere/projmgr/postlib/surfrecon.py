import pandas as pd
from scipy.interpolate import interp1d
import pyvicar
from projmgr import paths

pyvicar.assert_api_version("1.0.2", "1.1.0")

import pyvicar.tools.matplotlib as pvmpl
from pyvicar.tools.post.time import TFilter, correct_kb, stat
import numpy as np
import matplotlib.pyplot as plt
from .misc.pflib import make_post_pfs

mpi_async = True

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())


def post_surfrecon(p):
    p2 = make_post_pfs(p)

    c = p.Case(p.name)
    c.draglift.read()
    c.report.read()
    dl = c.draglift[1]
    kin = c.report.ib2_wing_kin[1]

    df = pd.read_csv(paths.stat / "rs_dlcurve.csv")
    fmax_full = interp1d(df["aoa"][:-1], df["lift_max_c0"][:-1], kind="linear", fill_value="extrapolate")
    fstab_full = interp1d(df["aoa"][:-1], df["lift_stab_c0"][:-1], kind="linear", fill_value="extrapolate")

    def fmax(aoa):
        return np.sign(aoa) * fmax_full(np.abs(aoa))

    def fstab(aoa):
        return np.sign(aoa) * fstab_full(np.abs(aoa))

    area = dl.area.ravel()

    leads = np.stack(
        [
            p2.xyz_shdr_lead,
            p2.xyz_elbw_lead,
            p2.xyz_wrst_lead,
            p2.xyz_wtip_lead,
            p2.xyz_ftip_lead,
        ]
    )
    trails = np.stack(
        [
            p2.xyz_shdr_trail,
            p2.xyz_elbw_trail,
            p2.xyz_wrst_trail,
            p2.xyz_wtip_trail,
            p2.xyz_ftip_trail,
        ]
    )
    secnorms = np.linalg.norm(trails - leads, axis=-1)
    diags1 = trails[1:, :, :] - leads[:-1, :, :]
    diags2 = leads[1:, :, :] - trails[:-1, :, :]
    # areas = np.linalg.norm(np.cross(diags1, diags2, axis=-1), axis=-1) / 2
    areas = np.cross(diags1, diags2, axis=-1)[:, :, 2] / 2
    area_rec = np.sum(areas, axis=0)

    k, b = correct_kb(area_rec, area)
    area_corr = area_rec * k + b

    def stat_err(x, target):
        return {
            "abs": np.max(np.abs(target - x)),
            "rel": np.max(np.abs((target - x) / area)),
        }

    # ===== approximated area plot, stat ===== #

    fig = plt.figure()
    ax = fig.add_subplot()

    time = kin.time.ravel() / p.T
    ax.plot(time, area, "k--", label="Area")
    ax.plot(time, area_rec, "r", label="Area (Reconstructed)")
    ax.plot(time, areas[0, :], "r--", label="Area (Rec. S-E)")
    ax.plot(time, areas[1, :], "g--", label="Area (Rec. E-W)")
    ax.plot(time, areas[2, :], "b--", label="Area (Rec. W-H)")
    ax.plot(time, areas[3, :], "m--", label="Area (Rec. H-T)")
    ax.plot(time, area_corr, "b", label="Area (Rec. & Corrected)")

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time / T")
    ax.set_ylabel("Area")
    ax.set_title("Area")
    fig.tight_layout()

    c.create_matplotlib_fig(fig, "surfrecon_area")

    report_area = {
        "corr": {"k": k, "b": b},
        "err_rec": stat_err(area_rec, area),
        "err_corr": stat_err(area_corr, area),
        "area": stat(area),
        "area_rec": stat(area_rec),
        "area_corr": stat(area_corr),
        "area_se": stat(areas[0, :]),
        "area_ew": stat(areas[1, :]),
        "area_ww": stat(areas[2, :]),
        "area_wf": stat(areas[3, :]),
    }
    c.create_json_dict(report_area, "surfrecon_area")

    areas_corr = areas * k + b

    # ===== approximated lift plot, stat ===== #

    from .draglift import post_draglift
    from .kin import post_kin

    post_draglift(p)
    post_kin(p)
    c.post.reports.read()

    df_aoa = c.post.reports["kin_aoa"]["csv"].to_pandas()
    df_dl = c.post.reports["dl"]["csv"].to_pandas()
    area_max = c.post.reports["dl"]["json"].to_dict()["area"]

    effaoas = df_aoa[["elbw_effa", "wrst_effa", "wtip_effa", "ftip_effa"]].to_numpy().T
    effaoas = np.insert(effaoas, 0, values=0, axis=0)
    pitches = df_aoa[["elbw_sect", "wrst_sect", "wtip_sect", "ftip_sect"]].to_numpy().T
    pitches = np.insert(pitches, 0, values=0, axis=0)

    def section_to_integral(secs):
        segs = (secs[:-1, :] + secs[1:, :]) / 2
        patches = areas * segs
        integral = np.sum(patches, axis=0)
        return integral

    # seclifts_nok = np.sin(np.radians(effaoas)) * np.cos(np.radians(pitches))
    # secdrags_nok = np.sin(np.radians(effaoas)) * np.sin(np.radians(pitches))
    # constant = 3.745 / area_max
    # lift = section_to_integral(seclifts_nok) * constant
    # drag = section_to_integral(secdrags_nok) * constant
    
    seclifts_max = fmax(effaoas)
    seclifts_stab = fstab(effaoas)
    secdrags_max = seclifts_max * np.tan(np.radians(pitches))
    secdrags_stab = seclifts_stab * np.tan(np.radians(pitches))
    lift_max = section_to_integral(seclifts_max) / area_max
    drag_max = section_to_integral(secdrags_max) / area_max
    lift_stab = section_to_integral(seclifts_stab) / area_max
    drag_stab = section_to_integral(secdrags_stab) / area_max

    fig = plt.figure()
    ax = fig.add_subplot()

    ax.plot(time, df_dl["lift"], "k-", label="Simulation")
    ax.plot(time, lift_stab, "k--x", label=f"Stable", markevery=400)
    ax.plot(time, lift_max, "k--o", label=f"Max", markevery=400)

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time / T")
    ax.set_ylabel(r"$L/(1/2*\rho U^2 A_\mathrm{max})$")
    ax.set_title("Lift Approx.")
    fig.tight_layout()

    c.create_matplotlib_fig(fig, "surfrecon_lift")

    report_lift = {
        "lift": stat(df_dl["lift"]),
        "lift_rec": stat(lift_max),
        "drag": stat(df_dl["drag"]),
        "drag_rec": stat(drag_max),
    }
    c.create_json_dict(report_lift, "surfrecon_lift")

    c.create_csv_dataframe(
        {
            "drag_max": drag_max,
            "lift_max": lift_max,
            "drag_stab": drag_stab,
            "lift_stab": lift_stab,
        },
        "surfrecon_lift",
    )

    # ===== approximated CL distribution plot ===== #

    imin = report_lift["lift"]["argmin"]
    imax = report_lift["lift"]["argmax"]

    def distr(i):
        ysec = leads[:, i, 1]
        ymin = ysec[0]
        ymax = ysec[-1]
        ysec = (ysec - ymin) / (ymax - ymin)
        yseg = (ysec[1:] + ysec[:-1]) / 2

        ystair = np.stack((ysec[:-1], ysec[1:])).T.ravel()
        areaseg = areas[:, i] / np.sum(areas[:, i])
        areastair = np.stack((areaseg, areaseg)).T.ravel()

        effasec = effaoas[:, i]

        return {
            "area": (ystair, areastair),
            "cl": (ysec, seclifts_max[:, i]),
            "cl_avg": (ysec, np.mean(seclifts_max, axis=1)),
            "effa": (ysec, effasec),
        }

    distr_min = distr(imin)
    distr_max = distr(imax)

    fig = plt.figure()
    ax1 = fig.add_subplot()

    ax1.plot(*distr_max["cl"], "b-x", label="CL (max-lift time)")
    ax1.plot(*distr_min["cl"], "b--x", label="CL (min-lift time)")
    ax1.plot(*distr_max["cl_avg"], "b-o", label="CL (avg)")
    ax1.axis([0, 1, None, None])
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel("y / span")
    ax1.set_ylabel("CL")
    ax1.set_title("CL Distribution")

    ax2 = ax1.twinx()
    ax2.plot(*distr_max["area"], "r-", label="Area% (max-lift time)")
    ax2.plot(*distr_min["area"], "r--", label="Area% (min-lift time)")
    ax2.axis([0, 1, 0, 1])
    ax2.set_ylabel("Area%")

    fig.tight_layout()
    c.create_matplotlib_fig(fig, "surfrecon_distr_cl")

    fig = plt.figure()
    ax1 = fig.add_subplot()

    ax1.plot(*distr_max["effa"], "b-x", label="EffA (max-lift time)")
    ax1.plot(*distr_min["effa"], "b--x", label="EffA (min-lift time)")
    ax1.axis([0, 1, None, None])
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel("y / span")
    ax1.set_ylabel("EffA (Deg)")
    ax1.set_title("Eff AOA")

    ax2 = ax1.twinx()
    ax2.plot(*distr_max["area"], "r-", label="Area% (max-lift time)")
    ax2.plot(*distr_min["area"], "r--", label="Area% (min-lift time)")
    ax2.axis([0, 1, 0, 1])
    ax2.set_ylabel("Area%")

    fig.tight_layout()
    c.create_matplotlib_fig(fig, "surfrecon_distr_effa")
