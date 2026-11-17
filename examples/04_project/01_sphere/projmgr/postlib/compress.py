import pyvicar
import projmgr as mgr

pyvicar.assert_api_version("1.0.1", "1.1.0")


mpi_async = False


def post_compress(p):
    c = p.Case(p.name)
    mgr.runlib.init_partition(p, c)

    c.dump.vtm.read()

    # # specify inplace=False to not overwrite the original sub vtrs
    # c.dump.vtm.to_binary()

    c.dump.vtm.to_vtrs(
        c.input.parallel.npx.value,
        c.input.parallel.npx.value,
        keep_vtms=True,
    )
