def set_inlet(case, inlet, vel):
    u, v, w = vel
    bc = getattr(case.input.bc, inlet)
    setattr(bc, f"bc{inlet}", "dirichlet")
    setattr(bc, f"u{inlet}", u)
    setattr(bc, f"v{inlet}", v)
    setattr(bc, f"w{inlet}", w)

    case.input.domain.uinit = u
    case.input.domain.vinit = v
    case.input.domain.winit = w


def set_scalar_inlet(var, inlet, val):
    setattr(var, f"bc{inlet}", "dirichlet")
    setattr(var, f"tbc{inlet}", val)
    var.icVal = val
