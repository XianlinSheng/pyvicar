from dataclasses import dataclass
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, TextBox
from scipy import ndimage
from PIL import Image
from abc import abstractmethod


def figure_rearrange(
    image,
    configs,
    output=None,
    trim=True,
    background="white",
):
    """
    Rearrange rectangular regions of a PNG image.

    Parameters
    ----------
    image : str or PIL.Image.Image
        Source image or image path.

    configs : list[dict]
        Each config contains:
            bbox     : [x0, y0, x1, y1], normalized crop coordinates
            anchor   : str, anchor point of the cropped region
            position : [x, y], normalized position on original canvas

        If position is None or omitted, retain the original position.
        If anchor is None or omitted, use "top left".

        Anchor options:
            top left, top center, top right,
            center left, center, center right,
            bottom left, bottom center, bottom right

        Configurations are composited in list order.
        Later configurations appear above earlier ones.

    trim : bool
        If True, crop the final canvas to the union of
        all positioned bounding boxes.
        If False, retain the original canvas dimensions.

    background : tuple or str
        Background color.

    Returns
    -------
    PIL.Image.Image
        Rearranged RGBA image.
    """

    if isinstance(image, (str, Path)):
        image = Image.open(image)

    image = image.convert("RGBA")
    W, H = image.size

    anchors = {
        "top left": (0, 0),
        "top center": (0.5, 0),
        "top right": (1, 0),
        "center left": (0, 0.5),
        "center": (0.5, 0.5),
        "center right": (1, 0.5),
        "bottom left": (0, 1),
        "bottom center": (0.5, 1),
        "bottom right": (1, 1),
    }

    layers = []
    for cfg in configs:
        # Crop coordinates
        x0, y0, x1, y1 = cfg["bbox"]

        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            raise ValueError(f"Invalid bbox: {cfg['bbox']}")

        # Normalize config defaults
        cfg.setdefault("anchor", None)
        cfg.setdefault("position", None)

        if cfg["anchor"] is None:
            cfg["anchor"] = "top left"

        if cfg["position"] is None:
            cfg["position"] = [x0, y0]

        bbox = (
            round(x0 * W),
            round(y0 * H),
            round(x1 * W),
            round(y1 * H),
        )

        layer = image.crop(bbox)

        # Anchor and target position (unchanged)
        anchor = cfg["anchor"].lower()

        if anchor not in anchors:
            raise ValueError(f"Unknown anchor: {anchor}")

        ax, ay = anchors[anchor]
        px, py = cfg["position"]

        px = px * W
        py = py * H

        left = round(px - ax * layer.width)
        top = round(py - ay * layer.height)

        layers.append((layer, left, top))

        if not layers:
            imout = image.copy()
            if output is not None:
                imout.save(output)
            return imout

    # Determine output canvas
    if trim:
        xmin = min(x for _, x, _ in layers)
        ymin = min(y for _, _, y in layers)
        xmax = max(x + layer.width for layer, x, _ in layers)
        ymax = max(y + layer.height for layer, _, y in layers)
    else:
        xmin, ymin = 0, 0
        xmax, ymax = W, H

    imout = Image.new(
        "RGBA",
        (xmax - xmin, ymax - ymin),
        background,
    )

    # Composite layers in order
    for layer, x, y in layers:
        x -= xmin
        y -= ymin

        # Clip to output canvas
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(imout.width, x + layer.width)
        y1 = min(imout.height, y + layer.height)

        if x0 >= x1 or y0 >= y1:
            continue

        cropped = layer.crop(
            (
                x0 - x,
                y0 - y,
                x1 - x,
                y1 - y,
            )
        )

        imout.alpha_composite(cropped, (x0, y0))

    if output is not None:
        imout.save(output)

    return imout


@dataclass
class NBox:
    """Normalized bounding box: [0, 1] × [0, 1]."""

    x0n: float
    y0n: float
    x1n: float
    y1n: float

    def __str__(self):
        x0, y0, x1, y1 = self.x0n, self.y0n, self.x1n, self.y1n
        return f"{x0:.3f}, {y0:.3f}, {x1:.3f}, {y1:.3f}"


@dataclass
class PBox:
    """Pixel bounding box in integer."""

    x0p: int
    y0p: int
    x1p: int
    y1p: int


