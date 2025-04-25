class Dataset2D:
    _frozen = False

    def __init__(self, arr, startIdx=1):
        self.arr = arr
        self._startidx = startIdx

        self._frozen = True

    @property
    def arr(self):
        return self._arr

    @arr.setter
    def arr(self, newarr):
        if len(newarr.shape) != 2:
            raise ValueError(
                f"Expected a 2d array, but encountered shape {newarr.shape}"
            )

        self._arr = newarr

    @property
    def startidx(self):
        return self._startidx

    @startidx.setter
    def startidx(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Expected int for start index, but encountered {value}")
        self._startidx = value

    def _offset_ij(self, ij):
        if not isinstance(ij, tuple) and len(ij) == 2:
            raise IndexError(f'Expected 2D index for Dataset2D, but encountered "{ij}"')
        i, j = ij

        if isinstance(i, slice):
            start = i.start
            stop = i.stop
            step = i.step
            if not start is None:
                start -= self._startidx
            if not stop is None:
                stop -= self._startidx
            i = slice(start, stop, step)
        else:
            i = i - self._startidx

        if isinstance(j, slice):
            start = j.start
            stop = j.stop
            step = j.step
            if not start is None:
                start -= self._startidx
            if not stop is None:
                stop -= self._startidx
            j = slice(start, stop, step)
        else:
            j = j - self._startidx

        return i, j

    def __getitem__(self, idx):
        return self._arr[self._offset_ij(idx)]

    def __setitem__(self, idx, value):
        self._arr[self._offset_ij(idx)] = value

    def __getattr__(self, key):
        return getattr(self._arr, key)

    def __setattr__(self, key, value):
        if not self._frozen or key in dir(self):
            object.__setattr__(self, key, value)
        else:
            if not hasattr(self._value, key):
                raise AttributeError(
                    f'Key "{key}" not found in either the Dataset2D itself or its stored array {repr(self._value)}'
                )
            setattr(self._value, key, value)

    def __str__(self):
        return str(self._arr)

    def __repr__(self):
        return repr(self._arr)
