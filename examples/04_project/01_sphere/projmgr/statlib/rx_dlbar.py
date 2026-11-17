from .misc.dlbar import plot_dlbar

mpi_async = True


def stat_rx_dlbar():
    st = 40
    plat = "RC"

    aoas = [0, 5, 10, 20]
    labels = ["Pitch0", "Pitch5", "Pitch10", "Pitch20"]
    cases = [f"rxa{aoa}st{st}c0r120{plat}" for aoa in aoas]

    plot_dlbar(labels=labels, cases=cases, output=f"rx_dlbar_st{st}")
