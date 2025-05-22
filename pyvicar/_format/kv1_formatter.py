from .formatter import Formatter
from .tools import find_nearest_tab


class KV1Formatter(Formatter):
    def __init__(self, f):
        Formatter.__init__(self, f)

        self.kvtabN = 8  # tab for key or value
        self.lrtabN = 8  # tab for left and right section
        self.splittabN = 16  # tab for middle split
        self.minsplit = 32  # min position for middle split
        self.splittext = ""  # add text at middle split

    def write(self):
        f = self._f

        valuelens = [
            find_nearest_tab(
                field.value_len(self.verbose), tabN=self.kvtabN, rearblank=1
            )
            for field in self
        ]
        totalvaluelen = sum(valuelens)
        splitlen = max(totalvaluelen, self.minsplit)

        for field, valuelen in zip(self, valuelens):
            f.write(f"{field.value_str(self.verbose):<{valuelen-1}} ")

        nfill = (
            find_nearest_tab(splitlen, tabN=self.lrtabN, rearblank=0) - totalvaluelen
        )
        f.write(" " * nfill)

        splittextlen = find_nearest_tab(
            len(self.splittext), tabN=self.splittabN, rearblank=1
        )
        f.write(f"{self.splittext:<{splittextlen-1}} ")

        keylens = [
            find_nearest_tab(field.key_len(self.verbose), tabN=self.kvtabN, rearblank=1)
            for field in self
        ]
        totalkeylen = sum(keylens)

        for field, keylen in zip(self, keylens):
            f.write(f"{field.key_str(self.verbose):<{keylen-1}} ")

        f.write("\n")

        self._clear_cache()
