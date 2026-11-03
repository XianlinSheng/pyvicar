import pyvicar
import numpy as np
from pyvicar.tools.collections import struct
from pyvicar.grid import GridModel
from pyvicar.tools.fourier import Fourier
from dataclasses import dataclass

pyvicar.assert_api_version("1.0.1", "1.1.0")


@dataclass
class IB2Motion:
    shdr_flap: Fourier
    shdr_aoa: Fourier
    shdr_sweep: Fourier
    elbw_flex: Fourier
    wrst_sweep: Fourier
    wrst_flex: Fourier
    wrst_twist: Fourier

    shdr_fth: Fourier
    elbw_fth: Fourier
    wrst_fth: Fourier
    wtip_fth: Fourier

    # seagull kinematics
    @classmethod
    def make_sg(
        cls, aoa_min, aoa_max, sweep_type="osc", flex_type="osc", flap_type="osc"
    ):
        wrst_sweep = Fourier(
            2, np.array([[-0.7664, -3.0125], [28.0553, 4.1032]]), -38.4179
        )
        match sweep_type:
            case "osc":
                pass
            case "min":
                wrst_sweep = Fourier.make_constant(wrst_sweep.min())
            case "max":
                wrst_sweep = Fourier.make_constant(wrst_sweep.max())
            case _:
                raise TypeError(f"sweep_type {sweep_type} unrecognized")

        wrst_flex = Fourier(
            2, np.array([[9.6131, 3.0183], [11.0122, -1.3128]]), -17.3083
        )
        match flex_type:
            case "osc":
                pass
            case "min":
                wrst_flex = Fourier.make_constant(wrst_flex.min())
            case "max":
                wrst_flex = Fourier.make_constant(wrst_flex.max())
            case _:
                raise TypeError(f"flex_type {flex_type} unrecognized")

        shdr_flap = shdr_flap = Fourier(
            2, np.array([[17.8798, -4.5880], [-8.5368, 1.0898]]), 8.4654
        )
        match flap_type:
            case "osc":
                pass
            case "sym":
                shdr_flap = Fourier.make_sine_minmax(*shdr_flap.minmax(), np.pi)
            case _:
                raise TypeError(f"flap_type {flap_type} unrecognized")

        shdr_aoa = Fourier.make_sine_minmax(aoa_min, aoa_max, -np.pi / 2)

        return IB2Motion(
            shdr_flap=shdr_flap,
            shdr_aoa=shdr_aoa,
            shdr_sweep=Fourier.make_constant(0),
            elbw_flex=Fourier.make_constant(67),
            wrst_sweep=wrst_sweep,
            wrst_flex=wrst_flex,
            wrst_twist=Fourier.make_constant(0),
            shdr_fth=Fourier.make_constant(0),
            elbw_fth=Fourier.make_constant(0),
            wrst_fth=(wrst_sweep + 90) * 0.3,
            wtip_fth=(wrst_sweep + 90),
        )

    # rigid retracted
    @classmethod
    def make_rr(cls, aoa, flap):
        wrst_sweep = Fourier(
            2, np.array([[-0.7664, -3.0125], [28.0553, 4.1032]]), -38.4179
        )
        wrst_sweep = Fourier.make_constant(wrst_sweep.min())

        wrst_flex = Fourier(
            2, np.array([[9.6131, 3.0183], [11.0122, -1.3128]]), -17.3083
        )
        wrst_flex = Fourier.make_constant(wrst_flex.max())

        shdr_aoa = Fourier.make_sine_minmax(-aoa, aoa, -np.pi / 2)
        shdr_flap = Fourier.make_sine_minmax(-flap, flap, np.pi)

        return IB2Motion(
            shdr_flap=shdr_flap,
            shdr_aoa=shdr_aoa,
            shdr_sweep=Fourier.make_constant(0),
            elbw_flex=Fourier.make_constant(67),
            wrst_sweep=wrst_sweep,
            wrst_flex=Fourier.make_constant(0),
            wrst_twist=Fourier.make_constant(0),
            shdr_fth=Fourier.make_constant(0),
            elbw_fth=Fourier.make_constant(0),
            wrst_fth=(wrst_sweep + 90) * 0.3,
            wtip_fth=(wrst_sweep + 90),
        )

    # rigid extended
    @classmethod
    def make_rx(cls, aoa0, aoa, flap, twist):
        wrst_sweep = Fourier(
            2, np.array([[-0.7664, -3.0125], [28.0553, 4.1032]]), -38.4179
        )
        wrst_sweep = Fourier.make_constant(wrst_sweep.max())

        wrst_flex = Fourier(
            2, np.array([[9.6131, 3.0183], [11.0122, -1.3128]]), -17.3083
        )
        wrst_flex = Fourier.make_constant(wrst_flex.max())

        shdr_aoa = Fourier.make_sine_minmax(aoa0 - aoa, aoa0 + aoa, -np.pi / 2)
        shdr_flap = Fourier.make_sine_minmax(-flap, flap, np.pi)

        wrst_twist = Fourier.make_constant(twist)

        return IB2Motion(
            shdr_flap=shdr_flap,
            shdr_aoa=shdr_aoa,
            shdr_sweep=Fourier.make_constant(0),
            elbw_flex=Fourier.make_constant(67),
            wrst_sweep=wrst_sweep,
            wrst_flex=Fourier.make_constant(0),
            wrst_twist=wrst_twist,
            shdr_fth=Fourier.make_constant(0),
            elbw_fth=Fourier.make_constant(0),
            wrst_fth=(wrst_sweep + 90) * 0.3,
            wtip_fth=(wrst_sweep + 90),
        )

    # flexible rigid-twist
    @classmethod
    def make_fw(cls, aoa0, aoa, flap, twist):
        wrst_sweep = Fourier(
            2, np.array([[-0.7664, -3.0125], [28.0553, 4.1032]]), -38.4179
        )

        wrst_flex = Fourier(
            2, np.array([[9.6131, 3.0183], [11.0122, -1.3128]]), -17.3083
        )

        shdr_aoa = Fourier.make_sine_minmax(aoa0 - aoa, aoa0 + aoa, -np.pi / 2)
        shdr_flap = Fourier.make_sine_minmax(-flap, flap, np.pi)

        wrst_twist = Fourier.make_constant(twist)

        return IB2Motion(
            shdr_flap=shdr_flap,
            shdr_aoa=shdr_aoa,
            shdr_sweep=Fourier.make_constant(0),
            elbw_flex=Fourier.make_constant(67),
            wrst_sweep=wrst_sweep,
            wrst_flex=wrst_flex,
            wrst_twist=wrst_twist,
            shdr_fth=Fourier.make_constant(0),
            elbw_fth=Fourier.make_constant(0),
            wrst_fth=(wrst_sweep + 90) * 0.3,
            wtip_fth=(wrst_sweep + 90),
        )

    # flexible optimal twist
    @classmethod
    def make_fot(cls, st, k, flap):
        wrst_sweep = Fourier(
            2, np.array([[-0.7664, -3.0125], [28.0553, 4.1032]]), -38.4179
        )

        wrst_flex = Fourier(
            2, np.array([[9.6131, 3.0183], [11.0122, -1.3128]]), -17.3083
        )

        shdr_aoa = Fourier.make_constant(0)
        shdr_flap = Fourier.make_sine_minmax(-flap, flap, np.pi)

        twist = k * np.degrees(np.atan(np.pi * st))
        wrst_twist = Fourier.make_sine_minmax(-twist, twist, -np.pi / 2)

        return IB2Motion(
            shdr_flap=shdr_flap,
            shdr_aoa=shdr_aoa,
            shdr_sweep=Fourier.make_constant(0),
            elbw_flex=Fourier.make_constant(67),
            wrst_sweep=wrst_sweep,
            wrst_flex=wrst_flex,
            wrst_twist=wrst_twist,
            shdr_fth=Fourier.make_constant(0),
            elbw_fth=Fourier.make_constant(0),
            wrst_fth=(wrst_sweep + 90) * 0.3,
            wtip_fth=(wrst_sweep + 90),
        )

    # flapping, wrist sweep
    @classmethod
    def make_fs(cls, flap, sweep="dyn"):
        wrst_sweep = Fourier(
            2, np.array([[-0.7664, -3.0125], [28.0553, 4.1032]]), -38.4179
        )
        match sweep:
            case "min":
                wrst_sweep = Fourier.make_constant(wrst_sweep.min())
            case "max":
                wrst_sweep = Fourier.make_constant(wrst_sweep.max())

        shdr_flap = Fourier.make_sine_minmax(-flap, flap, np.pi)

        return IB2Motion(
            shdr_flap=shdr_flap,
            shdr_aoa=Fourier.make_constant(0),
            shdr_sweep=Fourier.make_constant(0),
            elbw_flex=Fourier.make_constant(67),
            wrst_sweep=wrst_sweep,
            wrst_flex=Fourier.make_constant(0),
            wrst_twist=Fourier.make_constant(0),
            shdr_fth=Fourier.make_constant(0),
            elbw_fth=Fourier.make_constant(0),
            wrst_fth=(wrst_sweep + 90) * 0.3,
            wtip_fth=(wrst_sweep + 90),
        )

    @classmethod
    def make_rs(cls, aoa):
        return IB2Motion(
            shdr_flap=Fourier.make_constant(0),
            shdr_aoa=Fourier.make_constant(aoa),
            shdr_sweep=Fourier.make_constant(0),
            elbw_flex=Fourier.make_constant(67),
            wrst_sweep=Fourier.make_constant(0),
            wrst_flex=Fourier.make_constant(0),
            wrst_twist=Fourier.make_constant(0),
            shdr_fth=Fourier.make_constant(0),
            elbw_fth=Fourier.make_constant(0),
            wrst_fth=Fourier.make_constant(30),
            wtip_fth=Fourier.make_constant(90),
        )


