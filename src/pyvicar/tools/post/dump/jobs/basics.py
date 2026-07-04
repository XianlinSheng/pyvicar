import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
import pyvicar.tools.post.dump.labels as lb
from pyvicar.tools.miscellaneous import args
from pyvicar.tools.post.dump.preprocesses.conversions import resolution_to_size
import pyvista as pv
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass


class JobOutputError(Exception):
    pass


@dataclass
class ObjPath:
    jobname: str
    objname: str


# this manages the outputs of jobs
class Status:
    def __init__(self):
        self._outputs = {}

    def jobs(self):
        return self._outputs.keys()

    def has_outputs(self, job_name: str):
        return job_name in self._outputs

    def set_outputs(self, job_name: str, outputs: dict):
        self._outputs[job_name] = outputs
        return self._outputs[job_name]

    def clear_outputs(self, job_name: str):
        self._outputs[job_name] = {}

    def __getitem__(self, job_name: str | ObjPath):
        if isinstance(job_name, str):
            try:
                return self._outputs[job_name]
            except KeyError:
                raise JobOutputError(
                    f"Requested PostJob '{job_name}' but either it was not called or it did not set an output in Status. Add the PostJob before this request or check the implementation"
                )
        elif isinstance(job_name, ObjPath):
            path = job_name
            try:
                return self[path.jobname][path.objname]
            except KeyError:
                raise JobOutputError(
                    f"Requested PostJob output '{path.jobname}'/'{path.objname}' but either the job was not called or it did not set the required output. Add the PostJob before this request or check the job output format or check the implementation"
                )
        else:
            raise TypeError(
                f"Expected a str for job_name or an ObjPath(jobname, objname) as quick access of [jobname][objname], got {type(job_name)} '{job_name}'"
            )

    def __setitem__(self, job_name: str | ObjPath, v):
        if isinstance(job_name, str) and isinstance(v, dict):
            try:
                self._outputs[job_name] = v
            except KeyError:
                raise JobOutputError(
                    f"Requested PostJob '{job_name}' but either it was not called or it did not set an output in Status. Add the PostJob before this request or check the implementation"
                )
        elif isinstance(job_name, ObjPath):
            path = job_name
            self[path.jobname][path.objname] = v
        else:
            raise TypeError(
                f"Expected st[str] = dict or st[ObjPath] (eqv) st[ObjPath.jobname][ObjPath.objname] = v, got st[{type(job_name)}'{job_name}'] = {type(v)}'{v}'"
            )

    def __getattr__(self, job_name: str):
        return self[job_name]

    def del_outputs(self, job_name: str):
        del self._outputs[job_name]


@dataclass
class FullStatus:
    g: Status  # global
    f: Status  # frame


