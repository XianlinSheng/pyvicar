import pyvicar
import pyvicar.tools.matplotlib as pvmpl
import matplotlib.pyplot as plt
from pyvicar.tools.post.time import stat, prepend_fill

# 1. draglift
# this script reads the case draglift outputs and plot the curves

# use at least v1.0.2 if only for postprocess because in lower version
# instantiating Case(...) alone would truncate existing input files
# create_json_dict, create_csv_dataframe, stat, prepend_fill, c.draglift.nseries are v1.0.2 features
pyvicar.assert_api_version("1.0.2", "1.1.0")

# this is for some presets of plotting fontsize.
# font_sizes_l() is the default (without importing pvmpl) and will be friendly for plot screen
# font_sizes_xl() will be friendly for illustration included in another canvas
pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())

U = 1
d = 1
A = d**2

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

# change this to a completed case in 01_geometry, like tut_sphere here
c = Case("tut_sphere")

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

# C = F/(1/2*rho*U^2*A) vicar3d solver has already divided 1/2, but no U and A (or L) yet
cx = forces.cx[0] / (U**2 * A)
cy = forces.cy[0] / (U**2 * A)
cz = forces.cz[0] / (U**2 * A)

ax.plot(forces.time, cx, label="cx")
ax.plot(forces.time, cy, label="cy")
ax.plot(forces.time, cz, label="cz")

ax.axis([None, None, None, None])
ax.grid(True)
ax.legend()
ax.set_xlabel("Time")
ax.set_ylabel("F/(1/2*rho*U^2*A)")
ax.set_title("Drag Lift Coeff")
fig.tight_layout()

# plt.show()

# pyvicar managed postprocessing file structure, at case/Post/Reports/...
c.create_matplotlib_fig(fig, "draglift")

# make statistics on time series, min max avg ..., return a dict
c.create_json_dict(
    {
        "cx": stat(cx),
        "cy": stat(cy),
        "cz": stat(cz),
    },
    "draglift",
)

# output filtered cleaned series, prepend_fill 0 to original series length
c.create_csv_dataframe(
    {
        "cx": prepend_fill(cx, c.draglift.nseries, 0),
        "cy": prepend_fill(cy, c.draglift.nseries, 0),
        "cz": prepend_fill(cz, c.draglift.nseries, 0),
    },
    "draglift",
)


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
