from pyvicar.tools.miscellaneous import args
from .basics import ObjPath, FullStatus, PostJob
import numpy as np


class CalcQ(PostJob):
    def __init__(self, **kwargs):
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "out_name": "Q",
                "vel_name": "VEL",
                "cell_to_point": {"run": False, "inplace": True, "keep": True},
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
        mesh = st.f[self.kwargs["mesh"]]
        if self.kwargs["cell_to_point"]["run"]:
            mesh = mesh.cell_data_to_point_data(
                pass_cell_data=self.kwargs["cell_to_point"]["keep"]
            )
            if self.kwargs["cell_to_point"]["inplace"]:
                st.f[self.kwargs["mesh"]] = mesh

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

        mesh.point_data[self.kwargs["out_name"]] = qfield
        del mesh.point_data["gradient"]
        st.f[self.kwargs["mesh"]] = mesh

    def frame_end(self, st: FullStatus):
        pass


class CalcVor(PostJob):
    def __init__(self, **kwargs):
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "out_name": "VOR",
                "vel_name": "VEL",
                "cell_to_point": {"run": False, "inplace": True, "keep": True},
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
        mesh = st.f[self.kwargs["mesh"]]
        if self.kwargs["cell_to_point"]["run"]:
            mesh = mesh.cell_data_to_point_data(
                pass_cell_data=self.kwargs["cell_to_point"]["keep"]
            )
            if self.kwargs["cell_to_point"]["inplace"]:
                st.f[self.kwargs["mesh"]] = mesh

        mesh = mesh.compute_derivative(self.kwargs["vel_name"], vorticity=True)
        mesh.rename_array("vorticity", self.kwargs["out_name"])
        st.f[self.kwargs["mesh"]] = mesh

    def frame_end(self, st: FullStatus):
        pass


class CalcFunc(PostJob):
    def __init__(self, names, f, **kwargs):
        self.names = names
        self.f = f
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "out_name": "OUT",
                "cell_to_point": {"run": False, "inplace": True, "keep": True},
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
        mesh = st.f[self.kwargs["mesh"]]
        if self.kwargs["cell_to_point"]["run"]:
            mesh = mesh.cell_data_to_point_data(
                pass_cell_data=self.kwargs["cell_to_point"]["keep"]
            )
            if self.kwargs["cell_to_point"]["inplace"]:
                st.f[self.kwargs["mesh"]] = mesh

        inputs = [mesh.point_data[name] for name in self.names]
        mesh.point_data[self.kwargs["out_name"]] = self.f(*inputs)

    def frame_end(self, st: FullStatus):
        pass
