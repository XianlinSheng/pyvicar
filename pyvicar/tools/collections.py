class struct:
    def from_dict(input):
        s = struct()
        for k, v in input.items():
            s.__setattr__(k, v)

        return s
