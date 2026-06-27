import pyvicar
import pyvicar.tools.mpi as mpi
import numpy as np
import matplotlib.pyplot as plt
import pyvicar.tools.matplotlib as pvmpl

# 5. recorder
# recorder is a 2d figure animation style that draws the curve left to right in time
# generally used together with field/body animations to show realtime reports
# run this after finishing 01_draglift and 02_isoq

# use at least v1.0.2 if only for postprocess because in lower version
# instantiating Case(...) alone would truncate existing input files
pyvicar.assert_api_version("1.0.2", "1.1.0")

pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

c = Case("tut_sphere")

c.read()

# typically one postprocess item generates multiple name.xx with different extensions
# this is referred as c.post.reports[name][ext] (same for c.post.animations[name][ext])
# note that reports.read() only scans for the existence of files,
# convert to python data structure by ["csv"].to_pandas(), ["json"].to_dict(), ["png"].to_ffmpeg()
draglift_df = c.post.reports["draglift"]["csv"].to_pandas()

# df[["a", "b"]] gives (nseries, 2) shaped array, transpose and unpack into 3 1d series
cx, cy, cz = draglift_df[["cx", "cy", "cz"]].to_numpy().T


def fig_f(ts, t, cx, cy, cz):
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.plot(t, cx, label="cx")
    ax.plot(t, cy, label="cy")
    ax.plot(t, cz, label="cz")

    ax.axis([0, c.draglift.time1[-1], None, None])
    ax.grid(True)
    ax.legend()
    ax.set_xlabel("Time")
    ax.set_ylabel("F/(1/2*rho*U^2*A)")
    ax.set_title("Drag Lift Coeff")
    fig.tight_layout()

    return fig


tsteps = np.arange(c.draglift.nseries) + 1
a = c.create_recorder_video(
    tsteps,
    [c.draglift.time1, cx, cy, cz],
    fig_f,
    c.dump.vtm,
    dt=1,
    keep_frames=True,
    out_name="draglift_recorder",
)

# a = c.create_recorder_video(
#     c.draglift.time1,
#     [c.draglift.time1, cx, cy, cz],
#     fig_f,
#     c.dump.vtm,
#     dt=c.draglift.time1[1] - c.draglift.time1[0],
#     keep_frames=True,
#     out_name="draglift_recorder",
# )

# this creates a new animation "q_...draglift" by ffmpeg handle
# the ffmpeg handle is obtained by Canvas tool that combines and arranges multiple videos
# q_p_o2 is the background, and more videos can be appended as rows below it
# row height is relative to background video height
c.post.animations.get_or_create("q_p_o2_draglift").video_by_ffmpeg(
    c.post.animations["q_p_o2"]["mp4"]
    .to_canvas(row_height=1 / 3)
    .append_row([a["mp4"]])
    .to_ffmpeg(),
    outformat="mp4",
)

mpi.print_elapsed_time()

# Note that two commands are provided here,
# the difference is the time stamping strategy, ts=... (first argument) and dt=.../t_f=...
#   the given arrays are defined on time stamp array ts, ts[i] gives t
#   a vtk stores the tstep, vtk.tstep*dt gives t (or specify t_f=function(tstep)->t)
# the create_recorder_video function will find the matching idx in the array for a vtk tstep,
# and slice all the given series (2nd argument) till the vtk time
# the sliced ts and series will be passed to fig_f(ts[s], *[series[s] for series in series_list])
# so in the end each vtk frame is matched with a figure only plotted to its time, realizing realtime drawing effect

# time stamping does not have to use time as common variable, can be k*time even f(time) as long as its an one-to-one map
# if the time series is complete (each idx match a tstep), idx simply = tstep - 1 (first output is tstep=1), so
# ts can simply be the tstep array itself, and dt=1, so matching tsteps[i] vs vtk.tstep*1, which is the first strategy
# the second strategy is straight forward by using the time array and derived dt
# we use the first strategy because of possible dt changes during the simulation,
# the output filtered series are already prepended and complete in length in previous example 01_draglift
# in second strategy the ts in fig_f (first argument) is simply time, so in fact no need to pass time array again