class FigureContext:
    def __init__(
        self,
        image,
        detect=True,
        color_threshold=30,
        min_area=1e-4,
        close_size=3,
        group_gap_x=1e-2,
        group_gap_y=1e-2,
    ):
        self.image = self.load_image(image)
        self.height, self.width = self.image.shape[:2]

        self.color_threshold = color_threshold
        self.min_area = min_area
        self.close_size = close_size
        self.group_gap_x = group_gap_x
        self.group_gap_y = group_gap_y

        self.boxes = []
        self.selected = None

        self.mouse_mgr = None

        self.create_figure()

        if detect:
            self.detect_boxes()

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def load_image(image):
        if isinstance(image, (str, Path)):
            image = Image.open(image)

        image = image.convert("RGBA")
        rgba = np.asarray(image)

        # Composite transparency onto white.
        alpha = rgba[:, :, 3:4].astype(float) / 255.0
        rgb = rgba[:, :, :3].astype(float)

        return np.clip(rgb * alpha + 255.0 * (1.0 - alpha), 0, 255).astype(np.uint8)

    def normalize(self, xp, yp):
        return xp / self.width, yp / self.height

    def pixelize(self, xn, yn):
        return int(xn * self.width), int(yn * self.height)

    def pclamp(self, xp, yp):
        return np.clip(xp, 0, self.width), np.clip(yp, 0, self.height)

    def nclamp(self, xn, yn):
        return np.clip(xn, 0, 1), np.clip(yn, 0, 1)

    def to_nbox(self, pbox: PBox):
        return NBox(
            *self.normalize(*self.pclamp(pbox.x0p, pbox.y0p)),
            *self.normalize(*self.pclamp(pbox.x1p, pbox.y1p)),
        )

    def to_pbox(self, nbox: NBox):
        return PBox(
            *self.pixelize(*self.nclamp(nbox.x0n, nbox.y0n)),
            *self.pixelize(*self.nclamp(nbox.x1n, nbox.y1n)),
        )

    def event_nxy(self, event):
        if event.inaxes != self.ax or event.xdata is None:
            return None
        return np.array(self.normalize(*self.pclamp(event.xdata, event.ydata)))

    def is_sufficient(self, nbox):
        area = (nbox.x1n - nbox.x0n) * (nbox.y1n - nbox.y0n)
        return area >= self.min_area

    def is_mergable(self, nbox1, nbox2):
        x10, x11 = nbox1.x0n - self.group_gap_x, nbox1.x1n + self.group_gap_x
        y10, y11 = nbox1.y0n - self.group_gap_y, nbox1.y1n + self.group_gap_y
        x20, x21 = nbox2.x0n - self.group_gap_x, nbox2.x1n + self.group_gap_x
        y20, y21 = nbox2.y0n - self.group_gap_y, nbox2.y1n + self.group_gap_y
        return (x10 - x21) * (x11 - x20) <= 0 and (y10 - y21) * (y11 - y20) <= 0

    def merge_nboxes(self, nboxes):
        n = len(nboxes)
        for i in range(n):
            if nboxes[i] is None:
                continue
            j = i + 1
            while j < n:
                if nboxes[j] is None:
                    j += 1
                    continue
                if not self.is_mergable(nboxes[i], nboxes[j]):
                    j += 1
                    continue
                nboxes[i] = NBox(
                    min(nboxes[i].x0n, nboxes[j].x0n),
                    min(nboxes[i].y0n, nboxes[j].y0n),
                    max(nboxes[i].x1n, nboxes[j].x1n),
                    max(nboxes[i].y1n, nboxes[j].y1n),
                )
                nboxes[j] = None
                j = i + 1

        nboxes[:] = [nbox for nbox in nboxes if nbox is not None]

        return nboxes

    def update_coord_box(self):
        textbox = self.coord_box
        if self.selected is None:
            textbox.set_val("")
        else:
            textbox.set_val(self.boxes[self.selected].nbox)

    def select_box(self, ibox):
        if self.selected is not None:
            self.boxes[self.selected].unselect()
        self.selected = ibox
        if self.selected is not None:
            self.boxes[self.selected].select()
        self.update_coord_box()

    def find_box_at(self, xn, yn):
        for i, box in enumerate(self.boxes):
            if (
                box.nbox.x0n <= xn <= box.nbox.x1n
                and box.nbox.y0n <= yn <= box.nbox.y1n
            ):
                return i
        return None

    def find_corner_at(self, xn, yn, tol=0.01):
        if self.selected is None:
            return None

        posn = np.array([xn, yn])
        nbox = self.boxes[self.selected].nbox

        corners = [
            np.array([nbox.x0n, nbox.y0n]),
            np.array([nbox.x1n, nbox.y0n]),
            np.array([nbox.x0n, nbox.y1n]),
            np.array([nbox.x1n, nbox.y1n]),
        ]

        distances = [np.linalg.norm(posn - corner) for corner in corners]

        corner = int(np.argmin(distances))

        if distances[corner] <= tol:
            return corner

        return None

    def delete_selected(self):
        if self.selected is None:
            return

        self.boxes[self.selected].undraw()
        del self.boxes[self.selected]
        for i in range(self.selected, len(self.boxes)):
            box = self.boxes[i]
            box.undraw()
            box.index = i
            box.draw()
        self.selected = None
        self.update_coord_box()

    # ------------------------------------------------------------------
    # Figure and widgets
    # ------------------------------------------------------------------

    def create_figure(self):
        self.fig = plt.figure(figsize=(13, 8))

        self.ax = self.fig.add_axes([0.04, 0.08, 0.68, 0.84])
        self.ax.imshow(self.image)
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(self.height, 0)
        self.ax.set_aspect("equal")
        self.ax.set_title("Figure BBox Detector")
        self.ax.axis("off")

        # Original canvas boundary
        self.canvas_rect = Rectangle(
            (0, 0),
            self.width - 1,
            self.height - 1,
            linewidth=1.5,
            edgecolor="cyan",
            facecolor="none",
            linestyle="--",
        )
        self.ax.add_patch(self.canvas_rect)

        # Detection parameter controls.
        self.color_threshold_box = TextBox(
            self.fig.add_axes([0.80, 0.86, 0.15, 0.04]),
            "Color threshold ",
            initial=str(self.color_threshold),
        )
        self.min_area_box = TextBox(
            self.fig.add_axes([0.80, 0.79, 0.15, 0.04]),
            "Min area ",
            initial=str(self.min_area),
        )
        self.close_size_box = TextBox(
            self.fig.add_axes([0.80, 0.72, 0.15, 0.04]),
            "Close size ",
            initial=str(self.close_size),
        )
        self.gap_x_box = TextBox(
            self.fig.add_axes([0.80, 0.65, 0.15, 0.04]),
            "Group gap X ",
            initial=str(self.group_gap_x),
        )
        self.gap_y_box = TextBox(
            self.fig.add_axes([0.80, 0.58, 0.15, 0.04]),
            "Group gap Y ",
            initial=str(self.group_gap_y),
        )

        self.coord_box = TextBox(
            self.fig.add_axes([0.80, 0.43, 0.17, 0.05]),
            "Selected bbox ",
            initial="",
        )

        self.textboxes = [
            self.color_threshold_box,
            self.min_area_box,
            self.close_size_box,
            self.gap_x_box,
            self.gap_y_box,
            self.coord_box,
        ]

        self.detect_button = Button(
            self.fig.add_axes([0.80, 0.32, 0.17, 0.055]),
            "Detect",
        )
        self.clear_button = Button(
            self.fig.add_axes([0.80, 0.24, 0.17, 0.055]),
            "Clear",
        )

        self.status_text = self.fig.text(
            0.97, 0.08, "", fontsize=9, va="bottom", ha="right"
        )

        self.detect_button.on_clicked(lambda _: self.on_detect())
        self.clear_button.on_clicked(lambda _: self.on_clear())

        self.coord_box.on_submit(self.on_coordinate_submit)

        self.fig.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.fig.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect_boxes(self):
        rgb = self.image.astype(float)

        # Estimate the background color from the image borders.
        border = np.concatenate(
            [
                rgb[0, :, :],
                rgb[-1, :, :],
                rgb[:, 0, :],
                rgb[:, -1, :],
            ]
        )
        background = np.median(border, axis=0)

        distance = np.linalg.norm(rgb - background, axis=2)
        mask = distance > self.color_threshold

        if self.close_size > 1:
            structure = np.ones(
                (self.close_size, self.close_size),
                dtype=bool,
            )
            mask = ndimage.binary_closing(mask, structure=structure)

        labels, count = ndimage.label(mask)
        slices = ndimage.find_objects(labels)

        nboxes = []
        for region in slices:
            if region is None:
                continue

            y_slice, x_slice = region
            nbox = self.to_nbox(
                PBox(
                    x_slice.start,
                    y_slice.start,
                    x_slice.stop,
                    y_slice.stop,
                )
            )
            if self.is_sufficient(nbox):
                nboxes.append(nbox)

        self.merge_nboxes(nboxes)

        self.boxes = [
            BoxArtist.from_nbox(self, i, nbox) for i, nbox in enumerate(nboxes)
        ]
        self.selected = None

    # ------------------------------------------------------------------
    # Selection and editing
    # ------------------------------------------------------------------

    def on_mouse_press(self, event):
        self.mouse_mgr = MouseMgr.from_event(self, event)
        self.fig.canvas.draw_idle()

    def on_mouse_move(self, event):
        nxy = self.event_nxy(event)
        if nxy is None:
            self.status_text.set_text("Out of bound")
            self.fig.canvas.draw_idle()
            return
        self.status_text.set_text(f"Normalized Coordinate [{nxy[0]:.3f}, {nxy[1]:.3f}]")
        self.fig.canvas.draw_idle()
        if self.mouse_mgr is None:
            return
        self.mouse_mgr.move(*nxy)
        self.fig.canvas.draw_idle()

    def on_mouse_release(self, event):
        if self.mouse_mgr is None:
            return
        self.mouse_mgr.release()
        self.mouse_mgr = None
        self.fig.canvas.draw_idle()

    def on_coordinate_submit(self, value):
        if self.selected is None:
            return

        try:
            xy01n = [float(item.strip()) for item in value.split(",")]
            if len(xy01n) != 4:
                raise ValueError("Invalid bbox: expected x0, y0, x1, y1")

            nbox = NBox(*self.nclamp(*xy01n[:2]), *self.nclamp(*xy01n[2:]))
            self.boxes[self.selected].undraw()
            self.boxes[self.selected] = BoxArtist.from_nbox(
                self,
                self.selected,
                nbox,
                selected=True,
            )
            self.status_text.set_text(f"Box {self.selected} resized")
            self.fig.canvas.draw_idle()

        except Exception as e:
            self.status_text.set_text(f"{type(e).__name__}: {e}")

    # ------------------------------------------------------------------
    # Buttons and keyboard
    # ------------------------------------------------------------------

    def on_detect(self):
        try:
            self.color_threshold = float(self.color_threshold_box.text)
            self.min_area = float(self.min_area_box.text)
            self.close_size = int(self.close_size_box.text)
            self.group_gap_x = float(self.gap_x_box.text)
            self.group_gap_y = float(self.gap_y_box.text)

            self.on_clear()
            self.detect_boxes()
            self.fig.canvas.draw_idle()

        except Exception as e:
            self.status_text.set_text(f"{type(e).__name__}: {e}")

    def on_clear(self):
        for box in self.boxes:
            box.undraw()
        self.boxes.clear()
        self.selected = None
        self.fig.canvas.draw_idle()

    def on_key_press(self, event):
        if any(tb.capturekeystrokes for tb in self.textboxes):
            return

        if event.key in ("delete", "x"):
            self.delete_selected()
        elif event.key in ("escape", "q"):
            plt.close(self.fig)

        self.fig.canvas.draw_idle()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self):
        plt.show()
        return self.boxes


