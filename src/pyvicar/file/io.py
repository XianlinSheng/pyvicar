from abc import ABC, abstractmethod


class Writable(ABC):
    @abstractmethod
    def write(self):
        pass


class Readable(ABC):
    @abstractmethod
    def read(self):
        pass


def lazy_open(path, mode):
    return LazyFile(path, mode)


class LazyFile:
    def __init__(self, path, mode):
        self._path = path
        self._mode = mode
        self._f = None

    def _open_if_not(self):
        if self._f is None:
            self._f = open(self._path, self._mode)

    def write(self, *args, **kwargs):
        self._open_if_not()
        self._f.write(*args, **kwargs)

    def read(self, *args, **kwargs):
        self._open_if_not()
        self._f.read(*args, **kwargs)

    def flush(self, *args, **kwargs):
        self._open_if_not()
        self._f.flush(*args, **kwargs)
