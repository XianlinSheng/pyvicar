import ffmpeg
import shutil
import matplotlib.pyplot as plt
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Dict, List
from pyvicar._file import Readable
from pyvicar._file import Series, Siblings
import pyvicar.tools.mpi as mpi


class AnimationDict(Dict, Readable, Optional):
    def __init__(self, post):
        Dict.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._post = post
        self._path = self._post.path / "Animations"

    def _init(self):
        if mpi.is_synchost_or_async():
            self._path.mkdir(exist_ok=True)
        mpi.barrier_or_async()

    def _elemcheck(self, new):
        if not isinstance(new, Animation):
            raise TypeError(
                f"Expected an Animation to be inside an AnimationDict, but encountered {repr(new)}"
            )

    def __setitem__(self, _):
        raise AttributeError(
            f"[] = ... syntax not supported, animations are not resettable, to add new item, use animations.add_new(name) instead"
        )

    def __delitem__(self, key):
        ani = self._childrendict[key]
        ani.clear()
        del self._childrendict[key]

    def clear(self):
        for ani in self._childrendict.values():
            ani.clear()
        self._childrendict.clear()

    def read(self):
        if not self._path.exists():
            return

        self.enable()

        siblingsdict = Siblings.siblings_dict_at_path(self._path)
        for basename in siblingsdict.keys():
            ani = Animation(self, basename)
            self._childrendict[basename] = ani
            ani.read()

    def enable(self):
        super().enable()
        self._init()

    def _disable(self):
        return super().disable()

    @property
    def path(self):
        return self._path

    def add_new(self, name):
        name = str(name)
        if name in self._childrendict:
            raise KeyError(f"Name '{name}' already exists, change another name")

        ani = Animation(self, name)
        self._childrendict[name] = ani

        return ani

    def get_or_create(self, name):
        if not name in self._childrendict:
            ani = Animation(self, name)
            self._childrendict[name] = ani
        else:
            ani = self._childrendict[name]

        return ani


class Animation(Group, Dict, Readable):
    def __init__(self, animations, name):
        Group.__init__(self)
        Dict.__init__(self)
        self._animations = animations
        self._path = animations.path
        self._name = name

        self._children.frames = Frames(self, name)

        self._finalize_init()

    def __delattr__(self, name):
        if name != "frames":
            raise AttributeError(
                f"By default an attribute in Group is static and thus not deletable"
            )

        if self._children.frames and mpi.is_synchost_or_async():
            shutil.rmtree(self._children.frames.path)
        mpi.barrier_or_async()

        self._children.frames = Frames(self, self._name)

    def _elemcheck(self, new):
        if not isinstance(new, Video):
            raise TypeError(
                f"Expected a Video to be inside an Animation, but encountered {repr(new)}"
            )

    def __setitem__(self, _):
        raise AttributeError(
            f"[] = ... syntax not supported, videos are read-only and are not resettable"
        )

    def __delitem__(self, key):
        video = self._childrendict[key]
        if mpi.is_synchost_or_async():
            video.path.unlink()
        mpi.barrier_or_async()
        del self._childrendict[key]

    def __repr__(self):
        return f"Animation('{self._name}'; frames: {len(self._children.frames) if self._children.frames else 'inactive'}; videos: {list(self._childrendict.keys())})"

    def clear(self):
        for video in self._childrendict.values():
            if mpi.is_synchost_or_async():
                video.path.unlink()
            mpi.barrier_or_async()
        self._childrendict.clear()

        if self._children.frames and mpi.is_synchost_or_async():
            shutil.rmtree(self._children.frames.path)
        mpi.barrier_or_async()

        self._children.frames = Frames(self, self._name)

    def read(self):
        siblings = Siblings.from_basename(self._path, self._name)
        folders = siblings.folders()
        files = siblings.files()

        # frames folder
        if None in folders.exts():
            self._children.frames.enable()
            self._children.frames.read()

        # video files
        for file in files:
            # video does not need to be read
            video = Video(file.path, file.extension)
            self._childrendict[file.extension] = video

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    def video_by_ffmpeg(self, video, outformat="gif", quiet=False):
        match mpi.parallel_mode():
            case mpi.ParallelMode.Sync:
                run = mpi.is_host()
                threads = mpi.size()
            case mpi.ParallelMode.Async:
                run = True
                threads = 1

        if run:
            (
                video.output(f"{self._path}/{self._name}.{outformat}", threads=threads)
                .overwrite_output()
                .run(quiet=quiet)
            )
        mpi.barrier_or_async()


