import numpy as np


# Rodrigues Formula https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula
def rotate_vector(axis, deg, vec):
    axis = np.asarray(axis)
    vec = np.asarray(vec)
    rad = np.radians(deg)
    k = axis / np.linalg.norm(axis)
    v = vec

    return (
        v * np.cos(rad)
        + np.cross(k, v) * np.sin(rad)
        + k * np.sum(k * v) * (1 - np.cos(rad))
    )


def rotate_plane(xyz0, uxyz, vxyz, center, axis, deg):
    xyz0 = np.asarray(xyz0)
    uxyz = np.asarray(uxyz)
    vxyz = np.asarray(vxyz)
    center = np.asarray(center)
    axis = np.asarray(axis)
    xyz0 = rotate_vector(axis, deg, xyz0 - center) + center
    uxyz = rotate_vector(axis, deg, uxyz)
    vxyz = rotate_vector(axis, deg, vxyz)
    return xyz0, uxyz, vxyz


def uv2xyz(uxyz, vxyz, uv):
    uxyz = np.asarray(uxyz)
    vxyz = np.asarray(vxyz)
    return uxyz * uv[0] + vxyz * uv[1]


def xyz2uv(uxyz, vxyz, xyz, axis=-1):
    uxyz = np.asarray(uxyz)
    vxyz = np.asarray(vxyz)
    xyz = np.asarray(xyz)
    return np.stack(
        [np.sum(uxyz * xyz, axis=axis), np.sum(vxyz * xyz, axis=axis)], axis=axis
    )
