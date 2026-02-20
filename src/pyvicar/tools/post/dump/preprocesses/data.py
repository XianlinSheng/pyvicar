import numpy as np
from collections.abc import Iterable
import pyvicar.tools.post.dump.labels as lb


def prep_field(mesh, field):
    if isinstance(field, lb.FieldVectorVORFromVEL):
        mesh = mesh.compute_derivative(field.vel_name, vorticity=True)
        mesh.rename_array("vorticity", "VOR")
        field_name = "VOR"

    field_name = field.name

    match field:
        case lb.FieldScalar():
            return mesh, field_name
        case lb.FieldVector():
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
            comp_name = f"{field_name}({field.component.name})"
            mesh[comp_name] = comp
            return mesh, comp_name


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
        if c.dump.marker:
            markers = c.dump.marker.latest
        else:
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
