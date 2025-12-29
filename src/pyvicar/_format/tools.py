from dataclasses import dataclass
import pyvicar.tools.log as log


def find_nearest_tab(length, tabN, rearblank):
    mod = length % tabN
    # fill to nearest tab, and leave blank by -rearblank
    nfill = tabN - mod - rearblank
    # fill extra tabs if not enough for rear blank
    while nfill < 0:
        nfill += tabN

    return length + nfill + rearblank


def write_banner(f, content, length=80, filler="="):
    filler = filler[0]
    contentLen = len(content)
    fillerLen = length - contentLen
    leftLen = int(fillerLen / 2)
    rightLen = fillerLen - leftLen

    f.write(f"{filler*leftLen}{content}{filler*rightLen}\n")


@dataclass
class Table:
    data: list[list]

    def create():
        return Table([])

    def add(self, row):
        self.data.append(row)
        return self

    def format(self):
        # fill missing blocks with empty string
        ncol = max([len(row) for row in self.data])
        for row in self.data:
            row += [""] * (ncol - len(row))

        # compute max width for each column
        cols = list(zip(*self.data))  # transpose
        col_widths = [max(len(str(item)) for item in col) for col in cols]

        # print each row with padding
        out = []
        for row in self.data:
            out.append([str(item).ljust(width) for item, width in zip(row, col_widths)])

        self.data = out
        return self

    def log(self):
        for row in self.data:
            log.log(" ".join(row))

    def log_host(self):
        for row in self.data:
            log.log_host(" ".join(row))
