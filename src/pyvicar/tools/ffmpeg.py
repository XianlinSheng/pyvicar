import ffmpeg
from pathlib import Path


def probe_video(path):
    probe = ffmpeg.probe(path)
    stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    return int(stream["width"]), int(stream["height"])


def to_path(obj):
    if obj is None:
        return obj

    if isinstance(obj, Path) or isinstance(obj, str):
        path = Path(obj)
        if not path.exists():
            raise ValueError(f"Path does not exist {path}")
        return path

    # special treatments on c.post.animations objects
    # import only if its not a str and might be such an obj to prevent circular import
    from pyvicar.case.post.animations import Video, Animation

    if isinstance(obj, Video):
        return obj.path

    msg = f"Expect a pathlib.Path/str/pyvicar.post.animations.Video object, got type {type(obj)} {obj}"
    if isinstance(obj, Animation):
        msg = f"{msg}. Animation is a set of frames and multiple video formats, use anim[extension] to pick a Video file"

    raise TypeError(msg)


class Canvas:
    def __init__(self, bg, row_height=0.25):
        self.bg = to_path(bg)
        self.row_height_ratio = row_height
        self.rows = []

    def append_row(self, videos):
        self.rows.append([to_path(video) for video in videos])
        return self

    def to_ffmpeg(self):
        # probe background
        bg_w, bg_h = probe_video(self.bg)
        row_h = int(bg_h * self.row_height_ratio)

        # enforce even height (erase last bit)
        row_h &= ~1

        # compute row widths
        row_widths = []

        for row in self.rows:

            width_sum = 0

            for vid in row:
                w, h = probe_video(vid)

                scaled_w = int(round(w * row_h / h))

                # enforce even width
                scaled_w &= ~1

                width_sum += scaled_w

            row_widths.append(width_sum)

        canvas_w = max([bg_w] + row_widths)

        # enforce even width
        canvas_w &= ~1

        # create ffmpeg inputs
        bg_input = ffmpeg.input(self.bg)

        row_streams = []
        input_index = 0

        for row in self.rows:

            vids = []

            for vid in row:
                inp = ffmpeg.input(vid)
                scaled = inp.video.filter("scale", -2, row_h)
                vids.append(scaled)

            if len(vids) == 1:
                row_stream = vids[0]
            else:
                row_stream = ffmpeg.filter(vids, "hstack", inputs=len(vids))

            padded = row_stream.filter("pad", canvas_w, row_h, "(ow-iw)/2", "(oh-ih)/2")

            row_streams.append(padded)

        # pad background
        bg_stream = bg_input.video.filter(
            "pad", canvas_w, bg_h, "(ow-iw)/2", "(oh-ih)/2"
        )

        # vertical stack
        streams = [bg_stream] + row_streams
        if row_streams:
            final = ffmpeg.filter(streams, "vstack", inputs=len(streams))
        else:
            final = bg_stream

        return final


class Array:
    def __init__(self, row_height: int):
        self.row_height = row_height
        self.rows = []

    def append_row(self, videos):
        self.rows.append([to_path(video) for video in videos])
        return self

    def to_ffmpeg(self):
        if not self.rows:
            raise ValueError("No videos input")

        nrows = len(self.rows)
        ncols = max(len(r) for r in self.rows)

        # precompute scaled widths
        scaled_width = {}
        col_width = [0] * ncols

        for r, row in enumerate(self.rows):
            for c, path in enumerate(row):
                if path is None:
                    continue

                w, h = probe_video(path)
                sw = round(w * self.row_height / h)
                sw += sw % 2  # make even for most codecs

                scaled_width[(r, c)] = sw
                col_width[c] = max(col_width[c], sw)

        # column start positions
        col_x = []
        x = 0
        for w in col_width:
            col_x.append(x)
            x += w

        streams = []
        layout = []

        for r, row in enumerate(self.rows):
            for c, path in enumerate(row):
                if path is None:
                    continue

                stream = (
                    ffmpeg.input(path)
                    .filter("scale", scaled_width[(r, c)], self.row_height)
                    .filter("setsar", 1)
                )

                streams.append(stream)

                x = col_x[c] + (col_width[c] - scaled_width[(r, c)]) // 2
                y = r * self.row_height
                layout.append(f"{x}_{y}")

        return ffmpeg.filter(
            streams,
            "xstack",
            inputs=len(streams),
            layout="|".join(layout),
            fill="black",
        )
