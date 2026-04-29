from dataclasses import dataclass
from enum import Enum
from abc import abstractmethod


# name is the base name for the field, but without possible suffix like vec components
# fullname is promised full access name for the field that field prep needs to obey
# and other dependant settings can rely on without touching prep details
@dataclass
class FieldBase:
    name: str

    @abstractmethod
    def fullname(self):
        pass


class FieldScalar(FieldBase):
    def fullname(self):
        return self.name


@dataclass
class FieldRenameScalar(FieldScalar):
    orig: str


class VecComp(Enum):
    X = 0
    Y = 1
    Z = 2
    MAG = 3


@dataclass
class FieldVector(FieldBase):
    component: VecComp

    def fullname(self):
        return f"{self.name}({self.component.name})"


@dataclass
class FieldVectorVORFromVEL(FieldVector):
    vel_name: str


class Field:
    @staticmethod
    def scalar(name):
        return FieldScalar(name)

    @staticmethod
    def rename_scalar(name, orig):
        return FieldRenameScalar(name, orig)

    @staticmethod
    def vector(name, component="mag"):
        return FieldVector(name, VecComp[component.upper()])

    @staticmethod
    def vor_from_vel(vel_name, component="z"):
        return FieldVectorVORFromVEL(
            "VOR", component=VecComp[component.upper()], vel_name=vel_name
        )
