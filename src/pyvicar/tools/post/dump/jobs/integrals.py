import pyvicar.tools.log as log
from pyvicar.tools.miscellaneous import args
from .basics import (
    ObjPath,
    FullStatus,
    PostJob,
    bcast_if_multiblock,
    shcopy_mesh,
    comps_castup,
    comps_castdown,
)
import numpy as np
import pyvista as pv
from mpi4py import MPI


class SweepDensity(PostJob):
    def __init__(self, phi_f, **kwargs):
        self.phi_f = phi_f
        self.kwargs = args.add_default(
            kwargs,
            {
                "cell_field": None,
                "point_field": None,
                "mesh": ObjPath("read", "mesh"),
                "phi_min": 0,
                "phi_max": 1,
                "phi_n": 100,
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        cell = self.kwargs["cell_field"]
        point = self.kwargs["point_field"]
        names = []
        if cell is not None:
            names.append(f"cell/{cell}")
        if point is not None:
            names.append(f"point/{point}")
        return f"sweep_density({self.kwargs["mesh"].to_str()}/{'|'.join(names)})"

    def global_begin(self, st: FullStatus):
        cell = self.kwargs["cell_field"]
        point = self.kwargs["point_field"]
        if cell is None and point is None:
            raise ValueError(
                f"No field is specified for integral. "
                + f"Either pass cell_field='P' or point_field='P'"
            )

        if cell is not None and point is not None:
            raise ValueError(
                f"Both cell and point fields are given, ambiguous on which to process. "
                + f"Either pass cell_field='P' or point_field='P'"
            )

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        meshes = st.f[self.kwargs["mesh"]]
        out = {}

        phi_min = self.kwargs["phi_min"]
        phi_max = self.kwargs["phi_max"]
        phi_n = self.kwargs["phi_n"]
        dphi = (phi_max - phi_min) / phi_n
        phis = (np.arange(phi_n) + 0.5) * dphi

        def process(mesh, path):
            if self.kwargs["cell_field"]:
                name = self.kwargs["cell_field"]
            else:
                name = self.kwargs["point_field"]
                mesh = shcopy_mesh(mesh, keep_points=[name])
                mesh = mesh.point_data_to_cell_data(pass_point_data=False)

            mesh = mesh.compute_cell_sizes()
            if "Area" in mesh.cell_data:
                meas = mesh.cell_data["Area"]
            elif "Volume" in mesh.cell_data:
                meas = mesh.cell_data["Volume"]
            cell = mesh.cell_data[name]
            cell, ncomps = comps_castup(cell)
            xyz = mesh.cell_centers().points
            phi = self.phi_f(xyz, st)
            iphi = np.clip(np.floor((phi - phi_min) / dphi).astype(int), -1, phi_n) + 1
            pcell = np.zeros((phi_n + 2, ncomps), dtype=cell.dtype)
            pmeas = np.zeros(phi_n + 2)
            np.add.at(pmeas, iphi, meas)
            pmeas /= dphi
            np.add.at(pcell, iphi, cell * meas[:, np.newaxis])
            pcell /= dphi
            out[path] = {
                "phi": phis,
                "measure": pmeas,
                "integral": comps_castdown(pcell),
            }

        bcast_if_multiblock(meshes, process)

        st.f.set_outputs(self.name(), out)

    def frame_end(self, st: FullStatus):
        pass


class TimeAvg(PostJob):
    def __init__(self, case, out_name, obj_path, **kwargs):
        self.case = case
        self.out_name = out_name
        self.obj_path = obj_path
        self.kwargs = args.add_default(
            kwargs,
            {
                "tmin": None,
                "tmax": None,
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return f"time_avg({self.out_name})"

    def global_begin(self, st: FullStatus):
        self.case.draglift.read()
        st.g.set_outputs(self.name(), {"time": self.case.draglift.time1, "init": False})

    def global_end(self, st: FullStatus):
        out = st.g[self.name()]
        comm = MPI.COMM_WORLD
        if not out["init"]:
            shape = None
        else:
            shape = out["v_acc"].shape

        shapes = comm.allgather(shape)
        shapes_set = set(shapes)
        shapes_set.discard(None)
        if len(shapes_set) > 1:
            raise ValueError(
                f"Expected each rank having the same array shape or all-zero, got {shapes}"
            )
        if len(shapes_set) == 0:
            log.log_host(f"Post: TimeAvg Warning: No integrated data")
            return

        shape = next(iter(shapes_set))

        if not out["init"]:
            out["v_acc"] = np.zeros(shape)
            out["t_acc"] = np.array(0, dtype=float)

        comm.Allreduce(MPI.IN_PLACE, out["v_acc"], op=MPI.SUM)
        comm.Allreduce(MPI.IN_PLACE, out["t_acc"], op=MPI.SUM)
        out["v_avg"] = out["v_acc"] / out["t_acc"]

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        out = st.g[self.name()]
        t = out["time"][st.f.read["tstep"] - 1]
        tmin = self.kwargs["tmin"]
        tmax = self.kwargs["tmax"]
        if tmin is not None and t < tmin:
            return
        if tmax is not None and t > tmax:
            return

        if not out["init"]:
            out["v_prev"] = np.ascontiguousarray(st.f[self.obj_path])
            out["t_prev"] = np.array(t, dtype=float)
            out["v_acc"] = np.zeros_like(out["v_prev"])
            out["t_acc"] = np.zeros_like(out["t_prev"])
            out["init"] = True
        else:
            v = np.ascontiguousarray(st.f[self.obj_path])
            t = np.array(t)
            dt = t - out["t_prev"]
            out["v_acc"] += (out["v_prev"] + v) / 2 * dt
            out["t_acc"] += dt
            out["v_prev"] = v
            out["t_prev"] = t

    def frame_end(self, st: FullStatus):
        pass
