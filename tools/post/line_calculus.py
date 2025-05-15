import pyvista as pv
import numpy as np


def get_full_sample(sample):
    full_sample = sample
    full_sample = full_sample.point_data_to_cell_data(pass_point_data=True)
    full_sample = full_sample.cell_data_to_point_data(pass_cell_data=True)


def get_line_seg_array(line: pv.Line, convert=True):
    if convert:
        line = line.cell_data_to_point_data()
    points = line.points
    x_seg = (points[:-1, :] + points[1:, :]) / 2
    dl_vectors = np.diff(points, axis=0)
    dl_lengths = np.linalg.norm(dl_vectors, axis=1)

    return x_seg, dl_vectors, dl_lengths


def get_line_seg_field_array(line: pv.Line, field: str, convert=True):
    if convert:
        line = line.cell_data_to_point_data()
    x_seg, dl_vectors, dl_lengths = get_line_seg_array(line, convert=False)
    u = line.point_data[field]
    u_seg = (u[:-1] + u[1:]) / 2

    return dl_vectors, dl_lengths, x_seg, u_seg


def line_seg_field(line: pv.Line, field: str, convert=True):
    dl_vectors, dl_lengths, x_seg, u_seg = get_line_seg_field_array(
        line, field, convert=convert
    )
    return u_seg, x_seg


def line_dot(line: pv.Line, field: str, convert=True):
    dl_vectors, dl_lengths, x_seg, u_seg = get_line_seg_field_array(
        line, field, convert=convert
    )
    dl_units = dl_vectors / dl_lengths[:, np.newaxis]
    if len(u_seg.shape) == 1:
        return dl_units * u_seg[:, np.newaxis], x_seg
    else:
        return np.sum(dl_units * u_seg, axis=1), x_seg


def line_cross(line: pv.Line, field: str, convert=True):
    dl_vectors, dl_lengths, x_seg, u_seg = get_line_seg_field_array(
        line, field, convert=convert
    )
    dl_units = dl_vectors / dl_lengths[:, np.newaxis]
    if len(u_seg.shape) == 1:
        return dl_units * u_seg[:, np.newaxis], x_seg
    else:
        return np.cross(dl_units, u_seg, axis=1), x_seg


# ds * u
def integrate_over_line(line: pv.Line, field: str, convert=True):
    dl_vectors, dl_lengths, x_seg, u_seg = get_line_seg_field_array(
        line, field, convert=convert
    )
    if len(u_seg.shape) == 1:
        return np.sum(dl_lengths * u_seg)
    else:
        return np.sum(dl_lengths[:, np.newaxis] * u_seg, axis=0)


# dl dot u
def integrate_over_line_dot(line: pv.Line, field: str, convert=True):
    dl_vectors, dl_lengths, x_seg, u_seg = get_line_seg_field_array(
        line, field, convert=convert
    )
    if len(u_seg.shape) == 1:
        return np.sum(dl_vectors * u_seg[:, np.newaxis], axis=0)
    else:
        return np.einsum("si,si->", dl_vectors, u_seg)


# dl cross u
def integrate_over_line_cross(line: pv.Line, field: str, convert=True):
    dl_vectors, dl_lengths, x_seg, u_seg = get_line_seg_field_array(
        line, field, convert=convert
    )
    if len(u_seg.shape) == 1:
        return np.sum(dl_vectors * u_seg[:, np.newaxis], axis=0)
    else:
        return np.sum(np.cross(dl_vectors, u_seg, axis=1), axis=0)


def line_length(line: pv.Line, convert=True):
    x_seg, dl_vectors, dl_lengths = get_line_seg_array(line, convert=convert)
    return np.sum(dl_lengths)


def avg_over_line(line: pv.Line, field: str, convert=True):
    if convert:
        line = line.cell_data_to_point_data()
    return integrate_over_line(line, field, convert=False) / line_length(
        line, convert=False
    )
