from .mpi import print_host

_if_print = True


def set_print():
    global _if_print
    _if_print = True


def unset_print():
    global _if_print
    _if_print = False


def log(*args, **kwargs):
    if _if_print:
        print("Info: ", *args, **kwargs)


def log_host(*args, **kwargs):
    if _if_print:
        print_host("Info: ", *args, **kwargs)
