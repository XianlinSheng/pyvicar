from pyvicar.tools.miscellaneous import args
from .basics import ObjPath, FullStatus, PostJob


class ToPoints(PostJob):
    def __init__(self, *meshes, **kwargs):
        self.kwargs = args.add_default(
            kwargs,
            {
                "inplace": True,
                "keep": False,
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
