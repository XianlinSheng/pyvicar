import numpy as np
from collections.abc import Iterable, Hashable
from pyvicar.grid import Segment


class Verbose:
    def __init__(self, dscrp=False, vmap=False, vorig=False):
        # key(dscrp) valueMapped
        self.dscrp = dscrp
        # key{valueOrig: valueMapped} valueMapped
        self.vmap = vmap
        # key valueOrig. 
        # Warning: valueOrig is only for easy inspection, it is not valid in the files
        self.vorig = vorig


    def __or__(self, B):
        return Verbose(
            self.dscrp or B.dscrp,
            self.vmap or B.vmap,
            self.vorig or B.vorig,
        )


Verbose.dscrp = Verbose(dscrp = True)
Verbose.vmap = Verbose(vmap = True)
Verbose.keyall = Verbose(dscrp = True, vmap = True)
Verbose.vorig = Verbose(vorig = True)
Verbose.all = Verbose(dscrp = True, vmap = True, vorig = True)


class Struct:
    pass

class Field:
    _frozen = False
    vmapPresets = Struct()

    def __init__(self, key, value, dscrp="", vmap={}):
        self.key = key
        self.dscrp = dscrp

        # infer the storing type
        # default, input is what is stored
        self._valueType = type(value)

        # input is a verbose name, and should store its mapped true value
        if isinstance(value, Hashable) and value in vmap:
            self._valueType = type(vmap[value])

        # input a dataset, and should store a wrapped-up Dataset2D object
        if isinstance(value, np.ndarray):
            self._valueType = Dataset2D

        # e.g. {'invalid': 0, 'valid': 1}, input 'valid' will be auto converted to 1
        self._vmap = vmap
        self._rmap = {v: k for k, v in vmap.items()}

        # set it at last because this method needs all other parameters
        self.value = value
        
        self._frozen = True

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        # implicit extract value from another Field
        if isinstance(new, Field):
            self.value = new.value
            return
        
        # implicit convert value based on preset map
        if isinstance(new, Hashable) and new in self._vmap:
            new = self._vmap[new]
        
        # implicit int -> float conversion
        if self._valueType is float and isinstance(new, int):
            new = float(new)

        
        # implicit np.ndarray -> Dataset2D
        if self._valueType is Dataset2D and isinstance(new, np.ndarray):
            new = Dataset2D(new)

        # implicit Grid Segment -> Dataset2D
        if self._valueType is Dataset2D and isinstance(new, Segment):
            new = Dataset2D(new.grid[:, np.newaxis])

        # implicit Iterable -> Point3D
        if self._valueType is Point3D and isinstance(new, Iterable):
            new = Point3D(new)
        
        if not type(new) is self._valueType:
            raise TypeError(f'Attempted to set {type(new)} type value {new} to a Field for {self._valueType}')

        self._value = new
    
    def key_str(self, verbose=Verbose()):
        key = self.key
        
        if verbose.dscrp and self.dscrp:
            dscrp = f'({self.dscrp})'
        else:
            dscrp = ''

        if verbose.vmap and self._vmap:
            vmap = f'[{self.rmap_str()}]'
        else:
            vmap = ''

        return f'{key}{dscrp}{vmap}'

    def value_str(self, verbose=Verbose()):
        value = self.value
        if verbose.vorig and value in self._rmap:
            value = self._rmap[value]
        elif not verbose.vorig and value in self._vmap:
            value = self._vmap[value]
        
        return str(value)
    
    def vmap_str(self):
        kvstrs = [f'{k}: {v}' for k, v in self._vmap.items()]
        return ', '.join(kvstrs)

    def rmap_str(self):
        kvstrs = [f'{k}: {v}' for k, v in self._rmap.items()]
        return ', '.join(kvstrs)
    
    def key_len(self, verbose=Verbose()):
        return len(self.key_str(verbose))

    def value_len(self, verbose=Verbose()):
        return len(self.value_str(verbose))
    
    def align_len(self, verbose=Verbose()):
        return max(self.key_len(verbose), self.value_len(verbose))
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f'Field[{self._valueType.__name__}]({self.key_str(verbose=Verbose.all)}: {self.value_str(verbose=Verbose.all)})'
    
    def __getitem__(self, idx):
        return self._value[idx]
        
    def __setitem__(self, idx, value):
        self._value[idx] = value
    
    def __getattr__(self, key):
        return getattr(self._value, key)

    def __setattr__(self, key, value):
        if not self._frozen or key in dir(self):
            object.__setattr__(self, key, value)
        else:
            if not hasattr(self._value, key):
                raise AttributeError(f'Key "{key}" not found in either the Field itself or its stored value {repr(self._value)}')
            setattr(self._value, key, value)


Field.vmapPresets.bool2int = {False: 0, True: 1}
Field.vmapPresets.xyz2int = {'x': 1, 'y': 2, 'z': 3}


class Point3D:
    def __init__(self, xyz):
        self.xyz = xyz

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @x.setter
    def x(self, x):
        self._x = float(x)

    @y.setter
    def y(self, y):
        self._y = float(y)

    @z.setter
    def z(self, z):
        self._z = float(z)
    
    @property
    def xyz(self):
        return [self._x, self._y, self._z]
    
    @xyz.setter
    def xyz(self, new):
        if not isinstance(new, Iterable):
            raise TypeError(f'Expected an Iterable (list) storing [x, y, z], but encountered {new}')
        x, y, z = new
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def __str__(self):
        return f'{self._x} {self._y} {self._z}]'

    def __repr__(self):
        return f'Point3D([{self._x}, {self._y}, {self._z}])'


class Dataset2D:
    def __init__(self, arr):
        self.arr = arr
        self._startidx = 1

    @property
    def arr(self):
        return self._arr
    
    @arr.setter
    def arr(self, newarr):
        if len(newarr.shape) != 2:
            raise ValueError(f'Expected a 2d array, but encountered shape {newarr.shape}')
        
        self._arr = newarr
    
    @property
    def startidx(self):
        return self._startidx

    @startidx.setter
    def startidx(self, value):
        if not isinstance(value, int):
            raise TypeError(f'Expected int for start index, but encountered {value}')
        self._startidx = value

    def _offset_ij(self, ij):
        if not isinstance(ij, tuple) and len(ij) == 2:
            raise IndexError(f'Expected 2D index for Dataset2D, but encountered "{idx}"')
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

    def __str__(self):
        return str(self._arr)

    def __repr__(self):
        return repr(self._arr)

