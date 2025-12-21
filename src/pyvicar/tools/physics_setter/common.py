def set_inlet(c, inlet, vel):
    u, v, w = vel
    bc = getattr(c.input.bc, inlet)
    setattr(bc, f"bc{inlet}", "dirichlet")
    setattr(bc, f"u{inlet}", u)
    setattr(bc, f"v{inlet}", v)
    setattr(bc, f"w{inlet}", w)

    c.input.domain.uinit = u
    c.input.domain.vinit = v
    c.input.domain.winit = w


def set_scalar_inlet(var, inlet, val):
    setattr(var, f"bc{inlet}", "dirichlet")
    setattr(var, f"tbc{inlet}", val)
    var.icVal = val


def set_re(c, re, U=1, L=1):
    c.input.timeStep.re = re / (U * L)
