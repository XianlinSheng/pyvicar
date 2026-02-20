import numpy as np


def resolution_to_size(resolution):
    presets = {
        "hd720": [1280, 720],
        "hd1080": [1920, 1080],
        "4k": [3840, 2160],
        "8k": [7680, 4320],
    }
    if isinstance(resolution, str):
        resolution = presets[resolution.lower()]
    elif isinstance(resolution, int):
        resolution = [resolution, resolution]

    return resolution


def normal_to_plane(normal):
    mapping = {"x": "yz", "y": "xz", "z": "xy"}
    return mapping[normal.lower()] if isinstance(normal, str) else normal


def vecstr_to_array(vec):
    mapping = {"x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}
    return np.asarray(mapping[vec.lower()] if isinstance(vec, str) else vec)
