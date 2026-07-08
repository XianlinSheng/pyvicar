from pyvicar.tools.miscellaneous import args
from .basics import ObjPath, FullStatus, PostJob, bcast_if_multiblock, shcopy_mesh
import numpy as np


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
        return f"calc_q({self.out_name})"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshobj = st.f[self.kwargs["mesh"]]

        def calc(meshin):
            mesh = shcopy_mesh(meshin, keep_points=[self.kwargs["vel_name"]])
            mesh = mesh.compute_derivative(self.kwargs["vel_name"], gradient=True)
            grad = mesh.point_data["gradient"]
            grad = grad.reshape(-1, 3, 3)  # 3x3 tensor
            gradt = np.transpose(grad, (0, 2, 1))
            S = 0.5 * (grad + gradt)
            Omega = 0.5 * (grad - gradt)
            # Q = 0.5 (‖Ω‖² - ‖S‖²)
            qfield = 0.5 * (
                np.einsum("ijk,ijk->i", Omega, Omega) - np.einsum("ijk,ijk->i", S, S)
            )

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
        return f"calc_vor({self.out_name})"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshobj = st.f[self.kwargs["mesh"]]

        def calc(meshin):
            mesh = shcopy_mesh(meshin, keep_points=[self.kwargs["vel_name"]])
            mesh = mesh.compute_derivative(self.kwargs["vel_name"], vorticity=True)
            meshin[self.out_name] = mesh["vorticity"]

        bcast_if_multiblock(meshobj, calc)

    def frame_end(self, st: FullStatus):
        pass


class CalcNabla(PostJob):
    def __init__(self, **kwargs):
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "field": "VEL",
                "grad": None,
                "div": None,
                "curl": None,
                "q": None,
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return f"calc_nabla({self.kwargs["field"]})"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshobj = st.f[self.kwargs["mesh"]]

        def calc(meshin):
            mesh = shcopy_mesh(meshin, keep_points=[self.kwargs["field"]])
            mesh = mesh.compute_derivative(
                self.kwargs["field"],
                gradient=self.kwargs["grad"] is not None,
                divergence=self.kwargs["div"] is not None,
                vorticity=self.kwargs["curl"] is not None,
                qcriterion=self.kwargs["q"] is not None,
            )
            if self.kwargs["grad"] is not None:
                meshin[self.kwargs["grad"]] = mesh["gradient"]
            if self.kwargs["div"] is not None:
                meshin[self.kwargs["div"]] = mesh["divergence"]
            if self.kwargs["curl"] is not None:
                meshin[self.kwargs["curl"]] = mesh["vorticity"]
            if self.kwargs["q"] is not None:
                meshin[self.kwargs["q"]] = mesh["qcriterion"]

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
        return f"calc_func({self.out_name})"

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
        return f"calc_nondim_vec({self.out_name})"

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
        return f"calc_nondim_p({self.out_name})"

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
