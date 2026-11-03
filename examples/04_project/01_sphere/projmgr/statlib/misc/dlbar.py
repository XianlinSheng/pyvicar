import json
import numpy as np
import matplotlib.pyplot as plt
import projmgr.paths as paths



def dlstat(name):
    with open(f"{name}/Post/Reports/dl.json", "r") as f:
        return json.load(f)


def plot_dlbar(labels=[], cases=[], output="dlbar", lift=True, thrust=True, power=True, figsize=(8, 4), xlabel=""):
    if len(labels) != len(cases):
        raise ValueError(f"Mismatch length of labels ({labels}) and cases ({cases})")

    dls = [dlstat(case) for case in cases]
    lifts = np.array([dl["lift"]["avg"] for dl in dls])
    drags = np.array([dl["drag"]["avg"] for dl in dls])
    powers = np.array([dl["power"]["avg"] for dl in dls])

    x = np.arange(len(labels))

    width = 0.3
    count = lift + thrust + power
    match count:
        case 3:
            incs = [-width, 0, width]
        case 2:
            incs = [-width / 2, width / 2]
        case 1:
            incs = [0]
        case 0:
            raise RuntimeError("At least one among lift/drag/power needs to be selected to plot")

    it = iter(incs)

    fig1, ax1 = plt.subplots(figsize=figsize)

    if lift:
        lbar = ax1.bar(x + next(it), lifts, width, color="white", edgecolor="black", hatch="////", label="Lift")
        ax1.bar_label(lbar, fmt="%.2f", padding=2)
    if thrust:
        dbar = ax1.bar(x + next(it), -drags, width, color="white", edgecolor="black", hatch=r"\\\\", label="Thrust")
        ax1.bar_label(dbar, fmt="%.2f", padding=2)

    ax1.set_ylabel(r"Force $F/(1/2\rho U^2 A)$")
    ax1.grid(True)

    if power:
        ax2 = ax1.twinx()
        pbar = ax2.bar(x + next(it), powers, width, color="white", edgecolor="black", hatch="xxxx", label="Power")
        ax2.bar_label(pbar, fmt="%.2f", padding=2)

        ax2.set_ylabel(r"Power $P/(1/2\rho U^3 A)$")
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    else:
        ax1.legend(loc="upper right")

    # Use the same number of ticks
    n_ticks = 7
    y11, y12 = -.2, 1
    ax1.set_ylim([y11, y12])
    ax1.set_yticks(np.linspace(y11, y12, n_ticks))
    if power:
        y21, y22 = -.2, 1
        ax2.set_ylim([y21, y22])
        ax2.set_yticks(np.linspace(y21, y22, n_ticks))

    # T/L ratio between the two bars
    xnames = [
        f"{label}" + (f"\n$T/L={-dragv/liftv:.2f}$" if lift and thrust else "")
        for liftv, dragv, label in zip(lifts, drags, labels)
    ]
    ax1.set_xticks(x)
    ax1.set_xticklabels(xnames)

    if xlabel:
        ax1.set_xlabel(xlabel)

    plt.tight_layout()

    # plt.show()
    fig1.savefig(paths.stat / f"{output}.png")
