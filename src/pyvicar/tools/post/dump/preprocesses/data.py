import numpy as np
import pyvista as pv
from collections.abc import Iterable
import pyvicar.tools.post.dump.labels as lb
from pyvicar.tools.collections import struct


def prep_field(mesh, field):
    match field:
        case lb.FieldRenameScalar():
            mesh.rename_array(field.orig, field.name)
        case lb.FieldVectorVORFromVEL():
            # combine partitions otherwise vorticity is incorrect at partition boundary
            if isinstance(mesh, pv.MultiBlock):
                mesh = mesh.combine().clean(tolerance=1e-12)
            mesh = mesh.compute_derivative(field.vel_name, vorticity=True)
            mesh.rename_array("vorticity", field.name)

    if isinstance(field, lb.FieldVector):
        vec = mesh[field.name]
        match field.component:
            case lb.VecComp.X:
                comp = vec[:, 0]
            case lb.VecComp.Y:
                comp = vec[:, 1]
            case lb.VecComp.Z:
                comp = vec[:, 2]
            case lb.VecComp.MAG:
                comp = np.linalg.norm(vec, axis=1)
        comp_name = field.fullname()
        mesh[comp_name] = comp

    return mesh


def get_vtks_markers(c, vtks, markers):
    if vtks is None:
        c.dump.vtm.read()
        if c.dump.vtm:
            vtks = c.dump.vtm.latest
        else:
            raise Exception(
                f"Create Video: No VTM available, or pass VTK lists by vtks=..."
            )

    if markers is None:
        c.dump.marker.read()
        markers = [None] * len(vtks)

    if not isinstance(vtks, Iterable):
        vtks = [vtks]

    if not isinstance(markers, Iterable):
        markers = [markers]

    if len(vtks) != len(markers):
        raise Exception(
            f"Length of vtk and marker list not match: {len(vtks)} and {len(markers)}"
        )

    return c, vtks, markers


def check_or_broadcast(names, inputs):
    if isinstance(names, list):
        n = len(names)

        name_set = set(names)
        if len(name_set) != n:
            raise Exception(f"Got duplicated names in {names}")

        if isinstance(inputs, list) and len(inputs) != n:
            raise Exception(
                f"Inputs should match with output name list, expected a {n}-value list, got {inputs}"
            )

        if not isinstance(inputs, list):
            inputs = [inputs] * n

    else:
        if isinstance(inputs, list):
            raise TypeError(
                f"Inputs should match with output name, expected a single object, got list {inputs}"
            )

    return inputs


class Style(struct):
    pass


def dispatch_styles(names, **configs):
    configs = {
        key: check_or_broadcast(names, config) for key, config in configs.items()
    }
    configs["name"] = names
    keys = configs.keys()
    if isinstance(names, list):
        transposes = [dict(zip(keys, values)) for values in zip(*configs.values())]
        return [Style.from_dict(transpose) for transpose in transposes]
    else:
        return [Style.from_dict(configs)]


def calc_surf_data(mesh, surf, radius, pos=True, neg=True, double=True):
    if not (pos or neg or double):
        return

    xmin, xmax, ymin, ymax, zmin, zmax = surf.bounds

    xmin -= radius
    xmax += radius
    ymin -= radius
    ymax += radius
    zmin -= radius
    zmax += radius

    roi = mesh.clip_box(
        bounds=(xmin, xmax, ymin, ymax, zmin, zmax), invert=False, crinkle=True
    )

    cc = roi.cell_centers()
    cc = cc.cell_data_to_point_data()
    dist = cc.compute_implicit_distance(surf)
    d = dist["implicit_distance"]

    mask_pos = d > 0
    mask_neg = ~mask_pos

    cc_pos = cc.extract_points(mask_pos)
    cc_neg = cc.extract_points(mask_neg)

    # some output name might not be processed well, so rename it here
    for name in list(cc_pos.point_data):
        cc_pos.rename_array(name, f"{name}(SURF_POS)")
    for name in list(cc_neg.point_data):
        cc_neg.rename_array(name, f"{name}(SURF_NEG)")
    for name in list(cc.point_data):
        cc.rename_array(name, f"{name}(SURF)")

    if pos:
        surf_pos = surf.interpolate(cc_pos, sharpness=2, radius=radius)
        for name in surf_pos.point_data:
            surf.point_data[name] = surf_pos.point_data[name]
    if neg:
        surf_neg = surf.interpolate(cc_neg, sharpness=2, radius=radius)
        for name in surf_neg.point_data:
            surf.point_data[name] = surf_neg.point_data[name]
    if double:
        surf_double = surf.interpolate(cc, sharpness=2, radius=radius)
        for name in surf_double.point_data:
            surf.point_data[name] = surf_double.point_data[name]
