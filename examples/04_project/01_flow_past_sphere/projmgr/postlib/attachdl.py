import pyvicar
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
import pyvicar.tools.matplotlib as pvmpl
import re
import numpy as np
import matplotlib.pyplot as plt

pyvicar.assert_api_version("1.0.2", "1.1.0")

mpi_async = False

pvmpl.set_default(plt_kwargs=pvmpl.font_sizes_l())


def post_attachdl(p):
    c = p.Case(p.name)

    # needs draglift, post.reports post.animations, so almost effectively c.read() all
    c.read()

    draglift_df = c.post.reports["dl"]["csv"].to_pandas()

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
    adl = c.create_recorder_video(
        tsteps,
        [c.draglift.time1, cx, cy, cz],
        fig_f,
        c.dump.vtm,
        dt=1,
        keep_frames=True,
        out_name="dl",
    )

    # do this before iteration because each post job adds a new element to dict
    includes = [re.compile(r"^q\_.+$"), re.compile(r"^slice\_.+$")]
    excludes = [re.compile(r"^.+\_dup\_.+$"), re.compile(r"^.+\_dl$")]

    def is_match(key):
        return any([include.match(key) for include in includes]) and all(
            [not exclude.match(key) for exclude in excludes]
        )

    kas = [(key, anim) for key, anim in c.post.animations.items() if is_match(key)]

    # running multiple ffmpeg in parallel might out of memory,
    # ffmpeg can do multithreads so let one run with more resources
    mpi.set_sync()
    for key, anim in kas:
        log.log(f"Post Attach DL: {key}")
        c.post.animations.get_or_create(f"{key}_dl").video_by_ffmpeg(
            anim["mp4"]
            .to_canvas(row_height=1 / 3)
            .append_row([adl["mp4"]])
            .to_ffmpeg(),
            outformat="mp4",
        )
