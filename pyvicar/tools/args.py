def add_default(new, default):
    default.update(new)
    return default


def choose(kwargs, chosen):
    return {k: kwargs[k] for k in kwargs if k in chosen}
