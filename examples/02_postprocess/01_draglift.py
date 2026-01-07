from pyvicar.case.common import Case
import pyvicar.tools.matplotlib as pvmpl
import matplotlib.pyplot as plt

# 1. draglift
# this script reads the case draglift outputs and plot the curves

# this is for some presets of plotting fontsize.
# font_sizes_l() is the default (without importing pvmpl) and will be friendly for plot screen
# font_sizes_xl() will be friendly for illustration included in another canvas
pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())

c = Case("tut_draglift")
c.draglift.read()

forces = c.draglift.proc()

# # the following is a full version of the capabilities, see bottom for argument descriptions
# forces = c.draglift.proc(
#     cut=[0.1, None],
#     sum_force=True,
#     sum_moment=False,
#     sum_power=False,
#     sum_area=False,
#     filter_cutoff_period=0.1,
# )

# now retrieve series simply by:
# forces.cx[0] means the series for the first body
fig = plt.figure()
ax = fig.add_subplot()

ax.plot(forces.time, forces.cx[0], label="drag")

ax.axis([None, None, None, None])
ax.grid(True)
ax.legend()
ax.set_xlabel("Time")
ax.set_ylabel("CD")
ax.set_title("Drag")
fig.tight_layout()

plt.show()

# # or savefig
# fig.savefig("draglift.png")

# # or using pyvicar managed postprocessing file structure, at case/Post/Reports/...
# c.create_matplotlib_fig(fig, "draglift")

# one job is only done if its arg is specified,
# if call it empty c.draglift.proc(), it will give raw series

# cut: cut all series between certain time before any further processing.
#      cut=[start, end], specify one as None for no limit, [None, None] has no cut effect

# sum_force: sum force for all bodies and create a new series xxx_sum
#            force includes cx, cxp, cxs, cy, cyp, cys, cz, czp, czs
#            for pressure, stress components, and total force in xyz directions
#            and there will be new series cx_sum, ...

# sum_moment: sum moment for all bodies and create a new series xxx_sum
#             moment includes cmx, cmxp, cmxs, cmy, cmyp, cmys, cmz, cmzp, cmzs

# sum_power: sum power for all bodies and create a new series xxx_sum
#            power includes cpwx, cpwy, cpwz, cpw
#            for xyz components, and sum of these.
#            note the sum cpw is summation over xyz directions, cpw = cpwx + cpwy + cpwz
#            but sum_power gives summation over bodies,
#            cpw_sum = cpw[0] + cpw[1] + ..., cpwx_sum = cpwx[0] + cpwx[1] + ...

# filter_cutoff_period: lowpass butterworth filter all existing series, including the new.
#                       cutoff the oscillations with period lower than this threshold.

# some versions may not output certain series,
# and pyvicar detects it at runtime and skips their processings if not exist
