import numpy as np
import pyvicar.tools.fp as fp


# oclock is the position of camera relative to target, 12 oclock x+ downstream, z+ up
def calc_cam_position(target, l0, r, oclock, pitch, downstream_shift):
    target = np.asarray(target)

    target = target + np.asarray([downstream_shift, 0, 0]) * l0

    pitchrad = pitch * np.pi / 180
    h = r * np.sin(pitchrad)
    r *= np.cos(pitchrad)

    xyrad = -oclock * np.pi / 6
    xy = np.asarray([np.cos(xyrad), np.sin(xyrad)]) * r * l0
    xyz = np.asarray([xy[0], xy[1], h])

    cam = target + xyz

    up_pitchrad = (90 - pitch) * np.pi / 180
    up_xyrad = xyrad + np.pi
    up = np.asarray(
        [
            np.cos(up_pitchrad) * np.cos(up_xyrad),
            np.cos(up_pitchrad) * np.sin(up_xyrad),
            np.sin(up_pitchrad),
        ]
    )

    return [cam, target, up]


def set_cam_compass(
    target=[0, 0, 0],
    l0=1,
    r=4,
    oclock=2,
    pitch=30,
    downstream_shift=1,
    target_f=None,
    l0_f=None,
    r_f=None,
    oclock_f=None,
    pitch_f=None,
    downstream_shift_f=None,
):
    target_f = fp.f_or_uniform_f(target_f, target)
    l0_f = fp.f_or_uniform_f(l0_f, l0)
    r_f = fp.f_or_uniform_f(r_f, r)
    oclock_f = fp.f_or_uniform_f(oclock_f, oclock)
    pitch_f = fp.f_or_uniform_f(pitch_f, pitch)
    downstream_shift_f = fp.f_or_uniform_f(downstream_shift_f, downstream_shift)

    def plotter_f(plotter, c, i, vtk, marker):
        target_t = target_f(c, i, vtk, marker)
        l0_t = l0_f(c, i, vtk, marker)
        r_t = r_f(c, i, vtk, marker)
        oclock_t = oclock_f(c, i, vtk, marker)
        pitch_t = pitch_f(c, i, vtk, marker)
        downstream_shift_t = downstream_shift_f(c, i, vtk, marker)

        plotter.camera_position = calc_cam_position(
            target_t, l0_t, r_t, oclock_t, pitch_t, downstream_shift_t
        )
        return plotter

    return plotter_f


def set_cam_hovering(
    target=[0, 0, 0],
    l0=1,
    r=4,
    downstream_shift=1,
    target_f=None,
    l0_f=None,
    r_f=None,
    downstream_shift_f=None,
):
    target_f = fp.f_or_uniform_f(target_f, target)
    l0_f = fp.f_or_uniform_f(l0_f, l0)
    r_f = fp.f_or_uniform_f(r_f, r)
    downstream_shift_f = fp.f_or_uniform_f(downstream_shift_f, downstream_shift)

    def plotter_f(plotter, c, i, vtk, marker):
        target_t = target_f(c, i, vtk, marker)
        l0_t = l0_f(c, i, vtk, marker)
        r_t = r_f(c, i, vtk, marker)
        downstream_shift_t = downstream_shift_f(c, i, vtk, marker)

        cam0, target0, up = plotter.camera_position
        up = np.asarray(up)
        up /= np.linalg.norm(up)
        normal = np.asarray(cam0) - np.asarray(target0)
        normal /= np.linalg.norm(normal)
        right = np.cross(up, normal)
        target_t = target_t + right * l0_t * downstream_shift_t
        cam = target_t + normal * l0_t * r_t
        plotter.camera_position = [cam, target_t, up]
        return plotter

    return plotter_f
