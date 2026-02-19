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


def zip_f(*fs):
    def out_f(*args, **kwargs):
        return (f(*args, **kwargs) for f in fs)

    return out_f