@dataclass
class BoxArtist:
    ctx: FigureContext
    index: int
    nbox: NBox
    pbox: PBox
    selected: bool

    @classmethod
    def from_pbox(cls, ctx, index, pbox, selected=False):
        box = cls(ctx, index, ctx.to_nbox(pbox), pbox, selected)
        box.draw()
        return box

    @classmethod
    def from_nbox(cls, ctx, index, nbox, selected=False):
        box = cls(ctx, index, nbox, ctx.to_pbox(nbox), selected)
        box.draw()
        return box

    def draw(self):
        edge_color = "red" if self.selected else "lime"
        line_width = 2.0 if self.selected else 1.3

        self._rect = Rectangle(
            (self.pbox.x0p, self.pbox.y0p),
            self.pbox.x1p - self.pbox.x0p,
            self.pbox.y1p - self.pbox.y0p,
            fill=False,
            edgecolor=edge_color,
            linewidth=line_width,
            zorder=5,
        )

        # draw
        self._tag = self.ctx.ax.text(
            self.pbox.x0p,
            self.pbox.y0p,
            str(self.index),
            color="black",
            fontsize=9,
            ha="left",
            va="bottom",
            zorder=6,
            bbox={
                "boxstyle": "square,pad=0.15",
                "facecolor": edge_color,
                "edgecolor": edge_color,
                "alpha": 0.9,
            },
        )

        self.ctx.ax.add_patch(self._rect)

        # draw 4 corners
        if self.selected:
            corners = [
                (self.pbox.x0p, self.pbox.y0p),
                (self.pbox.x1p, self.pbox.y0p),
                (self.pbox.x0p, self.pbox.y1p),
                (self.pbox.x1p, self.pbox.y1p),
            ]
            self._corners = [
                self.ctx.ax.plot(
                    x,
                    y,
                    marker="s",
                    markersize=6,
                    markerfacecolor="yellow",
                    markeredgecolor="black",
                    zorder=8,
                )[0]
                for x, y in corners
            ]

    def undraw(self):
        self._rect.remove()
        self._tag.remove()
        if self.selected:
            for corner in self._corners:
                corner.remove()

    def select(self):
        self.undraw()
        self.selected = True
        self.draw()

    def unselect(self):
        self.undraw()
        self.selected = False
        self.draw()


