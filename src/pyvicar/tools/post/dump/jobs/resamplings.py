from pyvicar.tools.miscellaneous import args
from .basics import ObjPath, FullStatus, PostJob
import pyvista as pv


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


class VolToSurf(PostJob):
    def __init__(self, radius, **kwargs):
        self.radius = radius
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh_vol": ObjPath("read", "mesh"),
                "mesh_surf": ObjPath("read", "bodies"),
                "pos": False,
                "neg": False,
                "double": False,
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return "vol_to_surf"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        if not (self.kwargs["pos"] or self.kwargs["neg"] or self.kwargs["double"]):
            return

        def process(surf):
            xmin, xmax, ymin, ymax, zmin, zmax = surf.bounds

            xmin -= self.radius
            xmax += self.radius
            ymin -= self.radius
            ymax += self.radius
            zmin -= self.radius
            zmax += self.radius

            roi = vol.clip_box(
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

            if self.kwargs["pos"]:
                surf_pos = surf.interpolate(cc_pos, sharpness=2, radius=self.radius)
                for name in surf_pos.point_data:
                    surf.point_data[name] = surf_pos.point_data[name]
            if self.kwargs["neg"]:
                surf_neg = surf.interpolate(cc_neg, sharpness=2, radius=self.radius)
                for name in surf_neg.point_data:
                    surf.point_data[name] = surf_neg.point_data[name]
            if self.kwargs["double"]:
                surf_double = surf.interpolate(cc, sharpness=2, radius=self.radius)
                for name in surf_double.point_data:
                    surf.point_data[name] = surf_double.point_data[name]

        vol = st.f[self.kwargs["mesh_vol"]]
        surfs = st.f[self.kwargs["mesh_surf"]]

        if isinstance(surfs, pv.MultiBlock):
            for surf in surfs:
                process(surf)
        else:
            surf = surfs
            process(surf)

    def frame_end(self, st: FullStatus):
        pass
