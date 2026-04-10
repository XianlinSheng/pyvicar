from dataclasses import fields


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
    # recursive: if an item is a subdict, add default values to it from its counterpart in default dict
    @staticmethod
    def add_default(new, default, recursive=False, inplace=True):
        if recursive:
            for k, subdict in new.items():
                if not isinstance(subdict, dict):
                    continue
                if k not in default:
                    continue
                if not isinstance(default[k], dict):
                    raise Exception(
                        f"add_default recursive is specified, but for the key {k} the specified subdict {subdict} expects also a subdict for default dict, but encountered {default[k]}"
                    )
                new[k] = args.add_default(subdict, default[k], recursive=True)

        default.update(new)

        if inplace:
            for k, v in default.items():
                new[k] = v
            out = new
        else:
            out = default

        return out

    @staticmethod
    def choose(kwargs, chosen):
        return {k: kwargs[k] for k in kwargs if k in chosen}

    @staticmethod
    def none_to_default_impl(pds_it):
        for passv, defaultv, setter in pds_it:
            if passv is None:
                setter(defaultv)

    @staticmethod
    def none_to_default(pass_list, default_list):
        return [
            defaultv if passv is None else passv
            for passv, defaultv in zip(pass_list, default_list)
        ]


def broadcast_ops(cls, ops):
    def make_op(op):
        def method(self, other):
            return cls(
                *[
                    op(getattr(self, f.name), getattr(other, f.name))
                    for f in fields(self)
                ]
            )

        return method

    for op in ops:
        setattr(cls, f"__{op}__", make_op(getattr(operator, op)))

    return cls


def broadcast_arith_ops(cls):
    ops = ["add", "sub", "mul", "truediv"]
    return broadcast_ops(cls, ops)
