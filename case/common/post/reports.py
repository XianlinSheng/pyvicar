import pandas as pd
import numpy as np
import shutil
import matplotlib.pyplot as plt
from collections.abc import Sequence
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Dict, List
from pyvicar._file import Readable
from pyvicar._file import Series, Siblings
import pyvicar.tools.mpi as mpi


class ReportDict(Dict, Readable, Optional):
    def __init__(self, post):
        Dict.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._post = post
        self._path = self._post.path / "Reports"

    def _init(self):
        if mpi.is_synchost_or_async():
            self._path.mkdir(exist_ok=True)
        mpi.barrier_or_async()

    def _elemcheck(self, new):
        if not isinstance(new, Report):
            raise TypeError(
                f"Expected an Report to be inside an ReportDict, but encountered {repr(new)}"
            )

    def __setitem__(self, _):
        raise AttributeError(
            f"[] = ... syntax not supported, reports are not resettable, to add new item, use reports.add_new(name) instead"
        )

    def __delitem__(self, key):
        rep = self._childrendict[key]
        rep.clear()
        del self._childrendict[key]

    def clear(self):
        for rep in self._childrendict.values():
            rep.clear()
        self._childrendict.clear()

    def read(self):
        if not self._path.exists():
            return

        self.enable()

        siblingsdict = Siblings.siblings_dict_at_path(self._path)
        for basename in siblingsdict.keys():
            rep = Report(self, basename)
            self._childrendict[basename] = rep
            rep.read()

    def enable(self):
        super().enable()
        self._init()

    def _disable(self):
        return super().disable()

    @property
    def path(self):
        return self._path

    def add_new(self, name):
        name = str(name)
        if name in self._childrendict:
            raise KeyError(f"Name '{name}' already exists, change another name")

        rep = Report(self, name)
        self._childrendict[name] = rep

        return rep


class Report(Group, Dict, Readable):
    def __init__(self, reports, name):
        Group.__init__(self)
        Dict.__init__(self)
        self._reports = reports
        self._path = reports.path
        self._name = name

        self._children.rows = Rows(self, name)

        self._finalize_init()

    def __delattr__(self, name):
        if name != "rows":
            raise AttributeError(
                f"By default an attribute in Group is static and thus not deletable"
            )

        if self._children.rows and mpi.is_synchost_or_async():
            shutil.rmtree(self._children.rows.path)
        mpi.barrier_or_async()

        self._children.rows = Rows(self, self._name)

    def _elemcheck(self, new):
        if not isinstance(new, Table):
            raise TypeError(
                f"Expected a Table to be inside an Report, but encountered {repr(new)}"
            )

    def __setitem__(self, _):
        raise AttributeError(
            f"[] = ... syntax not supported, tables are read-only and are not resettable"
        )

    def __delitem__(self, key):
        table = self._childrendict[key]
        if mpi.is_synchost_or_async():
            table.path.unlink()
        mpi.barrier_or_async()
        del self._childrendict[key]

    def __repr__(self):
        return f"Report('{self._name}'; rows: {len(self._children.rows) if self._children.rows else 'inactive'}; tables: {list(self._childrendict.keys())})"

    def clear(self):
        for table in self._childrendict.values():
            if mpi.is_synchost_or_async():
                table.path.unlink()
            mpi.barrier_or_async()
        self._childrendict.clear()

        if self._children.rows and mpi.is_synchost_or_async():
            shutil.rmtree(self._children.rows.path)
        mpi.barrier_or_async()

        self._children.rows = Rows(self, self._name)

    def read(self):
        siblings = Siblings.from_basename(self._path, self._name)
        folders = siblings.folders()
        files = siblings.files()

        # rows folder
        if None in folders.exts():
            self._children.rows.enable()
            self._children.rows.read()

        # table files
        for file in files:
            # table does not need to be read
            table = Table(file.path, file.extension)
            self._childrendict[file.extension] = table

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    def table_visual_by_matplotlib(self, fig, *args, **kwargs):
        path = self._path / f"{self._name}.png"
        fig.savefig(path, *args, **kwargs)
        plt.close(fig)

    def table_by_dict(self, row, **kwargs):
        path = self._path / f"{self._name}.csv"

        # convert to csv compatible (split vector)
        row = _dict_to_csv_row(row, **kwargs)

        pd.DataFrame([row]).to_csv(path, index=False)


