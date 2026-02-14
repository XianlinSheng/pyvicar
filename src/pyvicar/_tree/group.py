from collections.abc import Iterable, MutableSequence, MutableMapping
from abc import ABC
from .field import Field
import pyvicar.tools.mpi as mpi


class Container(ABC):
    pass


# accessed by struct.name
# iterated by for name, obj in struct
class Struct(Iterable):
    def __iter__(self):
        return iter(vars(self).items())

    def __repr__(self):
        return f"Struct({vars(self)})"

    def keys(self):
        return vars(self).keys()

    def values(self):
        return vars(self).values()

    def items(self):
        return vars(self).items()


# group contains static children, defined compile-time (mod init)
class Group(Container):
    _frozen = False

    def __init__(self):
        Container.__init__(self)
        self._children = Struct()  # all kv pairs storage

    def _finalize_init(self):
        # expose public interface for items stored in _children
        for k, v in self._children:

            def make_group_property(k):
                def getter(self):
                    return getattr(self._children, k)

                def setter(self, value):
                    raise AttributeError(
                        f"Name {k} is a Group/List/Dict, not a settable Field"
                    )

                return property(getter, setter)

            def make_field_property(k):
                def getter(self):
                    return getattr(self._children, k)

                def setter(self, value):
                    getattr(self._children, k).value = value

                return property(getter, setter)

            match v:
                case Container():
                    setattr(self.__class__, k, make_group_property(k))
                case Field():
                    setattr(self.__class__, k, make_field_property(k))
                case _:
                    raise TypeError(
                        f'The children of a Group can either be another Container(Group/List/Dict) or a Field, but encountered "{k}": {v}'
                    )

        # freeze structure, no new attr is allowed to be created anymore
        self._frozen = True

    def __setattr__(self, key, value):
        if self._frozen and not hasattr(self, key):
            raise AttributeError(
                f'Name "{key}" not found. Group is a static directory, dynamic creation not allowed. Existing children:\n{self.keys()}'
            )
        object.__setattr__(self, key, value)

    def keys(self):
        return self._children.keys()

    def values(self):
        return self._children.values()

    def items(self):
        return self._children.items()

    def set_children(self, itemable):
        for k, v in itemable.items():
            if k in self._children.keys():
                setattr(self, k, v)


# List contains dynamic childrenlist that can be accessed as a list
class List(MutableSequence, Container):
    def __init__(self):
        Container.__init__(self)
        self._childrenlist = []
        self._startidx = 1

    @property
    def startidx(self):
        return self._startidx

    @startidx.setter
    def startidx(self, value):
        if not isinstance(value, int):
            raise TypeError(f"Expected int for start index, but encountered {value}")
        self._startidx = value

    # can be overriden to suit specific needs upper level
    def _elemcheck(self, new):
        if not isinstance(new, Container):
            raise TypeError(
                f"Expected a Container (Group/List/Dict) to be inside a List, but encountered {repr(new)}"
            )

    def _offset_i(self, i):
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

        return i

    def __getitem__(self, index):
        return self._childrenlist[self._offset_i(index)]

    def __setitem__(self, index, value):
        self._elemcheck(value)
        self._childrenlist[self._offset_i(index)] = value

    def __delitem__(self, index):
        del self._childrenlist[self._offset_i(index)]

    def __len__(self):
        return len(self._childrenlist)

    # this is necessary because default iter uses index and here the index can be shifted
    def __iter__(self):
        return iter(self._childrenlist)

    def insert(self, index, value):
        self._elemcheck(value)
        self._childrenlist.insert(index - self._startidx, value)

    def append(self, value):
        self._elemcheck(value)
        self._childrenlist.append(value)

    def clear(self):
        self._childrenlist.clear()

    def __iadd__(self, value):
        if isinstance(value, Iterable):
            for onevalue in value:
                self.append(onevalue)
        else:
            self.append(value)
        return self

    def __repr__(self):
        return f"List({repr(self._childrenlist)})"

    def mpi_dispatch(self):
        return mpi.dispatch_sequence(self, self._startidx)


# Dict contains dynamic children that can be accessed as a dict
class Dict(MutableMapping, Container):
    def __init__(self):
        Container.__init__(self)
        self._childrendict = {}

    # can be overriden to suit specific needs upper level
    def _elemcheck(self, new):
        if not isinstance(new, Container):
            raise TypeError(
                f"Expected a Container (Group/List/Dict) to be inside a List, but encountered {repr(new)}"
            )

    def __getitem__(self, key):
        return self._childrendict[key]

    def __setitem__(self, key, value):
        self._elemcheck(value)
        self._childrendict[key] = value

    # can be overriden to achieve deleting a file/folder
    def __delitem__(self, key):
        del self._childrendict[key]

    def __len__(self):
        return len(self._childrendict)

    def __iter__(self):
        return iter(self._childrendict)

    def __repr__(self):
        return f"Dict({repr(self._childrendict)})"

    def keys(self):
        return self._childrendict.keys()

    def values(self):
        return self._childrendict.values()

    def add_pair(self, key, value):
        self._elemcheck(value)
        self._childrendict[key] = value

    def clear(self):
        self._childrendict.clear()
