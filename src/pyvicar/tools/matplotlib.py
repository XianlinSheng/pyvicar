import matplotlib as mpl
import matplotlib.pyplot as plt
from pyvicar.tools.miscellaneous import args


def font_sizes_l():
    return {
        "font.size": 14,  # default text size
        "axes.titlesize": 18,  # title
        "axes.labelsize": 16,  # axis labels
        "xtick.labelsize": 14,  # x ticks
        "ytick.labelsize": 14,  # y ticks
        "legend.fontsize": 14,  # legend
    }


def font_sizes_xl():
    return {
        "font.size": 18,  # default text size
        "axes.titlesize": 22,  # title
        "axes.labelsize": 20,  # axis labels
        "xtick.labelsize": 18,  # x ticks
        "ytick.labelsize": 18,  # y ticks
        "legend.fontsize": 18,  # legend
    }


def set_default(mpl_kwargs={}, plt_kwargs={}):
    mpl_kwargs = args.add_default(
        mpl_kwargs,
        {
            "figure.dpi": 100,
            "savefig.dpi": 300,
            # "text.usetex": True,
            # "font.family": "Times New Roman",
        },
    )
    plt_kwargs = args.add_default(
        plt_kwargs,
        font_sizes_l(),
    )

    for k, v in mpl_kwargs.items():
        mpl.rcParams[k] = v

    for k, v in plt_kwargs.items():
        plt.rcParams[k] = v
