import string
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from scipy.interpolate import griddata
import pyvicar.tools.matplotlib as pvmpl
from .misc.dlbar import plot_dlbar
from projmgr import studies
from projmgr import paths

mpi_async = True

pvmpl.set_default(pvmpl.font_sizes_xl() | pvmpl.font_math())


def read_case(st, k):
    code = f"fotst{st}k{k}c14r120RC"
    p = studies.to_params(code)
    c = p.Case(p.name)
    c.draglift.read()
    c.post.read()
    return p, c


def lift(st, k):
    p, c = read_case(st, k)
    return c.post.reports["dl"]["json"].to_dict()["lift"]["avg"]


def thrust(st, k):
    p, c = read_case(st, k)
    return -c.post.reports["dl"]["json"].to_dict()["drag"]["avg"]


def power(st, k):
    p, c = read_case(st, k)
    return c.post.reports["dl"]["json"].to_dict()["power"]["avg"]


def lift_eff(st, k):
    p, c = read_case(st, k)
    l = p.span
    cl = c.post.reports["dl"]["json"].to_dict()["lift"]["avg"]
    cp = c.post.reports["dl"]["json"].to_dict()["power"]["avg"]
    return cl / cp / p.U 


def thrust_eff(st, k):
    p, c = read_case(st, k)
    l = p.span
    ct = -c.post.reports["dl"]["json"].to_dict()["drag"]["avg"]
    cp = c.post.reports["dl"]["json"].to_dict()["power"]["avg"]
    return ct / cp / p.U 


def plot_var(f, sts, ks, label, xlabel, output):
    stvs = np.array([st / 100 for st, k in product(sts, ks)])
    kvs = np.array([k / 100 for st, k in product(sts, ks)])
    vals = np.array([f(st, k) for st, k in product(sts, ks)])

    st1, st2 = .19, .41
    k1, k2 = .24, .76
    st_g1 = np.linspace(st1, st2, 100)
    k_g1 = np.linspace(k1, k2, 100)
    st_g2, k_g2 = np.meshgrid(st_g1, k_g1)
    val_g2 = griddata((stvs, kvs), vals, (st_g2, k_g2), method="linear")
    
    # # fill extrapolation
    # points = np.column_stack((stvs, kvs))
    # interp_rbf = RBFInterpolator(points, vals, kernel='linear', smoothing=0.0)
    # grid_points = np.column_stack((st_g2.ravel(), st_g2.ravel()))
    # val_g2_ex = interp_rbf(grid_points).reshape(st_g2.shape)
    # val_g2 = np.where(np.isnan(val_g2), val_g2_ex, val_g2)

    fig, ax = plt.subplots(figsize=(8, 6))
    cf = ax.contourf(st_g2, k_g2, val_g2, levels=30, cmap="viridis")
    fig.colorbar(cf, ax=ax, label=label)
    sc = ax.scatter(stvs, kvs, s=8, c='red', alpha=0.5)

    ax.set_xlabel(r'St' + f"\n{xlabel}")
    ax.set_ylabel(r'$\theta_m/a$')
    ax.set_xlim(st1, st2)
    ax.set_ylim(k1, k2)

    fig.tight_layout()
    fig.savefig(paths.stat / f"{output}.png")


def plot_aoa(st, k, ax, label, *args, **kwargs):
    p, c = read_case(st, k)
    t = c.draglift.time1
    a = c.post.reports["kin_aoa"]["csv"].to_pandas()["ftip_effa"]
    ax.plot(t / p.T, a, *args, label=label, markevery=200, **kwargs)


def plot_aoau(st, k, ax, label, *args, **kwargs):
    p, c = read_case(st, k)
    t = c.draglift.time1
    a = c.post.reports["kin_aoa"]["csv"].to_pandas()["ftip_effau"]
    ax.plot(t / p.T, a, *args, label=label, markevery=200, **kwargs)


