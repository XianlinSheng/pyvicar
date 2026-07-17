import pyvicar.tools.log as log
from pyvicar.tools.miscellaneous import args
from .basics import ObjPath, FullStatus, PostJob, shcopy_mesh, bcast_if_multiblock
import pyvista as pv
import numpy as np


class ToPoints(PostJob):
    def __init__(self, *meshes, **kwargs):
        self.kwargs = args.add_default(
            kwargs,
            {
                "inplace": True,
                "keep": True,
            },
            inplace=True,
            throw_unused=True,
        )
        self.meshes = meshes

    def name(self) -> str:
        return "to_points"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        out = {}
        for mesh_path in self.meshes:
            mesh = st.f[mesh_path]
            mesh = mesh.cell_data_to_point_data(pass_cell_data=self.kwargs["keep"])
            out[f"{mesh_path.jobname}/{mesh_path.objname}"] = mesh
            if self.kwargs["inplace"]:
                st.f[mesh_path] = mesh

        st.f.set_outputs(self.name(), out)

    def frame_end(self, st: FullStatus):
        if self.kwargs["inplace"]:
            st.f.clear_outputs(self.name())


# return idx_start, so that points[i] is nearly boxed by grid idx [idx_start[i], idx_start[i] + tot_idx)
# (point may not be nearly center or even outside of the box at the grid boundary)
def clamp_box(points, grid, tot_idx=6):
    half = tot_idx // 2
    idx = np.searchsorted(grid, points) - half
    idx = np.clip(idx, 0, grid.shape[0] - tot_idx)
    return idx


def comps_castup(x):
    if x.ndim == 1:
        return x[:, None], 1
    else:
        return x, x.shape[1]


def comps_castdown(x):
    if x.shape[1] == 1:
        return x[:, 0]
    else:
        return x


def reshape_3d(x, nx, ny, nz):
    return np.stack(
        [comp.reshape((nx, ny, nz), order="F") for comp in x.T],
        axis=-1,
    )


class VolToSurf(PostJob):
    def __init__(self, *configs, **kwargs):
        self.configs = [
            args.add_default(
                config,
                {
                    "cell_fields": None,
                    "pos": False,
                    "neg": False,
                    "double": False,
                },
            )
            for config in configs
        ]
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh_vol": ObjPath("read", "mesh"),
                "mesh_surf": ObjPath("read", "bodies"),
                "tot_idx": 6,
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return f"vol_to_surf({self.kwargs["mesh_vol"].to_str()}->{self.kwargs["mesh_surf"].to_str()})"

    def global_begin(self, st: FullStatus):
        if not self.configs:
            log.log(
                f"Post: Warning in VolToSurf: "
                + f"No interpolations are defined, pass dicts like "
                + "{'cell_fields': ['P'], 'neg': True, 'pos': True}"
                + f"to create surface fields"
            )

        for i, config in enumerate(self.configs):
            if not (config["neg"] or config["pos"] or config["double"]):
                log.log(
                    f"Post: Warning in VolToSurf Interp No. {i}: "
                    + f"None of the interp side ['neg', 'pos', 'double'] is enabled,"
                    + f"and thus no fields are defined, pass dicts like "
                    + "{'cell_fields': ['P'], 'neg': True, 'pos': True}"
                    + f"to create surface fields"
                )

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        fields = st.f.read["fields"]
        from pyvicar.case.dump.vtk import VTK, VTM

        # no heavy file read will happen
        if isinstance(fields, (VTK, VTM)):
            raise TypeError(
                f"Vol space must be on a structured mesh, got {fields}. "
                + f"Unstruc interpolation is removed due to time complexity. "
                + f"Use c.dump.vtm.to_vtrs(npx, npy, keep_vtms=True) to combine and use c.dump.vtr."
            )

    def frame_proc(self, st: FullStatus):
        if not self.configs:
            return

        vol = st.f[self.kwargs["mesh_vol"]]
        surfs = st.f[self.kwargs["mesh_surf"]]
        nx, ny, nz = vol.dimensions
        nxc, nyc, nzc = nx - 1, ny - 1, nz - 1
        xyz = vol.points
        x = xyz[:, 0].reshape((nx, ny, nz), order="F")[:, 0, 0]
        y = xyz[:, 1].reshape((nx, ny, nz), order="F")[0, :, 0]
        z = xyz[:, 2].reshape((nx, ny, nz), order="F")[0, 0, :]
        x = (x[1:] + x[:-1]) / 2
        y = (y[1:] + y[:-1]) / 2
        z = (z[1:] + z[:-1]) / 2
        tot_idx = self.kwargs["tot_idx"]

        def process(surf, path):
            idx_x = clamp_box(surf.points[:, 0], x, tot_idx=tot_idx)
            idx_y = clamp_box(surf.points[:, 1], y, tot_idx=tot_idx)
            idx_z = clamp_box(surf.points[:, 2], z, tot_idx=tot_idx)
            npoints = surf.points.shape[0]
            eps = 1e-6
            norm = (
                shcopy_mesh(surf, keep_cells=["NORM"])
                .cell_data_to_point_data(pass_cell_data=False)
                .point_data["NORM"]
            )

            for config in self.configs:
                if not (config["pos"] or config["neg"] or config["double"]):
                    return

                names = (
                    list(vol.cell_data.keys())
                    if config["cell_fields"] is None
                    else config["cell_fields"]
                )
                for name in names:
                    # uniform treatment scalar/vector/tensor into [i, j, k, comp]
                    volc, ncomp = comps_castup(vol.cell_data[name])
                    volc = reshape_3d(volc, nxc, nyc, nzc)

                    if config["neg"]:
                        num_neg = np.zeros((npoints, ncomp))
                        den_neg = np.zeros(npoints)

                    if config["pos"]:
                        num_pos = np.zeros((npoints, ncomp))
                        den_pos = np.zeros(npoints)

                    if config["double"]:
                        num = np.zeros((npoints, ncomp))
                        den = np.zeros(npoints)

                    # this is ~50 to ~500 lightweight loop over stencils
                    dis, djs, dks = np.meshgrid(
                        np.arange(tot_idx),
                        np.arange(tot_idx),
                        np.arange(tot_idx),
                        indexing="ij",
                    )
                    for di, dj, dk in zip(dis.ravel(), djs.ravel(), dks.ravel()):
                        stcl_i = idx_x + di
                        stcl_j = idx_y + dj
                        stcl_k = idx_z + dk

                        dx = x[stcl_i] - surf.points[:, 0]
                        dy = y[stcl_j] - surf.points[:, 1]
                        dz = z[stcl_k] - surf.points[:, 2]
                        dxyz = np.stack((dx, dy, dz), axis=-1)

                        d2 = dx * dx + dy * dy + dz * dz
                        # IDW
                        w = 1.0 / np.maximum(d2, eps) ** 2

                        # dot == 0 is ill-formed and cannot guarantee the side of the value so is excluded both
                        if config["neg"]:
                            w_neg = w * (np.sum(dxyz * norm, axis=-1) < 0)
                            num_neg += (
                                w_neg[:, np.newaxis] * volc[stcl_i, stcl_j, stcl_k, :]
                            )
                            den_neg += w_neg

                        if config["pos"]:
                            w_pos = w * (np.sum(dxyz * norm, axis=-1) > 0)
                            num_pos += (
                                w_pos[:, np.newaxis] * volc[stcl_i, stcl_j, stcl_k, :]
                            )
                            den_pos += w_pos

                        if config["double"]:
                            num += w[:, np.newaxis] * volc[stcl_i, stcl_j, stcl_k, :]
                            den += w

                    if config["neg"]:
                        surf.point_data[f"{name}(SURF_NEG)"] = comps_castdown(
                            num_neg / den_neg[:, np.newaxis]
                        )

                    if config["pos"]:
                        surf.point_data[f"{name}(SURF_POS)"] = comps_castdown(
                            num_pos / den_pos[:, np.newaxis]
                        )

                    if config["double"]:
                        surf.point_data[f"{name}(SURF)"] = comps_castdown(
                            num / den[:, np.newaxis]
                        )

        bcast_if_multiblock(surfs, process)

    def frame_end(self, st: FullStatus):
        pass


