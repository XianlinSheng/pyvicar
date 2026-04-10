from dataclasses import dataclass
from enum import Enum


@dataclass
class FieldBase:
    name: str


class FieldScalar(FieldBase):
    pass


class VecComp(Enum):
    X = 0
    Y = 1
    Z = 2
    MAG = 3


@dataclass
class FieldVector(FieldBase):
    component: VecComp


@dataclass
class FieldVectorVORFromVEL(FieldVector):
    vel_name: str


class Field:
    @staticmethod
    def scalar(name):
        return FieldScalar(name)

    @staticmethod
    def vector(name, component="mag"):
        return FieldVector(name, VecComp[component.upper()])

    @staticmethod
    def vor_from_vel(vel_name, component="z"):
        return FieldVectorVORFromVEL(
            "VOR", component=VecComp[component.upper()], vel_name=vel_name
        )
