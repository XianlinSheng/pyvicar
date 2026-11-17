import numpy as np
import projmgr.studies as studies

def get_stab(code):
    p = studies.to_params(code)
    c = p.Case(p.name)
    c.draglift.read()

    tn = c.draglift[1].time.ravel()[-1]

    dl = c.draglift.proc(
        cut=[tn - 0.2 * p.T, None],
        sum_force=True,
        sum_moment=False,
        sum_power=False,
        sum_area=False,
        filter_cutoff_period=0.05 * p.T,
    )

    area = np.max(dl.area[0])
    return {
        "drag": np.mean(dl.cx[0] / area),
        "span": np.mean(dl.cy[0] / area),
        "lift": np.mean(dl.cz[0] / area),
    }


def get_max(code):
    p = studies.to_params(code)
    c = p.Case(p.name)
    c.draglift.read()

    dl = c.draglift.proc(
        cut=[0.1 * p.T, None],
        sum_force=True,
        sum_moment=False,
        sum_power=False,
        sum_area=False,
        filter_cutoff_period=0.05 * p.T,
    )

    area = np.max(dl.area[0])
    return {
        "drag": dl.cx[0][np.argmax(np.abs(dl.cx[0]))] / area,
        "span": dl.cy[0][np.argmax(np.abs(dl.cy[0]))] / area,
        "lift": dl.cz[0][np.argmax(np.abs(dl.cz[0]))] / area,
    }

