import pyvicar
import pyvicar.tools.matplotlib as pvmpl
import matplotlib.pyplot as plt
from pyvicar.tools.post.time import stat, prepend_fill

pyvicar.assert_api_version("1.0.2", "1.1.0")

pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())

mpi_async = True


def post_draglift(p):
    c = p.Case(p.name)
    c.draglift.read()

    # CASE CHECK: series processings
    # dl = c.draglift.proc()

    dl = c.draglift.proc(
        cut=[p.T, None],
        sum_force=True,
        sum_moment=False,
        sum_power=False,
        sum_area=False,
        filter_cutoff_period=0.1,
    )

    fig = plt.figure()
    ax = fig.add_subplot()

    # CASE CHECK: what curves to plot and configs
    # cx has already 1/2 divided in the solver
    A = p.d**2
    cx = dl.cx[0] / A
    cy = dl.cy[0] / A
    cz = dl.cz[0] / A
    tau = dl.time / p.T
    ax.plot(tau, cx, label="CX")
    ax.plot(tau, cy, label="CY")
    ax.plot(tau, cz, label="CZ")

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time / T")
    ax.set_ylabel("F / (1/2*rho*U^2*d^2)")
    ax.set_title("Forces")
    fig.tight_layout()

    c.create_matplotlib_fig(fig, "dl")

    c.create_json_dict(
        {
            "cx": stat(cx),
            "cy": stat(cy),
            "cz": stat(cz),
        },
        "dl",
    )

    c.create_csv_dataframe(
        {
            "cx": prepend_fill(cx, c.draglift.nseries, 0),
            "cy": prepend_fill(cy, c.draglift.nseries, 0),
            "cz": prepend_fill(cz, c.draglift.nseries, 0),
        },
        "dl",
    )