class PostJob(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def global_begin(self, st: FullStatus):
        pass

    @abstractmethod
    def global_end(self, st: FullStatus):
        pass

    @abstractmethod
    def frame_begin(self, st: FullStatus):
        pass

    @abstractmethod
    def frame_proc(self, st: FullStatus):
        pass

    @abstractmethod
    def frame_end(self, st: FullStatus):
        pass


# guaranteed any other jobs inside any frame_xxx call,
# st.f["loop"]["iframe"] is the iframe for this iteration
class Loop(PostJob):
    def __init__(self, nframes):
        self.nframes_tot = nframes
        self._ielem = 0

    def name(self) -> str:
        return "loop"

    def global_begin(self, st: FullStatus):
        iframes_local = list(mpi.dispatch(range(self.nframes_tot)))
        nframes_local = len(iframes_local)
        st.g.set_outputs(
            self.name(),
            {
                "nframes": self.nframes_tot,
                "iframes_local": iframes_local,
                "nframes_local": nframes_local,
                "continue": nframes_local > 0,
                "progress": 0,
            },
        )
        mpi.set_async()

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        iframes = st.g.loop["iframes_local"]
        st.g.loop["progress"] = self._ielem / st.g.loop["nframes_local"]
        st.f.set_outputs(
            self.name(),
            {"iframe": iframes[self._ielem], "ielem": self._ielem},
        )

    def frame_proc(self, st: FullStatus):
        pass

    def frame_end(self, st: FullStatus):
        self._ielem += 1
        st.g.loop["continue"] = self._ielem < st.g.loop["nframes_local"]
        st.g.loop["progress"] = self._ielem / st.g.loop["nframes_local"]
        log.log(f"Post: Progress {st.g.loop["progress"]*100:5.01f}%")


# if a job has no status outputs, jobname is never used
class Clear(PostJob):
    def __init__(self, jobs):
        self.jobs = jobs

    def name(self) -> str:
        return "clear"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        for job in self.jobs:
            st.f.clear_outputs(job)

    def frame_end(self, st: FullStatus):
        pass


class Read(PostJob):
    def __init__(self, fields=None, markers=None):
        self.fields = fields
        self.markers = markers

        if fields is None and markers is None:
            raise ValueError(
                f"Expected at least one among fields and markers to be speicifed"
            )

    def name(self) -> str:
        return "read"

    def global_begin(self, st: FullStatus):
        nframes = [len(src) for src in [self.fields, self.markers] if src is not None]
        if len(set(nframes)) != 1:
            raise ValueError(
                f"Fields/Marker length should match, got {nframes} respectively"
            )

        nframes = nframes[0]
        if st.g.has_outputs("loop") and st.g.loop["nframes"] != nframes:
            raise ValueError(
                f"Fields/Marker length {nframes} not match with existing loop length {st.g.loop["nframes"]}"
            )

        st.g.set_outputs(self.name(), {"nframes": nframes})

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        i = st.f.loop["iframe"]
        msg = f"Post: Frame {i}"
        out = st.f.set_outputs(self.name(), {})
        if self.fields is not None:
            fields = self.fields[i + 1]
            msg += f" {fields}"
            out["fields"] = fields
        if self.markers is not None:
            marker = self.markers[i + 1]
            msg += f" {marker}"
            out["marker"] = marker
        log.log(msg)

    def frame_proc(self, st: FullStatus):
        out = st.f.read
        if self.fields is not None:
            out["mesh"] = out["fields"].to_pyvista()
        if self.markers is not None:
            out["bodies"] = out["marker"].to_pyvista_multiblocks()

    def frame_end(self, st: FullStatus):
        st.f.clear_outputs(self.name())


class Plot(PostJob):
    def __init__(self, case, *configs, **kwargs):
        for config in configs:
            args.add_default(
                config,
                {
                    "mesh": ObjPath("read", "fields"),
                    "opacity": 1,
                    "color": lb.Color.uniform("white"),
                    "texture": lb.Texture.specular(),
                    "kwargs": {},
                },
                inplace=True,
                throw_unused=True,
            )
        self.case = case
        self.configs = configs
        self.kwargs = args.add_default(
            kwargs,
            {
                "add_axes": True,
                "show_grid": True,
                "enable_anti_aliasing": True,
                "plotter_f": lambda p, c, i, v, m: p,
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return "plot"

    def global_begin(self, st: FullStatus):
        pass

    def global_end(self, st: FullStatus):
        pass

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        plotter = pv.Plotter(off_screen=True)
        for config in self.configs:
            mesh = st.f[config["mesh"]]

            if isinstance(config["color"], lb.ColorField):
                field = config["color"].field
                if isinstance(field, lb.FieldVector):
                    vec = mesh[field.name]
                    match field.component:
                        case lb.VecComp.X:
                            comp = vec[:, 0]
                        case lb.VecComp.Y:
                            comp = vec[:, 1]
                        case lb.VecComp.Z:
                            comp = vec[:, 2]
                        case lb.VecComp.MAG:
                            comp = np.linalg.norm(vec, axis=1)
                    comp_name = field.fullname()
                    mesh[comp_name] = comp

            plotter.add_mesh(
                mesh,
                opacity=config["opacity"],
                smooth_shading=True,
                **config["color"].add_mesh_kwargs(),
                **config["texture"].add_mesh_kwargs(),
                **config["kwargs"],
            )

        if self.kwargs["add_axes"]:
            plotter.add_axes()
        if self.kwargs["show_grid"]:
            plotter.show_grid()
        if self.kwargs["enable_anti_aliasing"]:
            plotter.enable_anti_aliasing()

        plotter = self.kwargs["plotter_f"](
            plotter,
            self.case,
            st.f.loop["iframe"],
            st.f.read["fields"] if "fields" in st.f.read else None,
            st.f.read["marker"] if "marker" in st.f.read else None,
        )

        st.f.set_outputs(self.name(), {"plotter": plotter})

    def frame_end(self, st: FullStatus):
        st.f.clear_outputs(self.name())


class SaveCaseAnim(PostJob):
    def __init__(self, case, out_name, **kwargs):
        self.case = case
        self.out_name = out_name
        self.kwargs = args.add_default(
            kwargs,
            {
                "keep_frames": True,
                "resolution": "4k",
            },
            inplace=True,
            throw_unused=True,
        )

    def name(self) -> str:
        return f"save_case_anim({self.out_name})"

    def global_begin(self, st: FullStatus):
        self.case.post.enable()
        self.case.post.animations.enable()
        a = self.case.post.animations.get_or_create(self.out_name)
        a.frames.enable()
        st.g.set_outputs(self.name(), {"anim": a})

    def global_end(self, st: FullStatus):
        a = st.g[self.name()]["anim"]

        mpi.set_sync()
        a.read()
        mpi.barrier()
        a.frames.to_video(outformat="mp4")
        if not self.kwargs["keep_frames"]:
            del a.frames
        mpi.barrier()
        a.read()  # update the new video

    def frame_begin(self, st: FullStatus):
        pass

    def frame_proc(self, st: FullStatus):
        a = st.g[self.name()]["anim"]
        a.frames.frame_by_pyvista(
            st.f.loop["iframe"],
            st.f.plot["plotter"],
            window_size=resolution_to_size(self.kwargs["resolution"]),
        )

    def frame_end(self, st: FullStatus):
        pass
