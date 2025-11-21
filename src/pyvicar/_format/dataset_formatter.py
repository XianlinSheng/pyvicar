import numpy as np
from pyvicar._datatype import Point3D, Dataset2D
from pyvicar._tree import Field
from .formatter import Formatter


class DatasetFormatter(Formatter):
    def __init__(self, f):
        Formatter.__init__(self, f)

        self.tabN = 24  # tab of a row column
        self.blankN = 1  # leave blank rows between two datasetget
        self.printidx = False

    def write(self):
        f = self._f

        for field in self:
            # implict convert Point3D -> Dataset2D (1, 3)
            if isinstance(field.value, Point3D):
                field = Field(
                    field.key, Dataset2D(np.array([field.value.xyz], dtype=float))
                )

            if not isinstance(field.value, Dataset2D):
                raise TypeError(
                    f"DatasetFormatter is for Dataset2D Field only, but encountered {field}"
                )

            arr = field.value.arr

            for rowi, row in enumerate(arr):
                strlist = []
                if self.printidx:
                    strlist.append(f"{rowi + field.value.startidx:<{self.tabN - 1}}")
                for col in row:
                    strlist.append(f"{col:<{self.tabN - 1}}")

                f.write(" ".join(strlist))
                f.write("\n")

            for _ in range(self.blankN):
                f.write("\n")

        self._clear_cache()
