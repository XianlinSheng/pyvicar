import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from dataclasses import dataclass
import pyvicar.tools.log as log


def get_grid(c, dir):
    unif = getattr(c.input.domain, f"{dir}gridUnif")
    if unif == "uniform":
        n = getattr(c.input.domain, f"n{dir}").value
        l = getattr(c.input.domain, f"{dir}out").value
        return np.linspace(0, l, n)
    else:
        grid = getattr(c, f"{dir}grid")
        if not grid:
            raise Exception(
                f"{dir} is using nonuniform grid but {dir}grid is not active"
            )
        return grid.nodes.ravel()


# return all primes <= n
def sieve(n):
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i * i : n + 1 : i] = False
    return np.nonzero(is_prime)[0]


# return prime factors of n as a list (multiplicities included)
def prime_factors(n, primes=None):
    factors = []
    if n < 2:
        return factors

    if primes is None:
        primes = sieve(int(n**0.5) + 1)

    for p in primes:
        while n % p == 0:
            factors.append(p)
            n //= p
        if n == 1:
            break
    if n > 1:
        factors.append(n)
    return Counter(factors)


def prime_comb_str(counter):
    return " * ".join([f"{b}^{p}" for b, p in counter.items()])


@dataclass
class Table:
    data: list[list]

    def add(self, row):
        self.data.append(row)
        return self

    def format(self):
        # Step 1: compute max width for each column
        cols = list(zip(*self.data))  # transpose
        col_widths = [max(len(str(item)) for item in col) for col in cols]

        # Step 2: print each row with padding
        out = []
        for row in self.data:
            out.append([str(item).ljust(width) for item, width in zip(row, col_widths)])

        self.data = out
        return self

    def log(self):
        for row in self.data:
            log.log(" ".join(row))


@dataclass
class Grid:
    xyz: tuple
    nxyz: tuple
    ncxyz: tuple
    lxyz: tuple

    @classmethod
    def create(cls, c):
        x = get_grid(c, "x")
        y = get_grid(c, "y")
        z = get_grid(c, "z")
        nx, ny, nz = x.shape[0], y.shape[0], z.shape[0]
        nxc, nyc, nzc = nx - 1, ny - 1, nz - 1
        lx, ly, lz = x[-1], y[-1], z[-1]
        return cls((x, y, z), (nx, ny, nz), (nxc, nyc, nzc), (lx, ly, lz))


def stat_grid_impl(grid, dim2):
    nx, ny, nz = grid.nxyz
    nxc, nyc, nzc = grid.ncxyz

    primes = sieve(int(max(nxc, nyc, nzc) ** 0.5) + 1)

    head = "Grid Stat"
    log.log(f"{head}: Total Cells = {nxc*nyc*nzc:,}, Total Nodes = {nx*ny*nz:,}")
    if dim2:
        log.log(f"{head}: Total 2D Cells = {nxc*nyc:,}, Total 2D Nodes = {nx*ny:,}")

    def report_axis(name, n, nc):
        return [
            f"{head}:",
            f"{name} Nodes",
            f"= {n},",
            f"{name} Segs",
            f"= {nc}",
            f"= {prime_comb_str(prime_factors(nc, primes))}",
        ]

    (
        Table([])
        .add(report_axis("X", nx, nxc))
        .add(report_axis("Y", ny, nyc))
        .add(report_axis("Z", nz, nzc))
        .format()
        .log()
    )


def stat_grid(c):
    stat_grid_impl(Grid.create(c), c.input.domain.nDim == 2)


def show_grid(c, xyz=[0, 0, 0], full=True):
    dim2 = c.input.domain.nDim == 2
    grid = Grid.create(c)
    x, y, z = grid.xyz
    nx, ny, nz = grid.nxyz
    lx, ly, lz = grid.nxyz
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    if dim2 and len(xyz) == 2:
        xyz = [xyz[0], xyz[1], lz / 2]

    if c.unstrucSurface:
        meshes = [
            (surf.xyz.value.startidx, surf.xyz.value.arr, surf.conn.value.arr)
            for surf in c.unstrucSurface.surfaces
        ]
    else:
        meshes = []

    stat_grid_impl(grid, dim2)

    frow, fcol = 3, 3
    fig1 = plt.figure(figsize=(2.5 * fcol, 2.5 * frow))

    ax = fig1.add_subplot(frow, fcol, 1)
    ax.plot(x, "kx-")
    ax.set_title(f"X")

    ax = fig1.add_subplot(frow, fcol, 2)
    ax.plot(y, "kx-")
    ax.set_title(f"Y")

    ax = fig1.add_subplot(frow, fcol, 3)
    ax.plot(z, "kx-")
    ax.set_title(f"Z")

    ax = fig1.add_subplot(frow, fcol, 4)
    dx = x[1:] - x[:-1]
    ax.plot(dx, "kx-")
    ax.set_title(f"DX")

    ax = fig1.add_subplot(frow, fcol, 5)
    dy = y[1:] - y[:-1]
    ax.plot(dy, "kx-")
    ax.set_title(f"DY")

    ax = fig1.add_subplot(frow, fcol, 6)
    dz = z[1:] - z[:-1]
    ax.plot(dz, "kx-")
    ax.set_title(f"DZ")

    ax = fig1.add_subplot(frow, fcol, 7)
    ddx = dx[1:] - dx[:-1]
    ax.plot(ddx, "kx-")
    ax.set_title(f"DDX")

    ax = fig1.add_subplot(frow, fcol, 8)
    ddy = dy[1:] - dy[:-1]
    ax.plot(ddy, "kx-")
    ax.set_title(f"DDY")

    ax = fig1.add_subplot(frow, fcol, 9)
    ddz = dz[1:] - dz[:-1]
    ax.plot(ddz, "kx-")
    ax.set_title(f"DDZ")

    fig1.tight_layout()

    fig2 = plt.figure(figsize=(5, 5))
    ax = fig2.add_subplot(projection="3d")

    kwargs = {"linewidth": 1, "alpha": 0.6}
    if full:
        kwargs["rstride"] = 1
        kwargs["cstride"] = 1

    ax.plot_wireframe(X[:, :, 0], Y[:, :, 0], np.full((nx, ny), xyz[2]), **kwargs)
    ax.plot_wireframe(X[:, 0, :], np.full((nx, nz), xyz[1]), Z[:, 0, :], **kwargs)
    ax.plot_wireframe(np.full((ny, nz), xyz[0]), Y[0, :, :], Z[0, :, :], **kwargs)

    for mesh in meshes:
        start, xyz, conn = mesh
        conn -= start

        ax.plot_trisurf(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            triangles=conn,
            linewidth=0.1,
            edgecolor="k",
            facecolor="w",
        )

    ax.set_title(f"Perspective")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.grid(False)
    ax.set_proj_type("ortho")
    ax.set_aspect("equal", adjustable="box")

    fig2.tight_layout()
    plt.show()