class MouseMgr:
    @abstractmethod
    def press(self):
        pass

    @abstractmethod
    def move(self, xn, yn):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def cancel(self):
        pass

    # dispatch to mgr handling different behaviors on a press event
    # return None if no further behaviors
    @classmethod
    def dispatch_event(cls, ctx, event):
        nxy = ctx.event_nxy(event)
        if nxy is None:
            return None

        if event.button == 3 and ctx.mouse_mgr is not None:
            ctx.mouse_mgr.cancel()
            return None

        if event.button == 3 and ctx.mouse_mgr is None and ctx.selected is not None:
            print(f"Box {ctx.selected}: [{ctx.boxes[ctx.selected].nbox}]")
            return None

        if event.button != 1:
            return None

        # below are left click behaviors

        corner = ctx.find_corner_at(*nxy)

        # has a selected box and clicking a corner of it
        if corner is not None:
            return DragResize(corner)

        # corner is None if no selected box or not clicking any corner of it
        ibox = ctx.find_box_at(*nxy)

        # not clicking the currently selected box, select it and end
        if ibox != ctx.selected:
            ctx.select_box(ibox)
            return None

        # clicking on blanks
        if ctx.selected is None:
            return DragCreate(*nxy)

        return None

    @classmethod
    def from_event(cls, ctx, event):
        mgr = cls.dispatch_event(ctx, event)
        if mgr is not None:
            mgr.ctx = ctx
            mgr.press()
        return mgr


