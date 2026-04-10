# no return value, simply call multiple functions with same signature
def compose_f(*fs):
    def out_f(*args, **kwargs):
        for f in fs:
            f(*args, **kwargs)

    return out_f


# with return value, first var is pipeline var and returned to the next function
def pipeline_f(*fs):
    def out_f(v, *args, **kwargs):
        for f in fs:
            v = f(v, *args, **kwargs)
        return v

    return out_f


def send_pipe_f(f0, fs):
    def out_f(*args, **kwargs):
        v = f0(*args, **kwargs)
        for f in fs:
            v = f(v, *args, **kwargs)
        return v

    return out_f


def recv_pipe_f(fs, fn):
    def out_f(*args, **kwargs):
        for f in fs:
            v = f(v, *args, **kwargs)

        fn(v, *args, **kwargs)

    return out_f


def zip_f(*fs):
    def out_f(*args, **kwargs):
        return (f(*args, **kwargs) for f in fs)

    return out_f


def f_or_uniform_f(f, v):
    return uniform_f(v) if f is None else f


def uniform_f(v):
    def out_f(*args, **kwargs):
        return v

    return out_f
