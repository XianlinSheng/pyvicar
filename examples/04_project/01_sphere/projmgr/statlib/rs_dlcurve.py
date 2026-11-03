import numpy as np
import matplotlib.pyplot as plt
import pyvicar.tools.matplotlib as pvmpl
from pyvicar.tools.post.time import slice_by_t, correct_k, correct_kb
import pandas as pd
import projmgr.paths as paths
from .misc import dlcurve_naca0012
from .misc import rsdata

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())

mpi_async = True


def stat_rs_dlcurve():
    aoa = np.array([-10, -5, 0, 5, 10, 30, 50])
    n = aoa.shape[0]
    drag_c0 = np.zeros((2, n))
    drag_c14 = np.zeros((2, n))
    span_c0 = np.zeros((2, n))
    span_c14 = np.zeros((2, n))
    lift_c0 = np.zeros((2, n))
    lift_c14 = np.zeros((2, n))
    for i, a in enumerate([-10, -5, 0, 5, 10, 30, 50]):
        l = "l" if a >= 0 else ""
        code = f"rsa{a}c0{l}r120RC"

        dsl = rsdata.get_max(code)
        drag_c0[0, i] = dsl["drag"]
        span_c0[0, i] = dsl["span"]
        lift_c0[0, i] = dsl["lift"]
        dsl = rsdata.get_stab(code)
        drag_c0[1, i] = dsl["drag"]
        span_c0[1, i] = dsl["span"]
        lift_c0[1, i] = dsl["lift"]

        code = f"rsa{a}c14{l}r120RC"

        dsl = rsdata.get_max(code)
        drag_c14[0, i] = dsl["drag"]
        span_c14[0, i] = dsl["span"]
        lift_c14[0, i] = dsl["lift"]
        dsl = rsdata.get_stab(code)
        drag_c14[1, i] = dsl["drag"]
        span_c14[1, i] = dsl["span"]
        lift_c14[1, i] = dsl["lift"]

    k, b = correct_kb(lift_c0, lift_c14)

    pd.DataFrame(
        {
            "aoa": aoa,
            "drag_max_c0": drag_c0[0, :],
            "span_max_c0": span_c0[0, :],
            "lift_max_c0": lift_c0[0, :],
            "drag_max_c14": drag_c14[0, :],
            "span_max_c14": span_c14[0, :],
            "lift_max_c14": lift_c14[0, :],
            "drag_stab_c0": drag_c0[1, :],
            "span_stab_c0": span_c0[1, :],
            "lift_stab_c0": lift_c0[1, :],
            "drag_stab_c14": drag_c14[1, :],
            "span_stab_c14": span_c14[1, :],
            "lift_stab_c14": lift_c14[1, :],
        }
    ).to_csv(paths.stat / "rs_dlcurve.csv", index=False)

    naca_aoa, naca_cl = dlcurve_naca0012.cl_re7e5()
    naca_lam_s = slice_by_t(naca_aoa, 0, 11)
    naca_lam_aoa = naca_aoa[naca_lam_s]
    lift_th_nok = np.sin(np.radians(naca_lam_aoa)) * np.cos(np.radians(naca_lam_aoa))
    kth = correct_k(lift_th_nok, naca_cl[naca_lam_s])
    lift_th_nok = np.sin(np.radians(aoa)) * np.cos(np.radians(aoa))
    lift_th = lift_th_nok * kth

    lift_th_nok_ofs = np.sin(np.radians(aoa + 2.5)) * np.cos(np.radians(aoa))
    lift_th_ofs = lift_th_nok_ofs * 4.5

    fig1 = plt.figure()
    plt.plot(aoa[:-1], lift_c0[0, :-1], "k-x", label="Max Force")
    plt.plot(aoa[:-1], lift_c0[1, :-1], "k-o", label="Stable Force")
    # plt.plot(aoa, lift_c14[0, :], "b-o", label="c14")
    # plt.plot(aoa, lift_c14[1, :], "b-o")
    # plt.plot(aoa, k * lift_c0 + b, "b--", label=f"c0*{k:.3f} + {b:.3f}")
    # plt.plot(aoa, (lift_c14 - b) / k, "r--", label=f"(c14 - b)/k")
    # plt.plot(aoa, lift_th, "r--", label=f"theory (* {kth:0.3f})")
    # plt.plot(aoa, lift_th_ofs, "b--", label=f"theory (+2deg *4)")
    plt.plot(naca_aoa, naca_cl, "k--", label="NACA0012 AR4 Re7e5")
    plt.plot([0, 10], [0, 1.1], "k-.", label="2D Flat Plate")
    plt.axis([None, None, None, None])
    plt.grid(True)
    plt.legend()
    plt.xlabel(r"Angle of Attack $(^\circ)$" + "\n(b) Lift Forces against Pitch Angles")
    plt.ylabel(r"Lift $L/(1/2\rho U^2 A)$")
    plt.tight_layout()
    # plt.show()
    plt.savefig(paths.stat / "rs_lift_curve.png")

    fig2 = plt.figure()
    plt.plot(aoa, drag_c0[0, :], "r-o", label="c0")
    plt.plot(aoa, drag_c0[0, :], "r-o")
    plt.plot(aoa, drag_c14[1, :], "b-o", label="c14")
    plt.plot(aoa, drag_c14[1, :], "b-o")
    plt.plot(*dlcurve_naca0012.cd_re7e5(), "k-", label="NACA0012 AR4 Re7e5")
    plt.plot(*dlcurve_naca0012.cd_re1e6(), "k--", label="NACA0012 AR4 Re1e6")
    plt.axis([None, None, None, None])
    plt.grid(True)
    plt.legend()
    plt.xlabel("aoa")
    plt.ylabel(r"Drag $D/(1/2\rho U^2 A)$")
    plt.tight_layout()
    # plt.show()
    plt.savefig(paths.stat / "rs_drag_curve.png")
