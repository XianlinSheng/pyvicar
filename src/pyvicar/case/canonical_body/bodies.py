from pyvicar._tree import List
from pyvicar.file import Writable
from .body import Body
from pyvicar.tools.miscellaneous import args


class Bodies(List, Writable):
    def __init__(self, f, config={}):
        List.__init__(self)
        Writable.__init__(self)

        config = args.add_default(config, {"body_cls": Body})

        self._f = f
        self._body_cls = config["body_cls"]
        self._body_config = config

    def _elemcheck(self, new):
        if not isinstance(new, self._body_cls):
            raise TypeError(
                f"Expected a {self._body_cls.__name__} object, but encountered {repr(new)}"
            )

    def write(self):
        f = self._f

        for body in self:
            body.write()
            f.write("\n")

    def appendnew(self, n=1):
        newobjs = [self._body_cls(self._f, config=self._body_config) for _ in range(n)]
        self._childrenlist += newobjs
        if n == 1:
            return newobjs[0]
        else:
            return newobjs

    def resetnew(self, n=1):
        self._childrenlist = [
            self._body_cls(self._f, config=self._body_config) for _ in range(n)
        ]