class Rows(List, Readable, Optional):
    def __init__(self, report, name):
        List.__init__(self)
        Optional.__init__(self)
        self._report = report
        self._path = report.path / name
        self._name = name

    def _init(self):
        if mpi.is_synchost_or_async():
            self._path.mkdir(exist_ok=True)
        mpi.barrier_or_async()

    def __delitem__(self, index):
        row = self._childrenlist[self._offset_i(index)]
        if mpi.is_synchost_or_async():
            row.path.unlink()
        mpi.barrier_or_async()
        del self._childrenlist[self._offset_i(index)]

    def clear(self):
        if mpi.is_synchost_or_async():
            for row in self._childrenlist:
                row.path.unlink()
        mpi.barrier_or_async()
        self._childrenlist.clear()

    def read(self):
        series = Series.from_format(self._path, self._name + r"\.(\d+)\.csv")

        for file in series:
            row = Row(file.path, file.idxes[0])
            self._childrenlist.append(row)

        if self._childrenlist:
            self._startidx = self._childrenlist[0].idx

    def enable(self):
        super().enable()
        self._init()

    def _disable(self):
        return super().disable()

    @property
    def path(self):
        return self._path

    def has_row(self):
        return len(self._childrenlist) > 0

    def row_by_dict(
        self, seriesi, row, seriesi_col=False, seriesi_label="seriesi", **kwargs
    ):
        path = self._path / f"{self._name}.{seriesi}.csv"

        # convert to csv compatible (split vector)
        row = _dict_to_csv_row(row, **kwargs)

        if seriesi_label in row:
            raise KeyError(
                f"Attempted to add a seriesi column, but the specified label already exists '{seriesi_label}': {row[seriesi_label]}"
            )
        if seriesi_col:
            row[seriesi_label] = seriesi

        pd.DataFrame([row]).to_csv(path, index=False)

    def to_full_table(self):
        dfs = [pd.read_csv(row.path) for row in self]
        combined_df = pd.concat(dfs, ignore_index=True)

        path = self._report.path / f"{self._name}.csv"
        combined_df.to_csv(path, index=False)


class Row(Group):
    def __init__(self, path, idx):
        Group.__init__(self)
        Optional.__init__(self)
        self._path = path
        self._idx = idx

    @property
    def path(self):
        return self._path

    @property
    def idx(self):
        return self._idx


class Table(Group):
    def __init__(self, path, extension):
        Group.__init__(self)
        self._path = path
        self._extension = extension

    @property
    def path(self):
        return self._path

    @property
    def extension(self):
        return self._extension

    def to_pandas(self):
        return pd.read_csv(self._path)


def _dict_to_csv_row(
    row,
    split_vector=True,
    split_vector_args={},
):
    split_vector_args = {
        **{
            "suffix": "xyz",
            "keep_original": True,
            "norm": False,
            "norm_label": "norm",
        },
        **split_vector_args,
    }

    # split vector-like value [1, 2, 3] into multiple cols with suffix _x _y _z ... _suffix[n]
    if split_vector:
        max_split = len(split_vector_args["suffix"])
        key_to_remove = []
        more_kv = {}
        for key, value in row.items():
            match value:
                case str():
                    continue
                case Sequence():
                    ncomp = len(value)
                case np.ndarray():
                    if len(value.shape) != 1:
                        raise ValueError(
                            f"Cannot split a multidimensional array shape {value.shape}"
                        )
                    ncomp = value.shape[0]
                case _:
                    continue

            if ncomp > max_split:
                raise ValueError(
                    f"Attempted to split vector to cols with suffix '{split_vector_args['suffix']}', but encountered {ncomp} components {value}, suffix not enough"
                )

            for comp, suffix in zip(value, split_vector_args["suffix"]):
                more_kv[f"{key}_{suffix}"] = comp

            if split_vector_args["norm"]:
                arr = np.array(value)
                more_kv[f"{key}_{split_vector_args['norm_label']}"] = np.linalg.norm(
                    arr
                )

            if not split_vector_args["keep_original"]:
                key_to_remove.append(key)

        for key in key_to_remove:
            del row[key]

        row.update(more_kv)

    return row
