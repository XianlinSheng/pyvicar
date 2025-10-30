import pyvista as pv
import numpy as np
from abc import abstractmethod
from pyvicar.tools.miscellaneous import split_into_n
import pyvicar.tools.log as log


_is_test = False


def is_test():
    return _is_test


def set_test():
    global _is_test
    _is_test = True


def unset_test():
    global _is_test
    _is_test = False


class _SampleMeshGenerator:
    @abstractmethod
    def to_pyvista_multiblocks():
        pass

    def add_field(self, mb):
        for i in range(len(mb)):
            mesh = mb[i]
            n_cells = mesh.n_cells
            mesh.cell_data["VEL"] = np.random.rand(n_cells, 3)
            mesh.cell_data["P"] = np.random.rand(n_cells)
            mesh.cell_data["GC"] = np.random.rand(n_cells)
            mesh.cell_data["BL"] = np.random.rand(n_cells)
            mesh.cell_data["DISSIP"] = np.random.rand(n_cells)


class _SampleMeshGenerator3DDomain(_SampleMeshGenerator):
    def __init__(self, lx, ly, lz, nx, ny, nz, npx, npy, npz):
        self.lx = lx
        self.ly = ly
        self.lz = lz

        self.nx = nx
        self.ny = ny
        self.nz = nz

        self.npx = npx
        self.npy = npy
        self.npz = npz

    def to_pyvista_multiblocks(self):
        x_full = np.linspace(0, self.lx, self.nx + 1)
        y_full = np.linspace(0, self.ly, self.ny + 1)
        z_full = np.linspace(0, self.lz, self.nz + 1)

        x_sizes = split_into_n(self.nx, self.npx)
        y_sizes = split_into_n(self.ny, self.npy)
        z_sizes = split_into_n(self.nz, self.npz)

        mb = pv.MultiBlock([None] * (self.npx * self.npy * self.npz))

        block_id = 0

        x_start = 0
        for i, x_size in zip(range(self.npx), x_sizes):
            y_start = 0
            for j, y_size in zip(range(self.npy), y_sizes):
                z_start = 0
                for k, z_size in zip(range(self.npz), z_sizes):
                    x = x_full[x_start : x_start + x_size + 1]
                    y = y_full[y_start : y_start + y_size + 1]
                    z = z_full[z_start : z_start + z_size + 1]

                    grid = pv.RectilinearGrid(x, y, z)
                    mb[block_id] = grid
                    mb[block_id].name = f"Block-{i}-{j}-{k}"

                    block_id += 1

                    z_start += z_size
                y_start += y_size
            x_start += x_size

        self.add_field(mb)

        return mb


class sample_option:
    def __new__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls} is a static class used to store configs and cannot be instantiated."
        )

    @classmethod
    def use_3ddomain(cls, lx=10, ly=6, lz=2, nx=10, ny=6, nz=2, npx=2, npy=2, npz=2):
        cls._generator = _SampleMeshGenerator3DDomain(
            lx, ly, lz, nx, ny, nz, npx, npy, npz
        )
        cls._sample = cls._generator.to_pyvista_multiblocks()
        cls._sample_combined = cls._sample.combine()


sample_option.use_3ddomain()


class SampleVTM:
    def __init__(self, path, tstep, seriesi):
        log.log(f"VTM Debug: creating handle for {path}, step {tstep}, No. {seriesi}")
        self._path = path
        self._tstep = tstep
        self._seriesi = seriesi

    @property
    def path(self):
        return self._path

    @property
    def tstep(self):
        return self._tstep

    @property
    def seriesi(self):
        return self._seriesi

    def to_pyvista_multiblocks(self):
        log.log(
            f"VTM Debug: transferring to pyvista mb {self._path}, step {self._tstep}, No. {self._seriesi}"
        )
        return sample_option._sample

    def to_pyvista(self):
        log.log(
            f"VTM Debug: transferring to pyvista combined {self._path}, step {self._tstep}, No. {self._seriesi}"
        )
        return sample_option._sample_combined

    def __repr__(self):
        return f"SampleVTM(tstep = {self._tstep})"


class SampleVTK:
    def __init__(self, path, tstep, seriesi):
        log.log(f"VTK Debug: creating handle for {path}, step {tstep}, No. {seriesi}")
        self._path = path
        self._tstep = tstep
        self._seriesi = seriesi

    @property
    def path(self):
        return self._path

    @property
    def tstep(self):
        return self._tstep

    @property
    def seriesi(self):
        return self._seriesi

    def to_pyvista(self):
        log.log(
            f"VTK Debug: transferring to pyvista combined {self._path}, step {self._tstep}, No. {self._seriesi}"
        )
        return sample_option._sample_combined

    def __repr__(self):
        return f"SampleVTK(tstep = {self._tstep})"
