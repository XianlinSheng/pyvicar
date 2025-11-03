import pyvista as pv
import numpy as np
from dataclasses import dataclass
from enum import Enum
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi


class QBase:
    pass


@dataclass
class QExist(QBase):
    q_name: str


@dataclass
class QFromVel(QBase):
    vel_name: str


class Q:
    def use_exist(q_name):
        return QExist(q_name)

    def from_vel(vel_name="VEL"):
        return QFromVel(vel_name)


# make the contour mesh
def create_isoq(
    mesh,
    q=Q.from_vel(),
    iso_value=0.1,
):
    if not isinstance(q, QBase):
        raise TypeError(f"Use Q wizard to create argument, but encounter {type(q)}")

    mesh = mesh.cell_data_to_point_data(pass_cell_data=False)

    match q:
        case QExist():
            qfield = mesh.point_data[q.q_name]
        case QFromVel():
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

    return mesh.contour(isosurfaces=[iso_value], scalars="Q")


@dataclass
class FieldBase:
    name: str


class FieldScalar(FieldBase):
    pass


class VecComp(Enum):
    X = 0
    Y = 1
    Z = 2
    MAG = 3


@dataclass
class FieldVector(FieldBase):
    component: VecComp


@dataclass
class FieldVectorVORFromVEL(FieldVector):
    vel_name: str


class Field:
    def scalar(name):
        return FieldScalar(name)

    def vector(name, component="mag"):
        return FieldVector(name, VecComp[component.upper()])

    def vor_from_vel(vel_name, component="z"):
        return FieldVectorVORFromVEL(
            "VOR", component=VecComp[component.upper()], vel_name=vel_name
        )


class ColorBase:
    pass


@dataclass
class ColorUniform(ColorBase):
    name: str


@dataclass
class ColorField(ColorBase):
    field: Field
    cmap: str
    clim: None | list
    scalar_bar_args: None | dict


class Color:
    def uniform(name="turquoise"):
        return ColorUniform(name)

    def field(
        fieldobj,
        cmap="coolwarm",
        clim=None,
        scalar_bar_args={
            "vertical": True,
            "label_font_size": 40,
            "title_font_size": 40,
        },
    ):
        if not isinstance(fieldobj, FieldBase):
            raise TypeError(
                f"Use Field wizard to create argument, but encounter {type(fieldobj)}"
            )
        return ColorField(fieldobj, cmap, clim, scalar_bar_args)


def prep_field(mesh, field):
    if isinstance(field, FieldVectorVORFromVEL):
        mesh = mesh.compute_derivative(field.vel_name, vorticity=True)
        mesh.rename_array("vorticity", "VOR")
        field_name = "VOR"

    field_name = field.name

    match field:
        case FieldScalar():
            return mesh, field_name
        case FieldVector():
            vec = mesh[field.name]
            match field.component:
                case VecComp.X:
                    comp = vec[:, 0]
                case VecComp.Y:
                    comp = vec[:, 1]
                case VecComp.Z:
                    comp = vec[:, 2]
                case VecComp.MAG:
                    comp = np.linalg.norm(vec, axis=1)
            comp_name = f"{field_name}({field.component.name})"
            mesh[comp_name] = comp
            return mesh, comp_name


# quick generate
def gen_isoq_video(
    vtklist,
    markers=None,
    marker_f=lambda m: m,
    plotter_f=lambda p: p,
    iso_opacity=0.5,
    iso_color=Color.field(Field.vector("VEL")),
    keep_frames=True,
    out_name="q",
):
    if not isinstance(iso_color, ColorBase):
        raise TypeError(
            f"Use Color wizard to create argument, but encounter {type(iso_color)}"
        )
    c = vtklist.case
    c.post.enable()
    c.post.animations.enable()
    a = c.post.animations.get_or_create(out_name)
    a.frames.enable()

    if not vtklist:
        return a

    mpi.set_async()

    if markers is None:
        markers = [None] * len(vtklist)

    for vtk, marker in mpi.dispatch(zip(vtklist, markers)):
        log.log(
            f"gen_isoq_video: posting frame {vtk}{f' with {marker}' if marker is not None else ''}"
        )

        mesh = vtk.to_pyvista()
        plotter = pv.Plotter(off_screen=True)

        if marker is not None:
            bodies = marker.to_pyvista_multiblocks()
            bodies = marker_f(bodies)
            for body in bodies:
                plotter.add_mesh(body)

        contours = create_isoq(mesh)
        if contours.n_points == 0 or contours.n_cells == 0:
            log.log(f"gen_isoq_video: No q isosurfaces after calculation")
        else:
            match iso_color:
                case ColorUniform():
                    plotter.add_mesh(
                        contours,
                        color=iso_color.name,
                        opacity=iso_opacity,
                        smooth_shading=True,
                    )
                case ColorField():
                    contours, field_name = prep_field(contours, iso_color.field)
                    plotter.add_mesh(
                        contours,
                        scalars=field_name,
                        cmap=iso_color.cmap,
                        clim=iso_color.clim,
                        show_scalar_bar=True,
                        opacity=iso_opacity,
                        scalar_bar_args=iso_color.scalar_bar_args,
                        smooth_shading=True,
                    )

        outline = mesh.outline()
        plotter.add_mesh(outline, color="black", line_width=1)
        plotter.add_axes()
        plotter.show_grid()

        plotter = plotter_f(plotter)

        a.frames.frame_by_pyvista(vtk.seriesi, plotter, window_size=[3840, 2160])

        plotter.close()
        plotter.deep_clean()
        del plotter

        pv.close_all()

    mpi.set_sync()

    a.read()
    mpi.barrier()
    a = c.post.animations[out_name]
    a.frames.to_video(outformat="mp4")
    if not keep_frames:
        del a.frames
    mpi.barrier()

    return a


