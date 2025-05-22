from collections.abc import Iterable
from pyvicar._file import Writable
from pyvicar._tree import Field


# A formatter formats a line of Field (in a buffer) and write file
class Formatter(Iterable, Writable):
    def __init__(self, f):
        self._f = f
        self._buffer = []
        self.verbose = Field.Verbose.keyall

    def __iter__(self):
        return iter(self._buffer)

    def __repr__(self):
        return f"Formatter({self._buffer})"

    def __iadd__(self, newfield):
        if isinstance(newfield, Iterable):
            self._buffer += newfield
        else:
            self._buffer.append(newfield)
        return self

    def _clear_cache(self):
        self._buffer = []
