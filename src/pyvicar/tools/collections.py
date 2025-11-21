class struct:
    def from_dict(input):
        s = struct()
        for k, v in input.items():
            setattr(s, k, v)

        return s

    def __str__(self):
        items = [f"  {k} : {v}" for k, v in vars(self).items()]
        return f"{self.__class__.__name__}\n(\n{'\n'.join(items)}\n)"
