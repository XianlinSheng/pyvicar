import numpy as np
from abc import ABC, abstractmethod
from collections.abc import Iterable
from .io import Writable
from pyvicar.tree.field import Verbose, Field, Point3D, Dataset2D


# A formatter formats a line of Field (in a buffer) and write file
class Formatter(Iterable, Writable):
    def __init__(self, f):
        self._f = f
        self._buffer = []
        self.verbose = Verbose.keyall

    def __iter__(self):
        return iter(self._buffer)

    def __repr__(self):
        return f"Formatter({self._buffer})"

    def __iadd__(self, newfield):
        if isinstance(newfield, Iterable):
            self._buffer += newfield
        else:
            self._buffer.append(newfield)
        return self
    
    def _clear_cache(self):
        self._buffer = []


class KV2Formatter(Formatter):
    def __init__(self, f):
        Formatter.__init__(self, f)

        self.tabN = 8
    
    def write(self):
        f = self._f

        fieldlens = [find_nearest_tab(field.align_len(self.verbose), tabN=self.tabN, rearblank=1) for field in self]

        for field, length in zip(self, fieldlens):
            f.write(f"{field.key_str(self.verbose):<{length-1}} ")

        f.write('\n')

        for field, length in zip(self, fieldlens):
            f.write(f"{field.value_str(self.verbose):<{length-1}} ")

        f.write('\n')

        self._clear_cache()


class KV1Formatter(Formatter):
    def __init__(self, f):
        Formatter.__init__(self, f)

        self.kvtabN = 8     # tab for key or value
        self.lrtabN = 8     # tab for left and right section
        self.splittabN = 16 # tab for middle split
        self.minsplit = 32  # min position for middle split
        self.splittext = '' # add text at middle split


    def write(self):
        f = self._f

        valuelens = [find_nearest_tab(field.value_len(self.verbose), tabN=self.kvtabN, rearblank=1) for field in self]
        totalvaluelen = sum(valuelens)
        splitlen = max(totalvaluelen, self.minsplit)

        for field, valuelen in zip(self, valuelens):
            f.write(f"{field.value_str(self.verbose):<{valuelen-1}} ")

        nfill = find_nearest_tab(splitlen, tabN=self.lrtabN, rearblank=0) - totalvaluelen
        f.write(' ' * nfill)

        splittextlen = find_nearest_tab(len(self.splittext), tabN=self.splittabN, rearblank=1)
        f.write(f'{self.splittext:<{splittextlen-1}} ')

        keylens = [find_nearest_tab(field.key_len(self.verbose), tabN=self.kvtabN, rearblank=1) for field in self]
        totalkeylen = sum(keylens)

        for field, keylen in zip(self, keylens):
            f.write(f"{field.key_str(self.verbose):<{keylen-1}} ")
        
        f.write('\n')

        self._clear_cache()


class DatasetFormatter(Formatter):
    def __init__(self, f):
        Formatter.__init__(self, f)

        self.tabN = 24      # tab of a row column
        self.blankN = 1     # leave blank rows between two datasetget
        self.printidx = False


    def write(self):
        f = self._f

        for field in self:
            # implict convert Point3D -> Dataset2D (1, 3)
            if isinstance(field.value, Point3D):
                field = Field(field.key, Dataset2D(np.array([field.value.xyz], dtype=float)))

            if not isinstance(field.value, Dataset2D):
                raise TypeError(f'DatasetFormatter is for Dataset2D Field only, but encountered {field}')

            arr = field.value.arr

            for rowi, row in enumerate(arr):
                strlist = []
                if self.printidx:
                    strlist.append(f'{rowi + field.value.startidx:<{self.tabN - 1}}')
                for col in row:
                    strlist.append(f'{col:<{self.tabN - 1}}')

                f.write(' '.join(strlist))
                f.write('\n')
            
            for _ in range(self.blankN):
                f.write('\n')

        self._clear_cache()


def find_nearest_tab(length, tabN, rearblank):
    mod = length % tabN
    # fill to nearest tab, and leave blank by -rearblank
    nfill = tabN - mod - rearblank
    # fill extra tabs if not enough for rear blank
    while nfill < 0:
        nfill += tabN
    
    return length + nfill + rearblank


def write_banner(f, content, length=80, filler='='):
    filler = filler[0]
    contentLen = len(content)
    fillerLen = length - contentLen
    leftLen = int(fillerLen / 2)
    rightLen = fillerLen - leftLen

    f.write(f'{filler*leftLen}{content}{filler*rightLen}\n')

