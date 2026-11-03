import pyvicar

pyvicar.assert_api_version("1.0.2", "1.1.0")

import pyvicar.tools.matplotlib as pvmpl
import pyvicar.tools.log as log
from pyvicar.tools.post.time import prepend_fill, slice_by_t, stat
import numpy as np
import matplotlib.pyplot as plt

mpi_async = True

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())


def post_draglift(p):
    c = p.Case(p.name)
    c.draglift.read()

    # CASE CHECK: what postprocesses to use
    # dl = c.draglift.proc()

    dl = c.draglift.proc(
        cut=[0.1 * p.T, None],
        sum_force=True,
        sum_moment=False,
        sum_power=False,
        sum_area=False,
        filter_cutoff_period=0.05 * p.T,
    )

    # ===== plot ===== #

    fig = plt.figure()
    ax1 = fig.add_subplot()

    # CASE CHECK: what curves to plot and configs
    # cx has already 1/2 divided in the solver
    # area = np.max(dl.area[0])
    area = 2.1962447512628547  # max area of non-cambered wing, consistent across cases
    drag = dl.cx[0] / p.U**2 / area
    span = dl.cy[0] / p.U**2 / area
    lift = dl.cz[0] / p.U**2 / area
    ax1.plot(dl.time / p.T, drag, 'k-o', label="Drag", markevery=200)
    # ax1.plot(dl.time / p.T, span, label="Span")
    ax1.plot(dl.time / p.T, lift, 'k-x', label="Lift", markevery=200)

    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$")
    ax1.set_ylabel(r"Force $F/(1/2\rho U^2 A_\mathrm{max})$")

    power = -dl.cpw[0] / p.U**3 / area
    ax2 = ax1.twinx()
    ax2.plot(dl.time / p.T, power, 'k-', label=r"Power")
    ax2.set_ylabel(r"Power $P/(1/2\rho U^3 A_\mathrm{max})$")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    # Use the same number of ticks
    n_ticks = 11
    x1, x2 = 0, 1.1
    y11, y12 = -1, 2
    ax1.axis([x1, x2, y11, y12])
    ax1.set_yticks(np.linspace(y11, y12, n_ticks))
    y21, y22 = 0, 2
    ax2.axis([x1, x2, y21, y22])
    ax2.set_yticks(np.linspace(y21, y22, n_ticks))

    fig.tight_layout()

    c.create_matplotlib_fig(fig, "dl")

    # ===== filtered series ===== #

    n = c.draglift[1].time.shape[0]
    drag = prepend_fill(drag, n, 0)
    span = prepend_fill(span, n, 0)
    lift = prepend_fill(lift, n, 0)
    power = prepend_fill(power, n, 0)

    dragp = dl.cxp[0] / p.U**2 / area
    spanp = dl.cyp[0] / p.U**2 / area
    liftp = dl.czp[0] / p.U**2 / area
    dragp = prepend_fill(dragp, n, 0)
    spanp = prepend_fill(spanp, n, 0)
    liftp = prepend_fill(liftp, n, 0)

    c.create_csv_dataframe(
        {
            "drag": drag,
            "span": span,
            "lift": lift,
            "power": power,
            "dragp": dragp,
            "spanp": spanp,
            "liftp": liftp,
        },
        "dl",
    )

    # ===== stat values ===== #

    time = c.draglift.time1

    if time[-1] < p.T:
        raise RuntimeError(f"Case sim length too short to stat a cycle, {time[-1]} < {p.T}")

    s = slice_by_t(time, time[-1] - p.T, None)

    d = {
        "area": area,
        "drag": stat(drag[s]),
        "span": stat(span[s]),
        "lift": stat(lift[s]),
        "power": stat(power[s]),
        "dragp": stat(dragp[s]),
        "spanp": stat(spanp[s]),
        "liftp": stat(liftp[s]),
    }

    c.create_json_dict(d, "dl")
