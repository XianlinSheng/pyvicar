import numpy as np
from .trisurface import TriSurface
from pyvicar._datatype import Dataset2D


class CSplineTri:
    def __init__(self, tFrame, conn, coeff, nSeg, time, periodic, startIdx=1):
        self._tFrame = tFrame
        self._conn = conn
        # coeff[itrinode, ixyz, iseg, abcd]
        self._coeff = coeff
        self._nSeg = nSeg
        self._nFrame = nSeg + 1
        self._time = time
        self._periodic = periodic
        self._startIdx = startIdx

    @property
    def tFrame(self):
        return Dataset2D(self._tFrame.reshape((-1, 1)), self._startIdx)

    @property
    def conn(self):
        return Dataset2D(self._conn, self._startIdx)

    # used for formattable 2d table, order: last axis increases first
    # for ixyz in 3 {for itrinode in ntrinode {for iedge in nedge { [ixyz,itrinode,iedge] }}}
    @property
    def coeff(self):
        return Dataset2D(self._coeff.reshape((-1, 4)), self._startIdx)

    @property
    def tFrame_np(self):
        return self._tFrame

    @property
    def conn_np(self):
        return self._conn

    @property
    def coeff_np(self):
        return self._coeff

    @property
    def nFrame(self):
        return self._nFrame

    @property
    def nSeg(self):
        return self._nSeg

    @property
    def time(self):
        return self._time

    @property
    def periodic(self):
        return self._periodic

    @property
    def startIdx(self):
        return self._startIdx

    def at_time(self, t, startIdx=1):
        t = t % self._time
        iseg = np.searchsorted(self._tFrame, t, side="left") - 1
        dt = self._tFrame[iseg + 1] - self._tFrame[iseg]
        rel_t = (t % dt) / dt
        xyz = np.einsum(
            "ijk,k->ij",
            self._coeff[:, :, iseg, :],
            np.array([1, rel_t, rel_t**2, rel_t**3]),
        )

        return TriSurface(Dataset2D(xyz, startIdx), Dataset2D(self._conn, startIdx))

    # https://mathworld.wolfram.com/CubicSpline.html
    def from_periodic_tri(surfs, time, tFrame=None):
        startidx = surfs[0].xyz.startidx
        conn = surfs[0].conn.arr
        startidx_check = [surf.xyz.startidx == startidx for surf in surfs]
        conn_startidx_check = [surf.conn.startidx == startidx for surf in surfs]
        conn_check = [np.array_equal(surf.conn.arr, conn) for surf in surfs]

        if not all(startidx_check):
            raise Exception(f"vertex startidx not the same for all frames")

        if not all(conn_startidx_check):
            raise Exception(f"connectivity array startidx not eq vertex startidx")

        if not all(conn_check):
            raise Exception(f"connectivity not the same for all frames")

        nSeg = len(surfs)

        if tFrame is None:
            tFrame = [time * iFrame / nSeg for iFrame in range(nSeg + 1)]

        if len(surfs) != len(tFrame) - 1:
            raise Exception(
                f"len of surfs {len(surfs)} should match with tFrame-1 {len(tFrame)}"
            )

        if tFrame[-1] != time:
            raise Exception(
                f"time of last frame {tFrame[-1]} should match duration {time}"
            )

        diag_l = np.diag(np.ones(nSeg - 1), k=-1)
        diag_d = np.diag(np.ones(nSeg))
        diag_u = np.diag(np.ones(nSeg - 1), k=-1)

        A = diag_l + diag_d + diag_u
        A[0, -1] = 1
        A[-1, 0] = 1

        looped_list = surfs[-1:] + surfs + surfs[0:1]
        looped_list = np.array([surf.xyz for surf in looped_list])

        def solve_one(itrinode, ixyz):
            # [nseg], start frame of the seg, include y0 at next cycle
            y = looped_list[1:-1, itrinode, ixyz]
            yp1 = looped_list[2:, itrinode, ixyz]
            ym1 = looped_list[:-2, itrinode, ixyz]

            # nnode eq
            b = 3 * (yp1 - ym1)
            D = np.linalg.solve(A, b)

            D = np.concatenate((D, D[0:1]), axis=0)

            # [nseg]
            # ai = yi, node yi is the start of edge ai
            a = y
            # bi = Di
            b = D[:-1]
            # ci = 3*(y[i+1]-yi)-2Di-D[i+1]
            c = 3 * (yp1 - y) - 2 * D[:-1] - D[1:]
            # di = 2*(yi-y[i+1])+Di+D[i+1]
            d = 2 * (y - yp1) + D[:-1] + D[1:]

            return np.stack((a, b, c, d)).T

        ntrinode = surfs[0].nPoint
        coeff = np.zeros((ntrinode, 3, nSeg, 4))

        for itrinode in range(ntrinode):
            for ixyz in range(3):
                coeff[itrinode, ixyz, :, :] = solve_one(itrinode, ixyz)

        return CSplineTri(np.array(tFrame), conn, coeff, nSeg, time, True, startidx)
