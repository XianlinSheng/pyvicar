import ffmpeg
import shutil
from collections.abc import Iterable
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Dict
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
        if mpi.is_host_in_sync():
            self._path.mkdir(exist_ok=True)
        mpi.barrier_or_async()

    def enable(self):
        super().enable()
        self._init()

    def _disable(self):
        return super().disable()

    def read(self):
        if not self._path.exists():
            return

        self.enable()

        siblingsdict = Siblings.siblings_dict_at_path(self._path)
        for basename, siblings in siblingsdict.items():
            ani = Animation(self, basename)
            folders = siblings.folders()
            files = siblings.files()

            # frames folder
            if None in folders.exts():
                folder = folders[None]
                series = Series.from_format(folder.path, basename + r"\.(\d+)\.png")
                ani.frames.enable()
                ani.frames._nframe = len(series)

            # movie files
            for file in files:
                movie = Movie(file.path, file.extension)
                ani.add_pair(file.extension, movie)

            self._childrendict[basename] = ani

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

    def del_animations(self, names=None):
        if names is None:
            names = list(self._childrendict.keys())

        if isinstance(names, str):
            ani = self._childrendict[names]
            ani.del_movies()
            ani.del_frames()
            del self._childrendict[names]
            return

        if isinstance(names, Iterable):
            for name in names:
                self.del_animations(name)
            return

        raise TypeError(
            f"del_animations takes in str or [str], but encountered {names}"
        )

    def _elemcheck(self, new):
        if not isinstance(new, Animation):
            raise TypeError(
                f"Expected an Animation to be inside an AnimationDict, but encountered {repr(new)}"
            )

    def __setitem__(self, _):
        raise AttributeError(
            f"[] = ... syntax not supported, animations are not resettable, to add new item, use animations.add_new(name) instead"
        )

    def __delitem__(self, _):
        raise AttributeError(
            f"del syntax not supported, use animations.del_animation(names) instead"
        )


class Animation(Group, Dict):
    def __init__(self, animations, name):
        Group.__init__(self)
        Dict.__init__(self)
        self._animations = animations
        self._path = animations.path
        self._name = name

        self._children.frames = Frames(self, name)

        self._finalize_init()

    @property
    def path(self):
        return self._path

    def has_movies(self):
        return len(self._childrendict) > 0

    def del_movies(self, names=None):
        if names is None:
            names = list(self._childrendict.keys())

        if isinstance(names, str):
            if mpi.is_host_in_sync():
                self._childrendict[names].path.unlink()
            mpi.barrier_or_async()
            del self._childrendict[names]
            return

        if isinstance(names, Iterable):
            for name in names:
                self.del_movies(name)
            return

        raise TypeError(f"del_movies takes in str or [str], but encountered {names}")

    def del_frames(self):
        if self._children.frames and mpi.is_host_in_sync():
            shutil.rmtree(self._children.frames.path)
        mpi.barrier_or_async()
        self._children.frames = Frames(self, self._name)

    def reset_frames(self):
        self.del_frames()
        self._children.frames.enable()

    def _elemcheck(self, new):
        if not isinstance(new, Movie):
            raise TypeError(
                f"Expected a Movie to be inside an Animation, but encountered {repr(new)}"
            )

    def __repr__(self):
        return f"Animation('{self._name}'; frames: {self._children.frames.nframe if self._children.frames else 'inactive'}; movies: {list(self._childrendict.keys())})"

    def __setitem__(self, _):
        raise AttributeError(
            f"[] = ... syntax not supported, movies are read-only and are not resettable"
        )

    def __delitem__(self, _):
        raise AttributeError(
            f"del syntax not supported, use animation.del_movies(names) or animation.del_frames() instead"
        )


class Frames(Group, Optional):
    def __init__(self, animation, name):
        Group.__init__(self)
        Optional.__init__(self)
        self._animation = animation
        self._path = animation.path / name
        self._name = name

    @property
    def path(self):
        return self._path

    @property
    def nframe(self):
        return self._nframe

    def is_active(self):
        return self

    def has_frame(self):
        return self._nframe > 0

    def is_complete(self):
        return self and self._nframe > 0

    def _init(self):
        if mpi.is_host_in_sync():
            self._path.mkdir(exist_ok=True)
        mpi.barrier_or_async()
        self._nframe = 0

    def enable(self):
        super().enable()
        self._init()

    def _disable(self):
        return super().disable()

    def to_ffmpeg(self, framerate=10):
        if not self.is_complete():
            raise Exception(
                f"Frames inactive or no valid frame files, cannot be transferred to ffmpeg, call animations.read() to reload data"
            )
        return ffmpeg.input(f"{self._path}/{self._name}.%d.png", framerate=framerate)

    def to_movie(
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

    def from_seriesi_pyvista(self, seriesi, plotter, *args, **kwargs):
        path = self._path / f"{self._name}.{seriesi}.png"
        plotter.show(screenshot=path, *args, **kwargs)


class Movie(Group):
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
