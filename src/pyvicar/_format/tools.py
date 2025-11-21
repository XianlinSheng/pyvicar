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