def add_default_for_none(passl, defaultl):
    return [
        passv if passv is not None else defaultv
        for passv, defaultv in zip(passl, defaultl)
    ]


# make the slice contour
def create_slice(
    mesh,
    normal="z",
    origin=[None, None, None],
    clip=None,  # [x1, x2, y1, y2, z1, z2]
):
    x1, x2, y1, y2, z1, z2 = mesh.bounds
    origin = add_default_for_none(origin, [(x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2])
    slice = mesh.slice(origin=origin, normal=normal)
    if clip is not None:
        clip = add_default_for_none(clip, [x1, x2, y1, y2, z1, z2])
        slice = slice.clip_box(clip, invert=False)

    return slice


# quick generate
def gen_slicecontour_video(
    vtklist,
    markers=None,
    normal="z",
    origin=[None, None, None],
    clip=None,
    marker_f=lambda m: m,
    plotter_f=lambda p: p,
    contour_color=Color.field(Field.vector("VEL")),
    keep_frames=True,
    out_name="vel",
):
    if not isinstance(contour_color, ColorBase):
        raise TypeError(
            f"Use Color wizard to create argument, but encounter {type(contour_color)}"
        )
    c = vtklist.case
    c.post.enable()
    c.post.animations.enable()
    a = c.post.animations.get_or_create(out_name)
    a.frames.enable()

    if not vtklist:
        return a

    mpi.set_async()

    if markers is None:
        markers = [None] * len(vtklist)

    for vtk, marker in mpi.dispatch(zip(vtklist, markers)):
        log.log(
            f"gen_slicecontour_video: posting frame {vtk}{f' with {marker}' if marker is not None else ''}"
        )

        mesh = vtk.to_pyvista()
        mesh = mesh.cell_data_to_point_data(pass_cell_data=False)
        plotter = pv.Plotter(off_screen=True)

        if marker is not None:
            bodies = marker.to_pyvista_multiblocks()
            bodies = marker_f(bodies)
            for body in bodies:
                plotter.add_mesh(body)

        if isinstance(contour_color, ColorField):
            mesh, field_name = prep_field(mesh, contour_color.field)

        slice = create_slice(mesh, normal, origin, clip)
        if slice.n_points == 0 or slice.n_cells == 0:
            log.log(f"gen_slicecontour_video: Empty slice")
        else:
            match contour_color:
                case ColorUniform():
                    plotter.add_mesh(
                        slice,
                        color=contour_color.name,
                        smooth_shading=True,
                    )
                case ColorField():
                    plotter.add_mesh(
                        slice,
                        scalars=field_name,
                        cmap=contour_color.cmap,
                        clim=contour_color.clim,
                        show_scalar_bar=True,
                        scalar_bar_args=contour_color.scalar_bar_args,
                        smooth_shading=True,
                    )

        # looking at the positive side, normal points to camera
        plotter.camera_position = normal
        plotter.camera.ParallelProjectionOn()
        # plotter.camera.zoom(1.5)
        plotter.add_axes()
        plotter.show_grid()

        plotter = plotter_f(plotter)

        a.frames.frame_by_pyvista(vtk.seriesi, plotter, window_size=[3840, 2160])

        plotter.close()
        plotter.deep_clean()
        del plotter

        pv.close_all()

    mpi.set_sync()

    a.read()
    mpi.barrier()
    a = c.post.animations[out_name]
    a.frames.to_video(outformat="mp4")
    if not keep_frames:
        del a.frames
    mpi.barrier()

    return a