@dataclass
class UFromTipFlowPitch:
    pitch: float


@dataclass
class UFromSt:
    st: float


def make_params(
    platform="local",
    version="common",
    name="test",
    allow_restart=True,
    re=2000,  # using chord
    chord_by_dx=5,  # chord/dx, grid resolution
    ib2_reslevel=2,
    motion=IB2Motion.make_rs(0),
    U=1,
    camber=0,
    twist="ulna",
    twist_k=0.5,
    gm_narrow=False,
    gcss="gcm",
    legacy_parallel=False,  # use 16 nodes 24*32 or 4 nodes 4*4
    step_test=False,
    body_test=False,  # when resolution not specified, run lightweight and ssm
):
    p = struct()

    p.platform = platform
    p.version = version
    p.name = name
    p.allow_restart = allow_restart
    p.re = re
    p.chord_by_dx = chord_by_dx
    p.ib2_reslevel = ib2_reslevel
    p.motion = motion
    p.camber = camber
    p.twist = twist
    p.twist_k = twist_k
    p.gm_narrow = gm_narrow
    p.gcss = gcss
    p.legacy_parallel = legacy_parallel
    p.step_test = step_test
    p.body_test = body_test

    p.Case = pyvicar.import_case(f"~/opt/ViCar3D/versions/{version}")

    p.hmrs_l = 0.4
    p.ulna_l = 0.98
    p.hand_l = 0.9
    p.hmrs_fth_n = 4
    p.ulna_fth_n = 16
    p.hand_fth_n = 11
    p.fth_ls = np.array([1.0, 0.6, 1.0, 1.0])
    p.fth_ws = np.array([0.8, 0.8, 0.8, 0.8])

    # close to these two integers
    p.chord = 1
    p.span = 3

    p.lu = 2.5
    p.lv = 3

    p.U = U
    p.re = re

    p.T = 10
    p.f = 1 / p.T
    p.omega = 2 * np.pi * p.f

    p.nu = 125 * ib2_reslevel + 1
    p.nv = 150 * ib2_reslevel + 1
    p.ubuffer = 0.3
    p.vbuffer = 0.08

    ef = np.radians(p.motion.elbw_flex.max())
    p.sw_vproj = np.sqrt(
        p.hmrs_l**2 + p.ulna_l**2 - 2 * p.hmrs_l * p.ulna_l * np.cos(ef)
    )
    p.ww_vproj = np.cos(np.radians(p.motion.wrst_sweep.absmin())) * p.hand_l
    p.ww_uproj = np.sin(np.radians(p.motion.wrst_sweep.absmax())) * p.hand_l
    p.ww_wproj = np.sin(np.radians(p.motion.wrst_flex.absmax())) * p.hand_l
    p.wf_vproj = np.cos(np.radians((p.motion.wtip_fth - 90).absmin())) * p.fth_ls[3]
    p.wf_uproj = np.sin(np.radians((p.motion.wtip_fth - 90).absmax())) * p.fth_ls[3]
    p.wf_wproj = np.sin(np.radians(p.motion.wrst_flex.absmax())) * p.fth_ls[3]
    p.sf_vproj = p.sw_vproj + p.ww_vproj + p.wf_vproj
    p.sf_uproj = p.ww_uproj + p.wf_uproj
    p.sf_wproj = p.ww_wproj + p.wf_wproj
    p.Umax_flap = np.radians(p.motion.shdr_flap.diff(p.omega).absmax()) * p.sf_vproj

    shdr_flap_min, shdr_flap_max = p.motion.shdr_flap.minmax()
    shdr_aoa_min, shdr_aoa_max = p.motion.shdr_aoa.minmax()
    shdr_sweep_min, shdr_sweep_max = p.motion.shdr_sweep.minmax()
    p.projxm = np.sin(np.radians(np.abs(shdr_sweep_min))) * p.span / p.chord
    p.projxm = np.sin(np.radians(np.abs(shdr_sweep_min))) * p.span / p.chord
    p.projxp = np.sin(np.radians(np.abs(shdr_sweep_max))) * p.span / p.chord
    p.projzm_flap = np.sin(np.radians(np.abs(shdr_flap_min))) * p.span / p.chord
    p.projzp_flap = np.sin(np.radians(np.abs(shdr_flap_max))) * p.span / p.chord
    p.projzm_aoa = (
        np.sin(np.radians(np.maximum(shdr_aoa_max, 0))) * p.sf_uproj / p.chord
    )
    p.projzp_aoa = np.sin(np.radians(np.maximum(-shdr_aoa_min, 0)))
    p.projzm_flex = p.sf_wproj / p.chord
    p.projzm = np.maximum(p.projzm_flap, p.projzm_aoa) + p.projzm_flex
    p.projzp = np.maximum(p.projzp_flap, p.projzp_aoa)

    if isinstance(p.U, UFromTipFlowPitch):
        p.ftip_flow_pitch = p.U.pitch
        p.U = p.Umax_flap / np.tan(np.radians(p.U.pitch))
    elif isinstance(p.U, UFromSt):
        A = p.sf_vproj * np.sin(np.radians(p.motion.shdr_flap.absmax()))
        p.U = 2 * A * p.f / p.U.st

    p.Umax_aoa = 2 * p.U
    p.Umax = np.sqrt(p.Umax_aoa**2 + p.Umax_flap**2)

    p.dx = p.chord / chord_by_dx
    p.ib2_dx = p.lu / (p.nu - 1)

    p.gm = GridModel.create(
        l0=[p.chord, p.span, p.chord],
        doml=[[30, 5], [0, 10], 20],
        refl=[[0.5, 2.5], [0, 1.2], 0.5],
        grow=[[1.4, 1.02], 1.4, 1.4],
    )
    p.gm.refl[0, 0] += p.projxm
    p.gm.refl[0, 1] += p.projxp
    p.gm.refl[2, 0] += p.projzm
    p.gm.refl[2, 1] += p.projzp

    return p
