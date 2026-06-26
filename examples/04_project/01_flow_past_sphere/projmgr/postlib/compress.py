import pyvicar.tools.log as log


def post_compress(p):

    log.log_host(f"Compress Case: {p.name}")

    c = p.Case(p.name)

    c.dump.vtm.read()

    # specify inplace=False to not overwrite the original sub vtrs
    c.dump.vtm.to_binary()