# # legacy vtk impl, algorithm time complexity unacceptable
# class VolToSurf(PostJob):
#     def __init__(self, radius, **kwargs):
#         self.radius = radius
#         self.kwargs = args.add_default(
#             kwargs,
#             {
#                 "mesh_vol": ObjPath("read", "mesh"),
#                 "mesh_surf": ObjPath("read", "bodies"),
#                 "pos": False,
#                 "neg": False,
#                 "double": False,
#             },
#             inplace=True,
#             throw_unused=True,
#         )

#     def name(self) -> str:
#         return "vol_to_surf"

#     def global_begin(self, st: FullStatus):
#         pass

#     def global_end(self, st: FullStatus):
#         pass

#     def frame_begin(self, st: FullStatus):
#         pass

#     def frame_proc(self, st: FullStatus):
#         if not (self.kwargs["pos"] or self.kwargs["neg"] or self.kwargs["double"]):
#             return

#         def process(surf):
#             xmin, xmax, ymin, ymax, zmin, zmax = surf.bounds

#             xmin -= self.radius
#             xmax += self.radius
#             ymin -= self.radius
#             ymax += self.radius
#             zmin -= self.radius
#             zmax += self.radius

#             roi = vol.clip_box(
#                 bounds=(xmin, xmax, ymin, ymax, zmin, zmax), invert=False, crinkle=True
#             )

#             cc = roi.cell_centers()
#             cc = cc.cell_data_to_point_data()
#             dist = cc.compute_implicit_distance(surf)
#             d = dist["implicit_distance"]

#             mask_pos = d > 0
#             mask_neg = ~mask_pos

#             cc_pos = cc.extract_points(mask_pos)
#             cc_neg = cc.extract_points(mask_neg)

#             # some output name might not be processed well, so rename it here
#             for name in list(cc_pos.point_data):
#                 cc_pos.rename_array(name, f"{name}(SURF_POS)")
#             for name in list(cc_neg.point_data):
#                 cc_neg.rename_array(name, f"{name}(SURF_NEG)")
#             for name in list(cc.point_data):
#                 cc.rename_array(name, f"{name}(SURF)")

#             if self.kwargs["pos"]:
#                 surf_pos = surf.interpolate(cc_pos, sharpness=2, radius=self.radius)
#                 for name in surf_pos.point_data:
#                     surf.point_data[name] = surf_pos.point_data[name]
#             if self.kwargs["neg"]:
#                 surf_neg = surf.interpolate(cc_neg, sharpness=2, radius=self.radius)
#                 for name in surf_neg.point_data:
#                     surf.point_data[name] = surf_neg.point_data[name]
#             if self.kwargs["double"]:
#                 surf_double = surf.interpolate(cc, sharpness=2, radius=self.radius)
#                 for name in surf_double.point_data:
#                     surf.point_data[name] = surf_double.point_data[name]

#         vol = st.f[self.kwargs["mesh_vol"]]
#         surfs = st.f[self.kwargs["mesh_surf"]]

#         if isinstance(surfs, pv.MultiBlock):
#             for surf in surfs:
#                 process(surf)
#         else:
#             surf = surfs
#             process(surf)

#     def frame_end(self, st: FullStatus):
#         pass
