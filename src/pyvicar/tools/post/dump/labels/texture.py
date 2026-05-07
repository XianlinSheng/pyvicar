from dataclasses import dataclass
from abc import abstractmethod


class TextureBase:
    @abstractmethod
    def add_mesh_kwargs(self):
        pass


@dataclass
class TextureNone(TextureBase):
    def add_mesh_kwargs(self):
        return {}


@dataclass
class TexturePBR(TextureBase):
    metallic: float
    roughness: float
    diffuse: float

    def add_mesh_kwargs(self):
        return {
            "pbr": True,
            "metallic": self.metallic,
            "roughness": self.roughness,
            "diffuse": self.diffuse,
        }


@dataclass
class TextureSpecular(TextureBase):
    specular: float
    specular_power: float
    diffuse: float
    ambient: float

    def add_mesh_kwargs(self):
        return {
            "specular": self.specular,
            "specular_power": self.specular_power,
            "diffuse": self.diffuse,
            "ambient": self.ambient,
        }


class Texture:
    @staticmethod
    def none():
        return TextureNone()

    @staticmethod
    def pbr(metallic=0.4, roughness=0.2, diffuse=1):
        return TexturePBR(metallic, roughness, diffuse)

    @staticmethod
    def specular(specular=0.6, specular_power=60, diffuse=1, ambient=0.1):
        return TextureSpecular(specular, specular_power, diffuse, ambient)
