import numpy as np
import pyvista as pv
from dataclasses import dataclass
from enum import Enum
import pyvicar.tools.log as log


class FieldType(Enum):
    Cell = 0
    Point = 1


class Q:
    def use_exist(q_name, q_type=FieldType.Cell):
        return QExist(q_name, q_type)

    def from_vel(vel_type=FieldType.Cell, vel_name="VEL"):
        return QFromVel(vel_name, vel_type)


@dataclass
class QExist(Q):
    q_name: str
    q_type: FieldType


@dataclass
class QFromVel(Q):
    vel_name: str
    vel_type: FieldType


def cell_to_point(mesh):
    if hasattr(cell_to_point, "point_passed"):
        return mesh
    cell_to_point.point_passed = True
    return mesh.cell_data_to_point_data(pass_cell_data=False)


def plot_isoq(
    mesh,
    q=Q.from_vel(),
    iso_value=0.1,
    off_screen=False,
):
    if not isinstance(q, Q):
        raise TypeError(f"Use Q wizard to create argument, but encounter {type(q)}")

    match q:
        case QExist():
            if q.q_type == FieldType.Cell:
                mesh = cell_to_point(mesh)
            qfield = mesh.point_data[q.q_name]
        case QFromVel():
            if q.vel_type == FieldType.Cell:
                mesh = cell_to_point(mesh)
            mesh = mesh.compute_derivative(q.vel_name, gradient=True)
            grad = mesh.point_data[f"gradient"]
            grad = grad.reshape(-1, 3, 3)  # 3x3 tensor
            gradt = np.transpose(grad, (0, 2, 1))
            S = 0.5 * (grad + gradt)
            Omega = 0.5 * (grad - gradt)
            # Q = 0.5 (‖Ω‖² - ‖S‖²)
            qfield = 0.5 * (
                np.einsum("ijk,ijk->i", Omega, Omega) - np.einsum("ijk,ijk->i", S, S)
            )

    mesh.point_data["Q"] = qfield

    contours = mesh.contour(isosurfaces=[iso_value], scalars="Q")
    outline = mesh.outline()

    plotter = pv.Plotter(off_screen=off_screen)
    plotter.add_mesh(outline, color="black", line_width=1)
    if contours.n_points == 0 or contours.n_cells == 0:
        log.log(f"No q isosurfaces after calculation")
    else:
        plotter.add_mesh(contours, color="turquoise", opacity=0.7)
    plotter.add_axes()
    plotter.show_grid()

    return plotter
