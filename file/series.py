import re
from pathlib import Path
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class IndexedFile:
    idxes: list[int]
    path: Path


class Series(Iterable):
    def __init__(self, nameformat, files):
        self._nameformat = nameformat
        self._files = files

    @property
    def nameformat(self):
        return self._nameformat

    def __iter__(self):
        return iter(self._files)
    

    # e.g. nameformat = r'file\.(\d{4})\.(\d{3})\.txt'
    def from_format(basepath, nameformat):
        regex_pattern = re.compile(nameformat)

        files = []
        for file in Path(basepath).iterdir():
            if file.is_file():
                match = regex_pattern.match(file.name)
                if match:
                    idxes = tuple(int(n) for n in match.groups())
                    files.append(IndexedFile(idxes, file))
        
        files.sort(key=lambda obj: obj.idxes)

        return Series(nameformat, files)


if __name__ == '__main__':
    series = Series.from_format('/home/vicar/plate_study/2d/w00f05', r'drag_lift_body_(\d{3})\.csv')
    for file in series:
        print(f'{file.idxes=},{file.path}')

