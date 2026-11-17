import matplotlib.pyplot as plt
import pyvicar.tools.matplotlib as pvmpl
import projmgr.studies as studies
import projmgr.paths as paths

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())

mpi_async = True


def read_case(aoa):
    code = f"rsa{aoa}c0{'l' if aoa >= 0 else ''}r120RC"
    p = studies.to_params(code)
    c = p.Case(p.name)
    c.draglift.read()
    c.post.read()   
    return c


def plot_drag(aoa, ax, *args, **kwargs):
    c = read_case(aoa)
    t = c.draglift.time1
    d = c.post.reports["dl"]["csv"].to_pandas()["drag"]
    ax.plot(t, d, *args, label=rf"${aoa}^\circ$", markevery=400, **kwargs)


def plot_lift(aoa, ax, *args, **kwargs):
    c = read_case(aoa)
    t = c.draglift.time1
    l = c.post.reports["dl"]["csv"].to_pandas()["lift"]
    if aoa < 0:
        l = -l
    ax.plot(t, l, *args, label=rf"${aoa}^\circ$", markevery=400, **kwargs)


def stat_rs_dlhistory():
    aoas = [0, 5, -5, 30, 10, -10]
    styles = ['k-', 'k-x', 'k--x', 'k-^', 'k-o', 'k--o']

    figd, axd = plt.subplots()
    figl, axl = plt.subplots()

    for aoa, style in zip(aoas, styles):
        plot_drag(aoa, axd, style)
        plot_lift(aoa, axl, style)

    axd.axis([1, 11, None, None])
    axd.grid(True)
    axd.legend(ncol=2)
    axd.set_xlabel(r"Time $t/(c/U)$")
    axd.set_ylabel(r"Drag $D/(1/2\rho U^2 A)$")

    axl.axis([1, 11, None, None])
    axl.grid(True)
    axl.legend(ncol=2)
    axl.set_xlabel(r"Time $t/(c/U)$" + "\n(a) Time Histories at Different Pitch Angles")
    axl.set_ylabel(r"Lift $|L/(1/2\rho U^2 A)|$")

    plt.tight_layout()

    # plt.show()
    figd.savefig(paths.stat / f"rs_drag_history.png")
    figl.savefig(paths.stat / f"rs_lift_history.png")
