import pyvicar
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
import pyvicar.tools.matplotlib as pvmpl
import pyvicar.tools.ffmpeg as pvff
import re
import numpy as np
import matplotlib.pyplot as plt

pyvicar.assert_api_version("1.0.3", "1.1.0")

mpi_async = False

pvmpl.set_default(pvmpl.font_sizes_l() | pvmpl.font_math())


def post_combine(p):
    c = p.Case(p.name)

    c.post.read()
    a = c.post.animations

    # running multiple ffmpeg in parallel might out of memory,
    # ffmpeg can do multithreads so let one run with more resources
    mpi.set_sync()
    c.post.animations.get_or_create(f"q_comb").video_by_ffmpeg(
        pvff.Array(row_height=1080)
        .append_row([a["q_p_o7"]["mp4"], a["q_v_o7"]["mp4"]])
        .append_row([a["q_p_o7_bel"]["mp4"], a["q_v_o7_bel"]["mp4"]])
        .to_ffmpeg(),
        outformat="mp4",
    )
