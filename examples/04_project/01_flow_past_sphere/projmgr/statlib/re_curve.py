import pyvicar
import pyvicar.tools.matplotlib as pvmpl
import projmgr.studies as studies
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

pyvicar.assert_api_version("1.0.2", "1.1.0")

mpi_async = True


def get_last_avg(p):
    c = p.Case(p.name)
    c.draglift.read()

    tn = c.draglift.time1[-1]

    dl = c.draglift.proc(
        cut=[tn - 25 * p.T, None],
        sum_force=True,
        sum_moment=False,
        sum_power=False,
        sum_area=False,
        filter_cutoff_period=0.05 * p.T,
    )

    # solver already divided 1/2
    constant = p.U**2 * np.pi * p.d**2 / 4
    return {
        "cx": np.mean(dl.cx[0] / constant),
        "cy": np.mean(dl.cy[0] / constant),
        "cz": np.mean(dl.cz[0] / constant),
    }


def stat_re_curve():
    pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())
    os.system("mkdir -p stat")

    res = [100, 1000, 10000]
    n = len(res)
    cx = np.zeros(n)
    cy = np.zeros(n)
    cz = np.zeros(n)
    for i, re in enumerate(res):
        code = f"re{re}devr10LC"
        p = studies.to_params(code)

        last_avg = get_last_avg(p)
        cx[i] = last_avg["cx"]
        cy[i] = last_avg["cy"]
        cz[i] = last_avg["cz"]

    res = np.asarray(res)
    pd.DataFrame(
        {
            "res": res,
            "cx": cx,
            "cy": cy,
            "cz": cz,
        }
    ).to_csv("stat/re_curve.csv", index=False)

    fig = plt.figure()
    ax = fig.add_subplot()

    ax.plot(res, cx, "r-x", label="CX")
    ax.plot(res, cy, "g-x", label="CY")
    ax.plot(res, cz, "b-x", label="CZ")

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Re")
    ax.set_ylabel("F / (1/2*rho*U^2*d^2)")
    ax.set_title("Forces")
    fig.tight_layout()
    fig.savefig("stat/re_curve.png")
