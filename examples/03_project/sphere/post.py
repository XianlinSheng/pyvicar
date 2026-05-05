import sys
import studies
import postlib
import pyvicar.tools.mpi as mpi

# usage  : python post.py <job> <code>
# example: python post.py compress re200rec

job = sys.argv[1]
code = sys.argv[2]
# code = "re1000rec"

p = studies.to_params(code)

match job:
    case "compress":
        postlib.post_compress(p)
    case "draglift":
        postlib.post_draglift(p)
    case "isoq":
        postlib.post_isoq(p)
    case "slicecontour":
        postlib.post_slicecontour(p)
    case _:
        raise Exception(f"Unrecognized post job name {job}")

mpi.print_elapsed_time()
