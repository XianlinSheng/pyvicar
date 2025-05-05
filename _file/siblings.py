import re
from pathlib import Path
from collections.abc import Iterable
from enum import Enum
from dataclasses import dataclass


class Siblings(Iterable):
    class FileType(Enum):
        File = 0
        Folder = 1

    def __init__(self, basename, extmap):
        self._basename = basename
        self._extmap = extmap

    @property
    def basename(self):
        return self._basename

    def __getitem__(self, ext):
        if not ext is None:
            ext = str(ext)
        return self._extmap[ext]

    def __iter__(self):
        return iter(self._extmap.values())

    def __bool__(self):
        return len(self._extmap) != 0

    def __len__(self):
        return len(self._extmap)

    def exts(self):
        return self._extmap.keys()

    def extitems(self):
        return self._extmap.items()

    def filter(self, f):
        return Siblings(
            self._basename, dict(filter(lambda item: f(item[1]), self._extmap.items()))
        )

    def files(self):
        return self.filter(lambda f: f.filetype == Siblings.FileType.File)

    def folders(self):
        return self.filter(lambda f: f.filetype == Siblings.FileType.Folder)

    def from_basename(basepath, basename):
        regex_pattern = re.compile(basename + r"(\..+)?")

        files = {}
        for file in Path(basepath).iterdir():
            match = regex_pattern.match(file.name)
            if not match:
                continue
            ext = match.groups()[0]
            if not ext is None:
                ext = str(ext)[1:]

            if file.is_file():
                filetype = Siblings.FileType.File
            elif file.is_dir():
                filetype = Siblings.FileType.Folder
            else:
                print(
                    "Warning: symlink will cause read write lock issues so it is not supported and thus ignored"
                )
                continue

            fileobj = FileWithExtension(basename, ext, file, filetype)
            files[ext] = fileobj

        return Siblings(basename, files)

    def siblings_dict_at_path(basepath):
        siblings = {}
        for file in Path(basepath).iterdir():
            splittednames = file.name.split(".", 1)
            basename = splittednames[0]
            if len(splittednames) == 2:
                ext = splittednames[1]
            else:
                ext = None

            if not basename in siblings:
                siblings[basename] = {}
            files = siblings[basename]

            if file.is_file():
                filetype = Siblings.FileType.File
            elif file.is_dir():
                filetype = Siblings.FileType.Folder
            else:
                print(
                    "Warning: symlink will cause read write lock issues so it is not supported and thus ignored"
                )
                continue

            fileobj = FileWithExtension(basename, ext, file, filetype)
            files[ext] = fileobj

        return {
            basename: Siblings(basename, files) for basename, files in siblings.items()
        }


@dataclass
class FileWithExtension:
    basename: str
    extension: str
    path: Path
    filetype: Siblings.FileType


if __name__ == "__main__":
    siblings = Siblings.from_basename("/home/vicar/plate_study/2d/w02f03/post", "glyph")
    for file in siblings:
        print(f"{file.extension=},{file.path=}")

    siblings_dict = Siblings.siblings_dict_at_path(
        "/home/vicar/plate_study/2d/w02f03/post"
    )
    for basename, siblings in siblings_dict.items():
        print(f"{basename=}, {siblings.basename=},{siblings.exts()=}")

    print(Siblings.siblings_dict_at_path("/home/vicar/plate_study/2d/w02f03/post/vor"))
