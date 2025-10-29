def split_into_n(total, n):
    if not isinstance(total, int) or not isinstance(n, int):
        raise TypeError(
            f"Total number and partition should both be integer, but encountered '{total}' divided into '{n}' parts"
        )
    eachbase = total // n
    extra = total - eachbase * n
    nelems = [eachbase] * n
    nelems = [eachbase + 1 if i < extra else eachbase for i in range(n)]

    return nelems


class args:
    def add_default(new, default):
        default.update(new)
        return default

    def choose(kwargs, chosen):
        return {k: kwargs[k] for k in kwargs if k in chosen}