class DragCreate(MouseMgr):
    def __init__(self, x0n, y0n):
        self.x0n = x0n
        self.y0n = y0n

    def press(self):
        self.ibox = len(self.ctx.boxes)
        self.box = None

    def move(self, x1n, y1n):
        ctx = self.ctx
        nbox = NBox(
            min(self.x0n, x1n),
            min(self.y0n, y1n),
            max(self.x0n, x1n),
            max(self.y0n, y1n),
        )

        if self.box is not None:
            self.box.undraw()

        if ctx.is_sufficient(nbox):
            self.box = BoxArtist.from_nbox(ctx, self.ibox, nbox, selected=True)
        else:
            self.box = None

    def release(self):
        if self.box is None:
            return

        ctx = self.ctx
        ctx.boxes.append(self.box)
        ctx.select_box(self.ibox)

    def cancel(self):
        if self.box is not None:
            self.box.undraw()


class DragResize(MouseMgr):
    def __init__(self, corner):
        self.corner = corner

    def press(self):
        ctx = self.ctx
        self.ix = (self.corner % 2) * 2
        self.iy = int(self.corner / 2) * 2 + 1
        nbox = ctx.boxes[ctx.selected].nbox
        self.xy01n = np.array([nbox.x0n, nbox.y0n, nbox.x1n, nbox.y1n])
        # switch plot to the tmp obj
        ctx.boxes[ctx.selected].undraw()
        self.box = BoxArtist.from_nbox(
            ctx,
            ctx.selected,
            nbox,
            selected=True,
        )

    def move(self, xn, yn):
        ctx = self.ctx
        self.xy01n[self.ix] = xn
        self.xy01n[self.iy] = yn

        nbox = NBox(*self.xy01n)
        if ctx.is_sufficient(nbox):
            self.box.undraw()
            self.box = BoxArtist.from_nbox(
                ctx,
                ctx.selected,
                nbox,
                selected=True,
            )

    def release(self):
        # hand over tmp obj ownership to formal list
        ctx = self.ctx
        ctx.boxes[ctx.selected] = self.box
        ctx.update_coord_box()

    def cancel(self):
        # switch the plot back
        ctx = self.ctx
        self.box.undraw()
        ctx.boxes[ctx.selected].draw()


def detect_figure_bbox(image, init_args={}):
    context = FigureContext(image=image, **init_args)
    return context.run()
