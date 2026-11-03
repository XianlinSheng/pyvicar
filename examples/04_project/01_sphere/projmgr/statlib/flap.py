import numpy as np
import matplotlib.pyplot as plt
import pyvicar.tools.matplotlib as pvmpl
import projmgr.studies as studies
import projmgr.paths as paths

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())

mpi_async = True


def stat_flap():
    code = f"fsminst30c0r120RC"
    p = studies.to_params(code)
    c = p.Case(p.name)
    c.draglift.read()
    c.post.read()   
    t = c.draglift.time1

    # eff aoa
    aoas = c.post.reports["kin_aoa"]["csv"].to_pandas()
    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.plot(t / p.T, aoas["elbw_effa"], 'k-x', label="Elbow", markevery=200)
    ax1.plot(t / p.T, aoas["wrst_effa"], 'k-o', label="Wrist", markevery=200)
    ax1.plot(t / p.T, aoas["wtip_effa"], 'k-^', label="Hand Tip", markevery=200)
    ax1.plot(t / p.T, aoas["ftip_effa"], 'k-v', label="Wing Tip", markevery=200)
    ax1.axis([.1, 2.1, None, None])
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(a) Effective AoA")
    ax1.set_ylabel(r"AoA $(^\circ)$")

    fig.tight_layout()
    fig.savefig(paths.stat / "flap_effaoa.png")


    # dl history
    lift = c.post.reports["dl"]["csv"].to_pandas()["lift"]
    power = c.post.reports["dl"]["csv"].to_pandas()["power"]
    lift_max = c.post.reports["surfrecon_lift"]["csv"].to_pandas()["lift_max"]
    lift_stab = c.post.reports["surfrecon_lift"]["csv"].to_pandas()["lift_stab"]

    fig = plt.figure()
    ax1 = fig.add_subplot()

    ax1.plot(t / p.T, lift, 'k-x', label="Lift", markevery=400)
    ax1.plot(t / p.T, lift_max, 'k--^', label="Approx. Max", markevery=400)
    ax1.plot(t / p.T, lift_stab, 'k--v', label="Approx. Stable", markevery=400)

    ax1.grid(True)
    ax1.legend()
    ax1.set_xlabel(r"Time $t/T$" + "\n(b)Lift and Power")
    ax1.set_ylabel(r"Lift $L/(1/2\rho U^2 A_\mathrm{max})$")

    ax2 = ax1.twinx()
    ax2.plot(t / p.T, power, 'k-', label=r"Power")
    ax2.set_ylabel(r"Power $P/(1/2\rho U^3 A_\mathrm{max})$")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    # Use the same number of ticks
    n_ticks = 11
    x1, x2 = 0.1, 2.1
    y11, y12 = -1, 2
    ax1.axis([x1, x2, y11, y12])
    ax1.set_yticks(np.linspace(y11, y12, n_ticks))
    y21, y22 = 0, 2
    ax2.axis([x1, x2, y21, y22])
    ax2.set_yticks(np.linspace(y21, y22, n_ticks))

    fig.tight_layout()

    fig.savefig(paths.stat / "flap_dlhistory.png")


