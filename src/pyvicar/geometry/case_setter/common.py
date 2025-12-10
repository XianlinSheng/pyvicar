def append_solid(case, mesh):
    case.input.internalBoundary.internalBoundaryPresent = True

    case.canonicalBody.nBody = case.canonicalBody.nBody.value + 1
    case.canonicalBody.nBodySolid = case.canonicalBody.nBodySolid.value + 1
    body = case.canonicalBody.bodies.appendnew()
    body.general.bodyType = 'unstruc'
    body.general.nPtsGCMBodyMarker = mesh.xyz.shape[0]
    body.general.nTriElement = mesh.conn.shape[0]

    if not case.unstrucSurface:
        case.unstrucSurface.enable()
        surf = case.unstrucSurface.surfaces.appendnew()
        surf.nPoint = mesh.xyz.shape[0]
        surf.nElem = mesh.conn.shape[0]
        surf.xyz = mesh.xyz
        surf.conn = mesh.conn

    