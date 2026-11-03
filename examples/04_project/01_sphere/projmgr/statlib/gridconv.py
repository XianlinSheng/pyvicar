import numpy as np
import matplotlib.pyplot as plt
import pyvicar.tools.matplotlib as pvmpl
import projmgr.studies as studies
import projmgr.paths as paths

pvmpl.set_default(pvmpl.font_sizes_xl() | pvmpl.font_math())

mpi_async = True


def read_case(resol):
    code = f"fotst30k50c14r{resol}{'RC' if resol <= 120 else 'BG'}"
    p = studies.to_params(code)
    c = p.Case(p.name)
    c.draglift.read()
    c.post.read()
    return p, c


def plot_drag(resol, ax, *args, **kwargs):
    p, c = read_case(resol)
    t = c.draglift.time1
    d = c.post.reports["dl"]["csv"].to_pandas()["drag"]
    ax.plot(t / p.T, d, *args, label=rf"$c/\Delta = {resol}$", markevery=200, **kwargs)


def plot_lift(resol, ax, *args, **kwargs):
    p, c = read_case(resol)
    t = c.draglift.time1
    l = c.post.reports["dl"]["csv"].to_pandas()["lift"]
    ax.plot(t / p.T, l, *args, label=rf"$c/\Delta = {resol}$", markevery=200, **kwargs)


def plot_power(resol, ax, *args, **kwargs):
    p, c = read_case(resol)
    t = c.draglift.time1
    pw = c.post.reports["dl"]["csv"].to_pandas()["power"]
    ax.plot(t / p.T, pw, *args, label=rf"$c/\Delta = {resol}$", markevery=200, **kwargs)


def stat_gridconv():
    resols = [100, 120, 140]

    styles = ['k--x', 'k-', 'k--o']

    figd, axd = plt.subplots()
    figl, axl = plt.subplots()
    figp, axp = plt.subplots()

    for resol, style in zip(resols, styles):
        plot_drag(resol, axd, style)
        plot_lift(resol, axl, style)
        plot_power(resol, axp, style)

    axl.axis([.1, 1.1, None, None])
    axl.grid(True)
    axl.legend()
    axl.set_xlabel(r"Time $t/T$" + "\n(a) Lift Coefficients")
    axl.set_ylabel(r"$L/(1/2\rho U^2 A)$")

    axd.axis([.1, 1.1, None, None])
    axd.grid(True)
    axd.legend()
    axd.set_xlabel(r"Time $t/T$" + "\n(b) Drag Coefficients")
    axd.set_ylabel(r"$D/(1/2\rho U^2 A)$")

    axp.axis([.1, 1.1, None, None])
    axp.grid(True)
    axp.legend()
    axp.set_xlabel(r"Time $t/T$" + "\n(c) Power Coefficients")
    axp.set_ylabel(r"$P/(1/2\rho U^3 A)$")

    figd.tight_layout()
    figl.tight_layout()
    figp.tight_layout()

    # plt.show()
    figd.savefig(paths.stat / f"gridconv_drag_history.png")
    figl.savefig(paths.stat / f"gridconv_lift_history.png")
    figp.savefig(paths.stat / f"gridconv_power_history.png")
