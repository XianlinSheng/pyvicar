from pyvicar.tools.miscellaneous import args
from .basics import ObjPath, FullStatus, PostJob


class IsoSurf(PostJob):
    def __init__(self, jobname, **kwargs):
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "iso_field": "Q",
                "iso_value": 0.1,
                "cell_to_point": {"run": False, "inplace": True, "keep": True},
                "iso_kwargs": {},
            },
            recursive=True,
            inplace=True,
            throw_unused=True,
        )
        self.jobname = jobname

    def name(self) -> str:
        return self.jobname

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

        iso = mesh.contour(
            isosurfaces=[self.kwargs["iso_value"]],
            scalars=self.kwargs["iso_field"],
            **self.kwargs["iso_kwargs"],
        )
        st.f.set_outputs(self.name(), {"mesh": iso})

    def frame_end(self, st: FullStatus):
        st.f.clear_outputs(self.name())


class Slice(PostJob):
    def __init__(self, jobname, **kwargs):
        self.kwargs = args.add_default(
            kwargs,
            {
                "mesh": ObjPath("read", "mesh"),
                "origin": [None, None, None],
                "normal": "z",
                "clip": None,
                "slice_kwargs": {},
            },
            inplace=True,
            throw_unused=True,
        )
        self.jobname = jobname

    def name(self) -> str:
        return self.jobname

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        mesh = st.f[self.kwargs["mesh"]]

        x1, x2, y1, y2, z1, z2 = mesh.bounds
        origin = args.none_to_default(
            self.kwargs["origin"], [(x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2]
        )
        slice = mesh.slice(origin=origin, normal=self.kwargs["normal"])
        if self.kwargs["clip"] is not None:
            clip = args.none_to_default(clip, [x1, x2, y1, y2, z1, z2])
            slice = slice.clip_box(clip, invert=False)
        st.f.set_outputs(self.name(), {"mesh": slice})

    def frame_end(self, st: FullStatus):
        st.f.clear_outputs(self.name())