class Frames(List, Readable, Optional):
    def __init__(self, animation, name):
        List.__init__(self)
        Optional.__init__(self)
        self._animation = animation
        self._path = animation.path / name
        self._name = name

    def _init(self):
        if mpi.is_synchost_or_async():
            self._path.mkdir(exist_ok=True)
        mpi.barrier_or_async()

    def __delitem__(self, index):
        frame = self._childrenlist[self._offset_i(index)]
        if mpi.is_synchost_or_async():
            frame.path.unlink()
        mpi.barrier_or_async()
        del self._childrenlist[self._offset_i(index)]

    def clear(self):
        if mpi.is_synchost_or_async():
            for frame in self._childrenlist:
                frame.path.unlink()
        mpi.barrier_or_async()
        self._childrenlist.clear()

    def read(self):
        series = Series.from_format(self._path, self._name + r"\.(\d+)\.png")

        for file in series:
            frame = Frame(file.path, file.idxes[0])
            self._childrenlist.append(frame)

        if self._childrenlist:
            self._startidx = self._childrenlist[0].idx

    def enable(self):
        super().enable()
        self._init()

    def _disable(self):
        return super().disable()

    @property
    def path(self):
        return self._path

    def has_frame(self):
        return len(self._childrenlist) > 0

    def frame_by_pyvista(self, seriesi, plotter, *args, **kwargs):
        path = self._path / f"{self._name}.{seriesi}.png"
        plotter.show(screenshot=path, *args, **kwargs)

    def frame_by_matplotlib(self, seriesi, fig, *args, **kwargs):
        path = self._path / f"{self._name}.{seriesi}.png"
        fig.savefig(path, *args, **kwargs)
        plt.close(fig)

    def to_ffmpeg(
        self,
        framerate=10,
    ):
        if not self:
            raise Exception(
                f"Frames inactive, cannot be transferred to ffmpeg, call animation.read() to load data"
            )

        if not self.has_frame():
            raise Exception(
                f"No active frames, cannot be transferred to ffmpeg, call frames.read() to load data"
            )
        return ffmpeg.input(f"{self._path}/{self._name}.%d.png", framerate=framerate)

    def to_video(
        self,
        framerate=10,
        outformat="gif",
        quiet=False,
    ):
        match mpi.parallel_mode():
            case mpi.ParallelMode.Sync:
                run = mpi.is_host()
                threads = mpi.size()
            case mpi.ParallelMode.Async:
                run = True
                threads = 1

        if run:
            (
                self.to_ffmpeg(framerate)
                .output(
                    f"{self._animation.path}/{self._name}.{outformat}", threads=threads
                )
                .overwrite_output()
                .run(quiet=quiet)
            )
        mpi.barrier_or_async()


class Frame(Group):
    def __init__(self, path, idx):
        Group.__init__(self)
        Optional.__init__(self)
        self._path = path
        self._idx = idx

    @property
    def path(self):
        return self._path

    @property
    def idx(self):
        return self._idx


class Video(Group):
    def __init__(self, path, extension):
        Group.__init__(self)
        self._path = path
        self._extension = extension

    @property
    def path(self):
        return self._path

    @property
    def extension(self):
        return self._extension

    def to_ffmpeg(self):
        return ffmpeg.input(f"{self._path}")
