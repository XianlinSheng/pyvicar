from pyvicar.case.common import Case
import pyvicar.tools.matplotlib as pvmpl
import matplotlib.pyplot as plt

pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())


def post_forces(p):
    c = Case(p.name)
    c.draglift.read()

    forces = c.draglift.proc()

    # forces = c.draglift.proc(
    #     cut=[0.1, None],
    #     sum_force=True,
    #     sum_moment=False,
    #     sum_power=False,
    #     sum_area=False,
    #     filter_cutoff_period=0.1,
    # )

    fig = plt.figure()
    ax = fig.add_subplot()

    ax.plot(forces.time / p.T, forces.cx[0] / p.d**2, label="CD")
    ax.plot(forces.time / p.T, forces.cy[0] / p.d**2, label="CLY")
    ax.plot(forces.time / p.T, forces.cz[0] / p.d**2, label="CLZ")

    ax.axis([None, None, None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time / T")
    ax.set_ylabel("F / (1/2*rho*U^2*d^2)")
    ax.set_title("Forces")
    fig.tight_layout()

    c.create_matplotlib_fig(fig, "draglift")

    # fig.savefig("draglift.png")


from run_test import p

post_forces(p)
