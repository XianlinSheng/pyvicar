import matplotlib.pyplot as plt
import pyvicar.tools.matplotlib as pvmpl
import pandas as pd
import projmgr.paths as paths
import projmgr.studies as studies
from .misc.dlbar import plot_dlbar

pvmpl.set_default(pvmpl.font_sizes_xl() | pvmpl.font_math())

mpi_async = True


def read_case(c):
    code = f"fsdynst30c{c}r120RC"
    p = studies.to_params(code)
    c = p.Case(p.name)
    c.draglift.read()
    c.post.read()
    return p, c


def plot_lift(c, ax, label, *args, **kwargs):
    p, c = read_case(c)
    t = c.draglift.time1
    l = c.post.reports["dl"]["csv"].to_pandas()["lift"]
    ax.plot(t / p.T, l, *args, label=label, markevery=200, **kwargs)


def plot_power(c, ax, label, *args, **kwargs):
    p, c = read_case(c)
    t = c.draglift.time1
    pw = c.post.reports["dl"]["csv"].to_pandas()["power"]
    ax.plot(t / p.T, pw, *args, label=label, markevery=200, **kwargs)


def stat_camber():
    fig = plt.figure()
    ax1 = fig.add_subplot()
    plot_lift(0, ax1, "Flat Lift", "k-x")
    plot_lift(14, ax1, "Cambered Lift", "k-o")
    ax1.axis([.1, 1.1, None, None])
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(a) Lift Coefficient")
    ax1.set_ylabel(r"Lift $L/(1/2\rho U^2 A_\mathrm{max})$")
    fig.tight_layout()
    fig.savefig(paths.stat / "camber_lift.png")

    fig = plt.figure()
    ax1 = fig.add_subplot()
    plot_power(0, ax1, "Flat", "k-x")
    plot_power(14, ax1, "Cambered", "k-o")
    ax1.axis([.1, 1.1, None, None])
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(b) Power Coefficient")
    ax1.set_ylabel(r"Power $P/(1/2\rho U^3 A_\mathrm{max})$")
    fig.tight_layout()
    fig.savefig(paths.stat / "camber_power.png")

    cambs = [0, 14]
    names = [f"fsdynst30c{camb}r120RC" for camb in cambs]
    plot_dlbar(labels=["Flat", "Cambered"], cases=names, output="camber_dlbar", drag=False, figsize=(6, 4), xlabel="(c) Net Lifts and Power")
