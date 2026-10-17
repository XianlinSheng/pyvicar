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


def font_math(usetex=False):
    if usetex:
        return {"text.usetex": True}
    else:
        return {
            "text.usetex": False,
            "axes.formatter.use_mathtext": True,
            "font.family": "serif",
            "font.serif": "cmr10",
            "mathtext.fontset": "cm",
            "mathtext.rm": "serif",
            "mathtext.it": "serif:italic",
            "mathtext.bf": "serif:bold",
        }



def set_default(kwargs={}):
    kwargs = args.add_default(
        kwargs,
        {
            "figure.dpi": 100,
            "savefig.dpi": 300,
        } | 
        font_sizes_l(),
    )

    for k, v in kwargs.items():
        plt.rcParams[k] = v
