from pyvicar.tools.study import StudyType
import projmgr.params as params


def make_study_t():
    return (
        StudyType()
        .add_branch(
            "motion",
            "",
            {
                "rs": StudyType().add_optional_int("aoa", "a", off_value=0),
                "sg": StudyType()
                .add_optional_int("aoa", "a", off_value=0)
                .add_optional_branch(
                    "oscillate", "", {"o": StudyType().add_optional_int("daoa", "d")}
                )
                .add_optional_choice(
                    "sweep", "s", ("osc", "min", "max"), off_choice="osc"
                )
                .add_optional_choice(
                    "flex", "x", ("osc", "min", "max"), off_choice="osc"
                )
                .add_optional_choice("flap", "f", ("osc", "sym"), off_choice="osc"),
                "rr": StudyType()
                .add_int("aoa", "a")
                .add_int("flap", "f")
                .add_int("effaoa", "efa"),
                "rx": StudyType()
                .add_switch("twist", "w")
                .add_int("aoa", "a")
                .add_optional_int("bias", "b", off_value=10)
                .add_optional_int("flap", "f", off_value=20)
                .add_int("st", "st"),
                "fw": StudyType()
                .add_int("aoa", "a")
                .add_optional_int("bias", "b", off_value=10)
                .add_optional_int("flap", "f", off_value=20)
                .add_int("st", "st"),
                "fot": StudyType()
                .add_optional_int("flap", "f", off_value=20)
                .add_int("st", "st")
                .add_int("k", "k"),
                "fs": StudyType()
                .add_optional_int("flap", "f", off_value=20)
                .add_choice("sweep", "", ("dyn", "min", "max"))
                .add_int("st", "st"),
            },
        )
        .add_int("camber", "c")
        .add_switch("legacy_parallel", "l")
        .add_optional_int("resolution", "r", off_value=5)
        .add_switch("step_test", "t")
        # Local, Rockfish, Blackwell, lenoVo
        .add_choice("platform", "", ("L", "R", "B", "V"))
        # Common, Gpu
        .add_choice("version", "", ("C", "G", "M"))
    )


def to_params(code):
    study_t = make_study_t()
    study = study_t.decode(code)

    U = 1
    twist_mode = "ulna"
    twist_k = 0.5
    match study.motion.branch:
        case "rs":
            motion = params.IB2Motion.make_rs(aoa=study.motion.substudy.aoa.value)
        case "sg":
            aoa = study.motion.substudy.aoa
            osc = study.motion.substudy.oscillate
            if osc.on:
                daoa = osc.substudy.daoa
                aoa_min = -daoa.value if daoa.on else -aoa.value
            else:
                aoa_min = aoa.value
            motion = params.IB2Motion.make_sg(
                aoa_min=aoa_min,
                aoa_max=aoa.value,
                sweep_type=study.motion.substudy.sweep.choice,
                flex_type=study.motion.substudy.flex.choice,
                flap_type=study.motion.substudy.flap.choice,
            )
        case "rr":
            aoa = study.motion.substudy.aoa.value
            flap = study.motion.substudy.flap.value
            effaoa = study.motion.substudy.effaoa.value
            motion = params.IB2Motion.make_rr(aoa=aoa, flap=flap)
            U = params.UFromTipFlowPitch(effaoa + aoa)
        case "rx":
            aoa = study.motion.substudy.aoa.value
            bias = study.motion.substudy.bias.value
            flap = study.motion.substudy.flap.value
            twist = -bias if study.motion.substudy.twist else 0
            st = study.motion.substudy.st.value / 100
            motion = params.IB2Motion.make_rx(
                aoa0=bias,
                aoa=aoa,
                flap=flap,
                twist=twist,
            )
            U = params.UFromSt(st)
        case "fw":
            aoa = study.motion.substudy.aoa.value
            bias = study.motion.substudy.bias.value
            flap = study.motion.substudy.flap.value
            twist = -bias
            st = study.motion.substudy.st.value / 100
            motion = params.IB2Motion.make_fw(
                aoa0=bias,
                aoa=aoa,
                flap=flap,
                twist=twist,
            )
            U = params.UFromSt(st)
        case "fot":
            twist_mode = "atan"
            flap = study.motion.substudy.flap.value
            st = study.motion.substudy.st.value / 100
            twist_k = study.motion.substudy.k.value / 100
            motion = params.IB2Motion.make_fot(
                st=st,
                k=twist_k,
                flap=flap,
            )
            U = params.UFromSt(st)
        case "fs":
            flap = study.motion.substudy.flap.value
            motion = params.IB2Motion.make_fs(
                flap=flap,
                sweep=study.motion.substudy.sweep.choice,
            )
            st = study.motion.substudy.st.value / 100
            U = params.UFromSt(st)

    resol = study.resolution.value
    if not study.resolution.on:
        ib2_reslevel = 1
    elif resol <= 20:
        ib2_reslevel = 1
    elif resol <= 40:
        ib2_reslevel = 2
    else:
        ib2_reslevel = 3

    platform_map = {"L": "local", "R": "rockfish", "B": "blackwell", "V": "lenovo"}
    version_map = {"C": "common", "G": "gpu", "M": "common-0.1.0"}

    return params.make_params(
        platform=platform_map[study.platform.choice],
        version=version_map[study.version.choice],
        name=study.encode(),
        allow_restart=True,
        chord_by_dx=study.resolution.value,
        ib2_reslevel=ib2_reslevel,
        motion=motion,
        U=U,
        camber=study.camber.value / 100,
        twist=twist_mode,
        twist_k=twist_k,
        gcss="gcm" if study.resolution.on else "ssm",
        legacy_parallel=study.legacy_parallel.on,
        step_test=study.step_test.on,
        body_test=not study.resolution.on,
    )
