def set_thrombosis_vars(case, inlet="x1"):
    case.input.scalars.iScalar = True

    if not case.scalar:
        case.scalar.enable()

    case.scalar.nscalars = 10
    case.scalar.reactionType = "thrombosis"

    vars = case.scalar.vars.appendnew(10)

    vars[0].set_inlet(inlet, 1400)
    vars[1].set_inlet(inlet, 0)
    vars[2].set_inlet(inlet, 2400)
    vars[3].set_inlet(inlet, 7000)
    vars[4].set_inlet(inlet, 0)
    vars[5].set_inlet(inlet, 1)
    vars[6].set_inlet(inlet, 0.05)
    vars[7].set_inlet(inlet, 0)
    vars[8].set_inlet(inlet, 0)

    bp = vars[7]
    bp.iadvec = False
    bp.idiff = False

    rt = vars[8]
    rt.idiff = False

    ti = vars[9]
    ti.iadvec = False
    ti.innerbcType = "isothermal"
    ti.innerbcVal = 1
    ti.sc = 1

    if not case.thrombosis:
        case.thrombosis.enable()
