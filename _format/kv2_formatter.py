from .formatter import Formatter
from .tools import find_nearest_tab


class KV2Formatter(Formatter):
    def __init__(self, f):
        Formatter.__init__(self, f)

        self.tabN = 8

    def write(self):
        f = self._f

        fieldlens = [
            find_nearest_tab(field.align_len(self.verbose), tabN=self.tabN, rearblank=1)
            for field in self
        ]

        for field, length in zip(self, fieldlens):
            f.write(f"{field.key_str(self.verbose):<{length-1}} ")

        f.write("\n")

        for field, length in zip(self, fieldlens):
            f.write(f"{field.value_str(self.verbose):<{length-1}} ")

        f.write("\n")

        self._clear_cache()