def plot_lift(st, k, ax, label, *args, **kwargs):
    p, c = read_case(st, k)
    t = c.draglift.time1
    l = c.post.reports["dl"]["csv"].to_pandas()["lift"]
    ax.plot(t / p.T, l, *args, label=label, markevery=200, **kwargs)


def plot_thrust(st, k, ax, label, *args, **kwargs):
    p, c = read_case(st, k)
    t = c.draglift.time1
    th = -c.post.reports["dl"]["csv"].to_pandas()["drag"]
    ax.plot(t / p.T, th, *args, label=label, markevery=200, **kwargs)



def stat_fot():
    sts = np.array([20, 20, 40])
    ks = np.array([25, 50, 75])

    # dl bar
    c = 14
    plat = "RC"

    for st, abc in zip(sts, string.ascii_lowercase):
        fracs = ["a/4", "a/2", "3a/4"]
        labels = [rf"$\theta_m={frac}$" for frac in fracs]
        cases = [f"fotst{st}k{k}c{c}r120{plat}" for k in ks]

        plot_dlbar(labels=labels, cases=cases, figsize=(8, 6), output=f"fot_dlbar_st{st}", xlabel=f"({abc}) St={st/100}")

    # space plots
    plot_var(lift, sts, ks, r"Lift $L/(1/2\rho U^2 A_\mathrm{max})$", "(a) Lift Coefficient", "fot_space_lift")
    plot_var(thrust, sts, ks, r"Thrust $T/(1/2\rho U^2 A_\mathrm{max})$", "(b) Thrust Coefficient", "fot_space_thrust")
    plot_var(power, sts, ks, r"Power $P/(1/2\rho U^3 A_\mathrm{max})$", "(c) Power Coefficient", "fot_space_power")

    plot_var(lift_eff, sts, ks, r"Lift Eff $LU/P$", "Lift Eff", "fot_space_lift_eff")
    plot_var(thrust_eff, sts, ks, r"Thrust $TU/P$", "Thrust Eff", "fot_space_thrust_eff")

    # eff aoa, lift, thrust st40
    st = 40
    ks = [25, 50, 75]
    alabels = ["a/4", "a/2", "3a/4"]
    styles = ["k-x", "k-o", "k-^"]

    fig = plt.figure()
    ax1 = fig.add_subplot()
    for k, alabel, style in zip(ks, alabels, styles):
        plot_aoa(st, k, ax1, rf"$\theta_m={alabel}$", style)
    # plot_aoau(st, 75, ax1, rf"$\theta_m={alabel}$ No Sweep", "k--^")
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(a) Effective AoA at Wing Tip")
    ax1.set_ylabel(r"AoA $(^\circ)$")
    ax1.set_xlim([.1, 1.1])
    fig.tight_layout()
    fig.savefig(paths.stat / f"fot_st{st}_effa.png")

    fig = plt.figure()
    ax1 = fig.add_subplot()
    for k, alabel, style in zip(ks, alabels, styles):
        plot_lift(st, k, ax1, rf"$\theta_m={alabel}$", style)
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(b) Lift Coefficient")
    ax1.set_ylabel(r"Lift $L/(1/2\rho U^2 A_\mathrm{max})$")
    ax1.set_xlim([.1, 1.1])
    fig.tight_layout()
    fig.savefig(paths.stat / f"fot_st{st}_lift.png")

    fig = plt.figure()
    ax1 = fig.add_subplot()
    for k, alabel, style in zip(ks, alabels, styles):
        plot_thrust(st, k, ax1, rf"$\theta_m={alabel}$", style)
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(c) Thrust Coefficient")
    ax1.set_ylabel(r"Thrust $T/(1/2\rho U^2 A_\mathrm{max})$")
    ax1.set_xlim([.1, 1.1])
    fig.tight_layout()
    fig.savefig(paths.stat / f"fot_st{st}_thrust.png")
