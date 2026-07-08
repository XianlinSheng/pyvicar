from pyvicar.tools.miscellaneous import args
from .basics import ObjPath, FullStatus, PostJob
import numpy as np
import pyvista as pv


def bcast_if_multiblock(mesh, f):
    if isinstance(mesh, pv.MultiBlock):
        for mesh1 in mesh:
            bcast_if_multiblock(mesh1, f)
    else:
        f(mesh)


class CalcQ(PostJob):
    def __init__(self, out_name, **kwargs):
        self.out_name = out_name
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "vel_name": "VEL",
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return "calc_q"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshobj = st.f[self.kwargs["mesh"]]

        def calc(meshin):
            mesh = meshin.compute_derivative(self.kwargs["vel_name"], gradient=True)
            grad = mesh.point_data["gradient"]
            grad = grad.reshape(-1, 3, 3)  # 3x3 tensor
            gradt = np.transpose(grad, (0, 2, 1))
            S = 0.5 * (grad + gradt)
            Omega = 0.5 * (grad - gradt)
            # Q = 0.5 (‖Ω‖² - ‖S‖²)
            qfield = 0.5 * (
                np.einsum("ijk,ijk->i", Omega, Omega) - np.einsum("ijk,ijk->i", S, S)
            )

            mesh.point_data[self.out_name] = qfield
            meshin.point_data[self.out_name] = qfield

        bcast_if_multiblock(meshobj, calc)

    def frame_end(self, st: FullStatus):
        pass


class CalcVor(PostJob):
    def __init__(self, out_name, **kwargs):
        self.out_name = out_name
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "vel_name": "VEL",
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return "calc_vor"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshobj = st.f[self.kwargs["mesh"]]

        def calc(mesh):
            mesh = mesh.compute_derivative(self.kwargs["vel_name"], vorticity=True)
            mesh.rename_array("vorticity", self.out_name)
            st.f[self.kwargs["mesh"]] = mesh

        bcast_if_multiblock(meshobj, calc)

    def frame_end(self, st: FullStatus):
        pass


class CalcFunc(PostJob):
    def __init__(self, out_name, names, f, **kwargs):
        self.out_name = out_name
        self.names = names
        self.f = f
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return "calc_func"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshobj = st.f[self.kwargs["mesh"]]

        def calc(mesh):
            inputs = [mesh.point_data[name] for name in self.names]
            mesh.point_data[self.out_name] = self.f(*inputs)

        bcast_if_multiblock(meshobj, calc)

    def frame_end(self, st: FullStatus):
        pass


class CalcNondimVec(PostJob):
    def __init__(self, out_name, **kwargs):
        self.out_name = out_name
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "vec_name": "VEL",
                "vec0": 1,
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return "calc_nondim_vel"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshobj = st.f[self.kwargs["mesh"]]

        def calc(mesh):
            mesh[self.out_name] = mesh[self.kwargs["vec_name"]] / self.kwargs["vec0"]

        bcast_if_multiblock(meshobj, calc)

    def frame_end(self, st: FullStatus):
        pass


class CalcNondimP(PostJob):
    def __init__(self, out_name, **kwargs):
        self.out_name = out_name
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "p_name": "P",
                "p0": None,
                "vel0": 1,
                "rho0": 1,
                "div2": True,
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return "calc_nondim_p"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshobj = st.f[self.kwargs["mesh"]]

        def calc(mesh):
            if self.kwargs["p0"] is None:
                p0 = self.kwargs["vel0"] ** 2 * self.kwargs["rho0"]
                if self.kwargs["div2"]:
                    p0 /= 2
            else:
                p0 = self.kwargs["p0"]

            mesh[self.out_name] = mesh[self.kwargs["p_name"]] / p0

        bcast_if_multiblock(meshobj, calc)

    def frame_end(self, st: FullStatus):
        pass
