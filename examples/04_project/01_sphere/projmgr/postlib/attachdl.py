import pyvicar
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
import pyvicar.tools.matplotlib as pvmpl
import re
import numpy as np
import matplotlib.pyplot as plt
from .surfrecon import post_surfrecon

pyvicar.assert_api_version("1.0.2", "1.1.0")

mpi_async = False

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())


def post_attachdl(p):
    post_surfrecon(p)

    c = p.Case(p.name)

    # needs draglift, post.reports post.animations, so almost effectively c.read() all
    c.read()

    draglift_df = c.post.reports["dl"]["csv"].to_pandas()
    surfrecon_df = c.post.reports["surfrecon_lift"]["csv"].to_pandas()

    drag, lift = draglift_df[["drag", "lift"]].to_numpy().T
    drag_rec, lift_rec = surfrecon_df[["drag_max", "lift_max"]].to_numpy().T

    def fig_f(ts, t, drag, lift, drag_rec, lift_rec):
        fig = plt.figure()
        ax = fig.add_subplot()

        t = t / p.T
        ax.plot(t, lift, "r--", label="Lift Sim.")
        ax.plot(t, lift_rec, "r-", label="Lift Approx.")
        ax.plot(t, drag, "b--", label="Drag Sim.")
        ax.plot(t, drag_rec, "b-", label="Drag Approx.")

        ax.axis([0, c.draglift.time1[-1] / p.T, -1.5, 3.5])
        ax.grid(True)
        ax.legend()
        ax.set_xlabel("Time")
        ax.set_ylabel("F/(1/2*rho*U^2*A)")
        ax.set_title("Force Coeff")
        fig.tight_layout()

        return fig

    tsteps = np.arange(c.draglift.nseries) + 1
    adl = c.create_recorder_video(
        tsteps,
        [c.draglift.time1, drag, lift, drag_rec, lift_rec],
        fig_f,
        c.dump.cgns,
        dt=1,
        keep_frames=False,
        out_name="dl",
    )
    aep = c.post.animations["eta_cdp"]
    aew = c.post.animations["eta_wid"]

    # do this before iteration because each post job adds a new element to dict
    # includes = [re.compile(r"^q\_.+$")]
    # excludes = [re.compile(r"^.+\_far\_.+$"), re.compile(r"^.+\_dl$")]
    includes = [re.compile(r"^body\_cdp.*$")]
    excludes = [re.compile(r"^.+\_dl$")]

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
            anim["mp4"].to_canvas(row_height=1 / 2.25)
            # .append_row([c.post.animations["dl"]["mp4"]])
            .append_row([adl["mp4"], aep["mp4"], aew["mp4"]]).to_ffmpeg(),
            outformat="mp4",
        )
