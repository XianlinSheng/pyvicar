from collections.abc import Iterable


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
            raise TypeError(
                f"Expected an Iterable (list) storing [x, y, z], but encountered {new}"
            )
        x, y, z = new
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def __str__(self):
        return f"{self._x} {self._y} {self._z}]"

    def __repr__(self):
        return f"Point3D([{self._x}, {self._y}, {self._z}])"
