from abc import ABC, abstractmethod


class Writable(ABC):
    @abstractmethod
    def write(self):
        pass


class Readable(ABC):
    @abstractmethod
    def read(self):
        pass


def lazy_open(*args, **kwargs):
    return LazyFile(*args, **kwargs)


class LazyFile:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._f = None

    def _open_if_not(self):
        if self._f is None:
            self._f = open(*self._args, **self._kwargs)

    def write(self, *args, **kwargs):
        self._open_if_not()
        return self._f.write(*args, **kwargs)

    def read(self, *args, **kwargs):
        self._open_if_not()
        return self._f.read(*args, **kwargs)

    def flush(self, *args, **kwargs):
        self._open_if_not()
        return self._f.flush(*args, **kwargs)
