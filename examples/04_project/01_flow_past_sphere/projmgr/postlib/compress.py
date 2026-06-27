import pyvicar

pyvicar.assert_api_version("1.0.1", "1.1.0")

mpi_async = False


def post_compress(p):

    c = p.Case(p.name)

    c.dump.vtm.read()

    # specify inplace=False to not overwrite the original sub vtrs
    c.dump.vtm.to_binary()
