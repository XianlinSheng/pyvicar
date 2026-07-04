from pyvicar.tools.miscellaneous import args
from .basics import ObjPath, FullStatus, PostJob
import numpy as np


class Translate(PostJob):
    def __init__(self, xyz, **kwargs):
        self.xyz = xyz
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "bodies"),
                "copy": False,
                "out_name": "translate",
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return self.kwargs["out_name"]

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        mesh = st.f[self.kwargs["mesh"]]
        mesh_new = mesh.translate(self.xyz, inplace=not self.kwargs["copy"])
        if self.kwargs["copy"]:
            st.f.set_outputs(self.name(), {"mesh": mesh_new})

    def frame_end(self, st: FullStatus):
        if self.kwargs["copy"]:
            st.f.clear_outputs(self.name())


class Reflect(PostJob):
    def __init__(self, xyz, normal, **kwargs):
        self.xyz = xyz
        self.normal = normal
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "bodies"),
                "copy": False,
                "out_name": "reflect",
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return self.kwargs["out_name"]

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        mesh = st.f[self.kwargs["mesh"]]
        mesh_new = mesh.reflect(
            point=self.xyz, normal=self.normal, inplace=not self.kwargs["copy"]
        )
        if self.kwargs["copy"]:
            st.f.set_outputs(self.name(), {"mesh": mesh_new})

    def frame_end(self, st: FullStatus):
        if self.kwargs["copy"]:
            st.f.clear_outputs(self.name())


class Rotate(PostJob):
    def __init__(self, xyz, axis, deg, **kwargs):
        self.xyz = xyz
        self.axis = axis
        self.deg = deg
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "bodies"),
                "copy": False,
                "out_name": "reflect",
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return self.kwargs["out_name"]

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        mesh = st.f[self.kwargs["mesh"]]
        mesh_new = mesh.rotate_vector(
            point=self.xyz,
            vector=self.axis,
            angle=self.deg,
            inplace=not self.kwargs["copy"],
        )
        if self.kwargs["copy"]:
            st.f.set_outputs(self.name(), {"mesh": mesh_new})

    def frame_end(self, st: FullStatus):
        if self.kwargs["copy"]:
            st.f.clear_outputs(self.name())
