import pyvista as pv
import numpy as np
import shutil
from pathlib import Path
import pyvicar.tools.mpi as mpi


def combine_vtr(vtm, ijs):
    # reconstruct full grid first
    xs = {}
    ys = {}
    for iblock, (ip, jp) in enumerate(ijs):
        block = vtm[iblock]
        xs[ip] = block.x
        ys[jp] = block.y

    xs = [xs[key] for key in sorted(xs)]
    ys = [ys[key] for key in sorted(ys)]

    ic0 = [0]
    for x in xs[:-1]:
        ic0.append(ic0[-1] + x.shape[0] - 1)
    jc0 = [0]
    for y in ys[:-1]:
        jc0.append(jc0[-1] + y.shape[0] - 1)

    xs = [xs[0]] + [x[1:] for x in xs[1:]]
    ys = [ys[0]] + [y[1:] for y in ys[1:]]

    x = np.concatenate(xs, axis=0)
    y = np.concatenate(ys, axis=0)
    z = vtm[0].z

    nx = x.shape[0]
    ny = y.shape[0]
    nz = z.shape[0]

    nxc = nx - 1
    nyc = ny - 1
    nzc = nz - 1

    full = pv.RectilinearGrid(x, y, z)

    # combine fields
    sample_block = vtm[0]
    for name in sample_block.cell_data:
        tensor_shape = sample_block.cell_data[name].shape[1:]
        fullshape = (nxc, nyc, nzc) + tensor_shape
        field = np.zeros(fullshape, dtype=sample_block.cell_data[name].dtype)
        for iblock, (ip, jp) in enumerate(ijs):
            block = vtm[iblock]
            bnx, bny, bnz = block.dimensions
            bnxc, bnyc, bnzc = bnx - 1, bny - 1, bnz - 1
            bshape = (bnxc, bnyc, bnzc) + tensor_shape
            field[
                ic0[ip] : ic0[ip] + bnxc,
                jc0[jp] : jc0[jp] + bnyc,
                ...,
            ] = block.cell_data[name].reshape(bshape, order="F")

        ravel_shape = (nxc * nyc * nzc,) + tensor_shape
        full.cell_data[name] = field.reshape(ravel_shape, order="F")

    return full


def create_ijs_from_forxy(npx, npy):
    list1 = []
    for ip in range(npx):
        for jp in range(npy):
            list1.append((ip, jp))
    return list1


def compress_to_vtk(vtms):
    for vtm in mpi.dispatch(vtms):
        print(f"compressing {vtm.path}")
        basename = vtm.path.stem
        mesh = pv.read(vtm.path)

        # vtk unstruc combine
        npoints_sum = sum(block.n_points for block in mesh)
        mesh = mesh.combine()
        mesh = mesh.clean(tolerance=1e-6)
        npoints_merged = mesh.n_points
        print(f"{npoints_sum = }, {npoints_merged = }")
        newpath = vtm.path.parent / Path(f"{basename}.vtk")
        mesh.save(newpath, binary=True)

        if vtm.path.exists():
            vtm.path.unlink()
        vtrfolder = vtm.path.parent / Path(f"{basename}")
        if vtrfolder.exists():
            shutil.rmtree(vtrfolder)


def compress_to_vtr(vtms, ijs):
    for vtm in mpi.dispatch(vtms):
        print(f"compressing {vtm.path}")
        basename = vtm.path.stem
        mesh = pv.read(vtm.path)

        # vtr reconstruction
        mesh = combine_vtr(mesh, ijs)
        newpath = vtm.path.parent / Path(f"{basename}.vtr")
        mesh.save(newpath, binary=True)

        if vtm.path.exists():
            vtm.path.unlink()
        vtrfolder = vtm.path.parent / Path(f"{basename}")
        if vtrfolder.exists():
            shutil.rmtree(vtrfolder)
