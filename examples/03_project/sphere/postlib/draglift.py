import pyvicar.tools.matplotlib as pvmpl
import matplotlib.pyplot as plt

pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())


def post_draglift(p):
    c = p.Case(p.name)
    c.draglift.read()

    # CASE CHECK: what postprocesses to use
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
    ax.plot(dl.time / p.T, dl.cx[0] / p.d**2, label="CD")
    ax.plot(dl.time / p.T, dl.cy[0] / p.d**2, label="CLY")
    ax.plot(dl.time / p.T, dl.cz[0] / p.d**2, label="CLZ")

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time / T")
    ax.set_ylabel("F / (1/2*rho*U^2*d^2)")
    ax.set_title("Forces")
    fig.tight_layout()

    c.create_matplotlib_fig(fig, "dl")
