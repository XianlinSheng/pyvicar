from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def figure_grid(
    row_height: int,
    rows: list[list[dict]],
    output: str | None = None,
    padding: int = 10,
):
    title_height = int(row_height * 0.1)
    font = ImageFont.load_default(size=int(row_height * 0.05))

    loaded = []
    for row in rows:
        loaded_row = []
        for item in row:
            im = Image.open(item["path"]).convert("RGB")

            # Resize to the specified image height
            width = round(im.width * row_height / im.height)
            im = im.resize((width, row_height), Image.Resampling.LANCZOS)

            loaded_row.append((im, item["title"]))
        loaded.append(loaded_row)

    # Determine column widths
    ncols = max(len(row) for row in loaded)
    col_widths = [
        max(
            (im.width for row in loaded for j, (im, _) in enumerate(row) if j == col),
            default=0,
        )
        for col in range(ncols)
    ]

    # Canvas dimensions
    row_total_height = row_height + title_height
    total_width = sum(col_widths) + padding * (ncols + 1)
    total_height = len(rows) * row_total_height + padding * (len(rows) + 1)

    canvas = Image.new("RGB", (total_width, total_height), "white")
    draw = ImageDraw.Draw(canvas)

    for i, row in enumerate(loaded):
        y = padding + i * (row_total_height + padding)

        for j, (im, title) in enumerate(row):
            x = padding + sum(col_widths[:j]) + padding * j

            # Center image within column
            ix = x + (col_widths[j] - im.width) // 2
            canvas.paste(im, (ix, y))

            # Outline around the entire subplot
            draw.rectangle(
                [(x, y), (x + col_widths[j], y + row_total_height)],
                outline="black",
                width=max(1, int(row_height * 0.005)),
            )

            # Title at top
            bbox = font.getbbox(title)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = x + (col_widths[j] - tw) // 2
            ty = y + (title_height - th) // 2 - bbox[1]
            draw.text((tx, ty), title, fill="black", font=font)

    if output is not None:
        canvas.save(output)

    return canvas
