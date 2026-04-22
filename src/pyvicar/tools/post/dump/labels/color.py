from dataclasses import dataclass
from .field import FieldBase
from abc import abstractmethod


class ColorBase:
    @abstractmethod
    def add_mesh_kwargs(self):
        pass


@dataclass
class ColorUniform(ColorBase):
    name: str

    def add_mesh_kwargs(self):
        return {"color": self.name}


@dataclass
class ColorField(ColorBase):
    field: FieldBase
    cmap: str
    clim: None | list
    scalar_bar_args: None | dict

    def add_mesh_kwargs(self):
        return {
            "scalars": self.field.fullname(),
            "cmap": self.cmap,
            "clim": self.clim,
            "show_scalar_bar": True,
            "scalar_bar_args": self.scalar_bar_args,
        }


class Color:
    @staticmethod
    def uniform(name="turquoise"):
        return ColorUniform(name)

    @staticmethod
    def field(
        fieldobj,
        cmap="coolwarm",
        clim=None,
        scalar_bar_args={
            "vertical": True,
            "label_font_size": 40,
            "title_font_size": 40,
        },
    ):
        if not isinstance(fieldobj, FieldBase):
            raise TypeError(
                f"Use Field wizard to create argument, but encounter {type(fieldobj)}"
            )
        return ColorField(fieldobj, cmap, clim, scalar_bar_args)
