from dataclasses import dataclass
from .field import FieldBase


class ColorBase:
    pass


@dataclass
class ColorUniform(ColorBase):
    name: str


@dataclass
class ColorField(ColorBase):
    field: FieldBase
    cmap: str
    clim: None | list
    scalar_bar_args: None | dict


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
