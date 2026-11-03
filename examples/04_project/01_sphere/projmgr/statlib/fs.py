import numpy as np
import matplotlib.pyplot as plt
import pyvicar.tools.matplotlib as pvmpl
import projmgr.studies as studies
import projmgr.paths as paths
from .misc.dlbar import plot_dlbar


mpi_async = True


def read_case(sweep):
    code = f"fs{sweep}st30c0r120RC"
    p = studies.to_params(code)
    c = p.Case(p.name)
    c.draglift.read()
    c.post.read()
    return p, c


def plot_lift(sweep, ax, label, *args, **kwargs):
    p, c = read_case(sweep)
    t = c.draglift.time1
    l = c.post.reports["dl"]["csv"].to_pandas()["lift"]
    ax.plot(t / p.T, l, *args, label=label, markevery=200, **kwargs)


def plot_lift_max(sweep, ax, label, *args, **kwargs):
    p, c = read_case(sweep)
    t = c.draglift.time1
    l = c.post.reports["surfrecon_lift"]["csv"].to_pandas()["lift_max"]
    ax.plot(t / p.T, l, *args, label=label, markevery=200, **kwargs)


def plot_power(sweep, ax, label, *args, **kwargs):
    p, c = read_case(sweep)
    t = c.draglift.time1
    pw = c.post.reports["dl"]["csv"].to_pandas()["power"]
    ax.plot(t / p.T, pw, *args, label=label, markevery=200, **kwargs)


def plot_area(sweep, ax, label, *args, **kwargs):
    p, c = read_case(sweep)
    t = c.draglift.time1
    a = c.draglift.proc(filter_cutoff_period=0.05 * p.T).area[0]
    # amax = c.post.reports["dl"]["json"].to_dict()["area"]
    amax = 2.1962447512628547  # tmp, when case result not complete and doesnt have a json report
    ax.plot(t / p.T, a / amax, *args, label=label, markevery=200, **kwargs)


def stat_fs():
    names = ["max", "min", "dyn"]
    labels = ["Max Area", "Min Area", "Changeable"]
    styles = ["k--o", "k--x", "k-"]

    pvmpl.set_default(pvmpl.font_sizes_xl() | pvmpl.font_math())

    # area
    fig = plt.figure()
    ax1 = fig.add_subplot()

    for name, label, style in zip(names, labels, styles):
        plot_area(name, ax1, label, style)

    ax1.axis([.1, 1.1, None, None])
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(a) Wing Area")
    ax1.set_ylabel("Relative Area (%)")

    fig.tight_layout()
    fig.savefig(paths.stat / "fs_area.png")


    # lift
    fig = plt.figure()
    ax1 = fig.add_subplot()

    for name, label, style in zip(names, labels, styles):
        plot_lift(name, ax1, label, style)
    # plot_lift_max("dyn", ax1, "Approx.", 'k--^')

    ax1.axis([.1, 1.1, None, None])
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(b) Lift Coefficient")
    ax1.set_ylabel(r"Lift $L/(1/2\rho U^2 A_\mathrm{max})$")

    fig.tight_layout()
    fig.savefig(paths.stat / "fs_lift.png")


    # power
    fig = plt.figure()
    ax1 = fig.add_subplot()

    for name, label, style in zip(names, labels, styles):
        plot_power(name, ax1, label, style)

    ax1.axis([.1, 1.1, None, None])
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(c) Power Coefficient")
    ax1.set_ylabel(r"Power $P/(1/2\rho U^3 A_\mathrm{max})$")

    fig.tight_layout()
    fig.savefig(paths.stat / "fs_power.png")


    pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())


    # net value
    cases = [f"fs{name}st30c0r120RC" for name in names]

    plot_dlbar(labels=labels[1:], cases=cases[1:], output="fs_dlbar", drag=False, figsize=(6, 4))

