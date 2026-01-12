import numpy as np
from pathlib import Path
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field, List
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter, DatasetFormatter


class IB2(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")
        self._formatter = KV1Formatter(self._f)

        self._children.nib2 = Field("nib2", 0)
        self._children.ib2s = Surfaces(self._f)

        self._finalize_init()

    def enable(self):
        Optional.enable(self)
        self._init()

    def write(self):
        if not self:
            raise Exception(f"The object is not active, call .enable() to enable it")

        f = self._f

        self._formatter += self._children.nib2
        self._formatter.write()

        f.write("\n")

        self._children.ib2s.write()

        f.flush()


class Surfaces(List, Writable):
    def __init__(self, f):
        List.__init__(self)
        Writable.__init__(self)
        self._f = f

    def _elemcheck(self, new):
        if not isinstance(new, Surface):
            raise TypeError(f"Expected a Surface object, but encountered {repr(new)}")

    def write(self):
        f = self._f

        for surface in self:
            surface.write()
            f.write("\n")

    def appendnew(self, surfType="user", n=1):
        clsobj = Surfaces.get_surf_clsbj(surfType)
        newobjs = [clsobj(self._f) for _ in range(n)]
        self._childrenlist += newobjs
        if n == 1:
            return newobjs[0]
        else:
            return newobjs

    def resetnew(self, surfType="user", n=1):
        clsobj = Surfaces.get_surf_clsbj(surfType)
        self._childrenlist = [clsobj(self._f) for _ in range(n)]

    def get_surf_clsbj(surfType):
        match surfType:
            case "user":
                clsobj = SurfTypeUser
            case "wing":
                clsobj = SurfTypeWing
            case _:
                raise Exception(f"unrecognized type {surfType}")

        return clsobj


class Surface(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._f = f
        self._headerFormatter = KV1Formatter(f)
        self._arrayFormatter = DatasetFormatter(f)
        self._headerFormatter.kvtabN = self._arrayFormatter.tabN

        self._children.iBody = Field("iBody", 0)
        self._children.type = Field("type", 0, "", {"user": 1, "wing": 2})
        self._children.nu = Field("nu", 0)
        self._children.nv = Field("nv", 0)

    def write(self):
        f = self._f

        self._headerFormatter += self._children.iBody
        self._headerFormatter.write()

        self._headerFormatter += self._children.nu
        self._headerFormatter += self._children.nv
        self._headerFormatter.write()

        self._headerFormatter += self._children.type
        self._headerFormatter.write()


class SurfTypeUser(Surface):
    def __init__(self, f):
        Surface.__init__(self, f)

        self._finalize_init()

        self.type = "user"

    def write(self):
        f = self._f

        Surface.write(self)


class SurfTypeWing(Surface):
    def __init__(self, f):
        Surface.__init__(self, f)

        self._children.x0 = Field("x0", 0.0)
        self._children.y0 = Field("y0", 0.0)
        self._children.z0 = Field("z0", 0.0)

        self._children.ux = Field("ux", 1.0)
        self._children.uy = Field("uy", 0.0)
        self._children.uz = Field("uz", 0.0)

        self._children.vx = Field("vx", 0.0)
        self._children.vy = Field("vy", 1.0)
        self._children.vz = Field("vz", 0.0)

        self._children.shdr_u = Field("shdr_u", 0.0, "shoulder joint position u")
        self._children.shdr_v = Field("shdr_v", 0.0, "shoulder joint position v")
        self._children.shdr_flap_u = Field("shdr_flap_u", 1.0, "flap axis u")
        self._children.shdr_flap_v = Field("shdr_flap_v", 0.0, "flap axis v")

        self._children.hmrs_l = Field("hmrs_l", 0.0)
        self._children.ulna_l = Field("ulna_l", 0.0)
        self._children.hand_l = Field("hand_l", 0.0)
        self._children.wing_w = Field("wing_w", 0.0)

        # feathers keyframing at joints
        self._children.hmrs_fth_n = Field("hmrs_fth_n", 0)
        self._children.ulna_fth_n = Field("ulna_fth_n", 0)
        self._children.hand_fth_n = Field("hand_fth_n", 0)

        self._children.shdr_fth_l = Field("shdr_fth_l", 0.0)
        self._children.elbw_fth_l = Field("elbw_fth_l", 0.0)
        self._children.wrst_fth_l = Field("wrst_fth_l", 0.0)
        self._children.wtip_fth_l = Field("wtip_fth_l", 0.0)

        self._children.f = Field("f", 0.0)
        self._children.shdr_flap_amp = Field("shdr_flap_amp", 0.0)
        self._children.shdr_aoa_amp = Field("shdr_aoa_amp", 0.0)
        self._children.shdr_sweep_amp = Field("shdr_sweep_amp", 0.0)
        self._children.elbw_flex_amp = Field("elbw_flex_amp", 0.0)
        self._children.wrst_sweep_amp = Field("wrst_sweep_amp", 0.0)
        self._children.elbw_flex_deg0 = Field("elbw_flex_deg0", 0.0)
        self._children.wrst_sweep_deg0 = Field("wrst_sweep_deg0", 0.0)

        self._children.shdr_fth_amp = Field("shdr_fth_amp", 0.0)
        self._children.elbw_fth_amp = Field("elbw_fth_amp", 0.0)
        self._children.wrst_fth_amp = Field("wrst_fth_amp", 0.0)
        self._children.wtip_fth_amp = Field("wtip_fth_amp", 0.0)

        self._children.shdr_fth_deg0 = Field("shdr_fth_deg0", 0.0)
        self._children.elbw_fth_deg0 = Field("elbw_fth_deg0", 0.0)
        self._children.wrst_fth_deg0 = Field("wrst_fth_deg0", 0.0)
        self._children.wtip_fth_deg0 = Field("wtip_fth_deg0", 0.0)

        self._children.fth_shape_npoint = Field("fth_shape_npoint", 4)
        self._children.fth_shape_uv = Field(
            "fth_shape_uv",
            np.array(
                [
                    [0, -0.1],
                    [1, -0.1],
                    [1, 0.1],
                    [0, 0.1],
                ]
            ),
        )

        self._finalize_init()

        self.type = "wing"

    def set_fth_kf(self, param, arr):
        poslist = ["shdr", "elbw", "wrst", "wtip"]
        for pos, val in zip(poslist, arr):
            name = f"{pos}_fth_{param}"
            setattr(self, name, val)

    def write(self):
        f = self._f

        Surface.write(self)

        self._headerFormatter += self._children.x0
        self._headerFormatter += self._children.y0
        self._headerFormatter += self._children.z0
        self._headerFormatter.write()

        self._headerFormatter += self._children.ux
        self._headerFormatter += self._children.uy
        self._headerFormatter += self._children.uz
        self._headerFormatter.write()

        self._headerFormatter += self._children.vx
        self._headerFormatter += self._children.vy
        self._headerFormatter += self._children.vz
        self._headerFormatter.write()

        self._headerFormatter += self._children.shdr_u
        self._headerFormatter += self._children.shdr_v
        self._headerFormatter.write()

        self._headerFormatter += self._children.shdr_flap_u
        self._headerFormatter += self._children.shdr_flap_v
        self._headerFormatter.write()

        self._headerFormatter += self._children.hmrs_l
        self._headerFormatter += self._children.ulna_l
        self._headerFormatter += self._children.hand_l
        self._headerFormatter += self._children.wing_w
        self._headerFormatter.write()

        self._headerFormatter += self._children.hmrs_fth_n
        self._headerFormatter += self._children.ulna_fth_n
        self._headerFormatter += self._children.hand_fth_n
        self._headerFormatter.write()

        self._headerFormatter += self._children.shdr_fth_l
        self._headerFormatter += self._children.elbw_fth_l
        self._headerFormatter += self._children.wrst_fth_l
        self._headerFormatter += self._children.wtip_fth_l
        self._headerFormatter.write()

        self._headerFormatter += self._children.f
        self._headerFormatter.write()

        self._headerFormatter += self._children.shdr_flap_amp
        self._headerFormatter += self._children.shdr_aoa_amp
        self._headerFormatter += self._children.shdr_sweep_amp
        self._headerFormatter.write()

        self._headerFormatter += self._children.elbw_flex_amp
        self._headerFormatter += self._children.wrst_sweep_amp
        self._headerFormatter.write()

        self._headerFormatter += self._children.elbw_flex_deg0
        self._headerFormatter += self._children.wrst_sweep_deg0
        self._headerFormatter.write()

        self._headerFormatter += self._children.shdr_fth_amp
        self._headerFormatter += self._children.elbw_fth_amp
        self._headerFormatter += self._children.wrst_fth_amp
        self._headerFormatter += self._children.wtip_fth_amp
        self._headerFormatter.write()

        self._headerFormatter += self._children.shdr_fth_deg0
        self._headerFormatter += self._children.elbw_fth_deg0
        self._headerFormatter += self._children.wrst_fth_deg0
        self._headerFormatter += self._children.wtip_fth_deg0
        self._headerFormatter.write()

        self._headerFormatter += self._children.fth_shape_npoint
        self._headerFormatter.write()

        self._arrayFormatter += self._children.fth_shape_uv
        self._arrayFormatter.write()
