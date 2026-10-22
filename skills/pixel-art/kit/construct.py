"""Whole-figure construction: polygon regions -> one canvas -> global light -> lines -> hand edits.

pixelkit stacks parts that are each outlined and lit on their own, which reads as balloons glued
together. Here the figure is built and lit as one form:
1. Regions (polygons or ellipses in canvas px, listed back-to-front) rasterize into one owner map.
2. One light for the whole figure. Each region declares the plane it faces (`tilt`), edges roll
   off with a small bevel (`volume`, off by default: per-part roll-off reads as carved relief), and a
   gentle silhouette-wide gradient gives the figure its one big shadow side. (A single inflated-silhouette height field alone makes faces look down into the neck.)
   `cast` adds contact shadows; isolated tone speckles are cleaned.
3. Lines: ink around the outer silhouette; interior boundaries follow each region's `line`
   policy ('ink' | 'shade' | None) and can be broken by hand edits.
4. Hand edits (face, clumps, folds, line breaks) are ops applied to the final key grid.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

from kit.pixelkit import OUTLINE_KEY, Shadow, hex_rgba

Point = tuple[float, float]


@dataclass(frozen=True)
class Region:
    name: str
    material: str
    shape: tuple[Point, ...]
    line: str | None = "ink"
    volume: float = 1.0
    cast: tuple[int, int] | None = None
    ellipse: bool = False  # shape = (top-left, bottom-right) of the bounding box
    groups: tuple[str, ...] = ()  # no line between regions sharing a group (one continuous form)
    tilt: tuple[float, float] = (0.0, 0.0)  # plane normal x/y slope: +x faces right, +y faces down
    line_vs: tuple[tuple[str, str | None], ...] = ()  # per lower-region-name policy overrides


@dataclass(frozen=True)
class Light:
    direction: tuple[float, float, float] = (-0.5, -0.7, 0.9)
    global_weight: float = 0.35
    blur: float = 4.0
    local_weight: float = 0.0  # per-part edge roll-off; any value hugs every outline with shade (relief look)
    bevel: float = 2.5
    hi: float = 0.86
    shade: float = 0.55
    selout: bool = True  # lit top/left silhouette edges take the material's deep tone instead of ink


@dataclass
class Figure:
    """Ramps map material -> (hi, base, shade, deep) palette keys."""
    size: tuple[int, int]
    palette: dict[str, str]
    ramps: dict[str, tuple[str, str, str, str]]
    regions: list[Region]
    light: Light = field(default_factory=Light)
    ops: list[tuple] = field(default_factory=list)
    shadow: Shadow | None = None


def limb(start: Point, end: Point, w_start: float, w_end: float) -> tuple[Point, ...]:
    """Tapered limb polygon from joint coordinates: e.g. limb(shoulder, wrist, 3, 2) for a slim arm,
    limb(hip, ankle, 4, 3) for a leg. Real limbs taper; equal widths give the cylinder look."""
    (x0, y0), (x1, y1) = start, end
    dx, dy = x1 - x0, y1 - y0
    length = max((dx * dx + dy * dy) ** 0.5, 1e-6)
    nx, ny = -dy / length, dx / length  # unit normal
    a, b = (w_start - 1) / 2, (w_end - 1) / 2  # vertices are inclusive, so a width of w spans +-(w-1)/2
    return ((x0 + nx * a, y0 + ny * a), (x1 + nx * b, y1 + ny * b), (x1 - nx * b, y1 - ny * b), (x0 - nx * a, y0 - ny * a))


def arc_pts(x0: float, x1: float, y: float, sag: float) -> tuple[Point, ...]:
    """Points from (x0, y) to (x1, y) along the front half of a horizontal ring seen from in front and above:
    a parabola dipping `sag` px toward the viewer (down) at the middle. Use for hems, belts, cuffs, collars, hat
    bands, boot tops and rims; sag ~ 15 % of the width (1 px for 4-7 px, 2 for 8-14, 3 for 15-20+).
    Works in either direction, so it can close a polygon: ((x0, top), (x1, top), *arc_pts(x1, x0, bottom, 3))."""
    n = int(abs(x1 - x0)) or 1
    return tuple((x0 + (x1 - x0) * i / n, y + sag * 4 * (i / n) * (1 - i / n)) for i in range(n + 1))


def band(x0: float, x1: float, y: float, thick: float, sag: float) -> tuple[Point, ...]:
    """Curved band polygon (belt, waistband, cuff, collar, hat band): top and bottom edges both sag toward the viewer."""
    return arc_pts(x0, x1, y, sag) + arc_pts(x1, x0, y + thick - 1, sag)


def rasterize(r: Region, size: tuple[int, int]) -> np.ndarray:
    img = Image.new("L", size, 0)
    d = ImageDraw.Draw(img)
    if r.ellipse:
        d.ellipse([r.shape[0], r.shape[1]], fill=1)
    else:
        d.polygon(list(r.shape), fill=1)
    return np.asarray(img, dtype=bool)


def _dilate4(m: np.ndarray) -> np.ndarray:
    return ndimage.binary_dilation(m, structure=ndimage.generate_binary_structure(2, 1))


def _despeckle(tone: np.ndarray, owner: np.ndarray) -> np.ndarray:
    """Replace tone pixels that match none of their same-region 4-neighbours (pixel noise)."""
    out = tone.copy()
    h, w = tone.shape
    for y in range(h):
        for x in range(w):
            if owner[y, x] < 0:
                continue
            nb = [tone[yy, xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if 0 <= yy < h and 0 <= xx < w and owner[yy, xx] == owner[y, x]]
            if nb and tone[y, x] not in nb:
                out[y, x] = max(set(nb), key=nb.count)
    return out


def bresenham(p0: Point, p1: Point) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = map(int, (*p0, *p1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, pts = dx + dy, []
    while True:
        pts.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err, x0 = err + dy, x0 + sx
        if e2 <= dx:
            err, y0 = err + dx, y0 + sy


@dataclass
class Built:
    owner: np.ndarray      # region index per pixel, -1 = empty
    tone: np.ndarray       # 0 hi, 1 base, 2 shade, 3 deep
    keys: np.ndarray       # final palette keys
    ndl: np.ndarray        # light term, for debugging


def build(fig: Figure) -> Built:
    w, h = fig.size
    masks = [rasterize(r, (w, h)) for r in fig.regions]
    owner = np.full((h, w), -1)
    for i, m in enumerate(masks):
        owner[m] = i
    union = owner >= 0

    # One light for the whole figure: designed planes + edge roll-off + gentle silhouette gradient.
    gy, gx = np.gradient(ndimage.gaussian_filter(ndimage.distance_transform_edt(union), fig.light.blur))
    nx, ny = -gx * fig.light.global_weight, -gy * fig.light.global_weight
    for i, r in enumerate(fig.regions):
        visible = owner == i
        if not visible.any():
            continue
        ly, lx = np.gradient(np.minimum(ndimage.distance_transform_edt(visible), fig.light.bevel))
        k = fig.light.local_weight * r.volume
        nx[visible] += -lx[visible] * k + r.tilt[0]
        ny[visible] += -ly[visible] * k + r.tilt[1]
    n = np.stack([nx, ny, np.ones_like(nx)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    lv = np.array(fig.light.direction) / np.linalg.norm(fig.light.direction)
    ndl = n @ lv
    tone = np.where(ndl > fig.light.hi, 0, np.where(ndl > fig.light.shade, 1, 2))
    tone = _despeckle(tone, owner)

    # Contact shadows: darken already-painted lower regions under the caster's shifted silhouette.
    for i, r in enumerate(fig.regions):
        if not r.cast:
            continue
        shifted = np.roll(np.roll(owner == i, r.cast[1], axis=0), r.cast[0], axis=1)
        under = shifted & union & (owner < i) & (owner >= 0)
        tone[under] = np.minimum(tone[under] + 1, 3)

    tone[~union] = -1
    keys = np.full((h, w), ".", dtype="<U1")
    for i, r in enumerate(fig.regions):
        ramp = fig.ramps[r.material]
        sel = owner == i
        keys[sel] = np.array(ramp)[np.clip(tone[sel], 0, 3)]

    # Interior lines go on the lower region's pixels bordering a region drawn in front of it.
    for i, r in enumerate(fig.regions):
        ring = _dilate4(owner == i) & union & (owner < i) & (owner >= 0)
        overrides = dict(r.line_vs)
        for y, x in zip(*np.nonzero(ring)):
            below = fig.regions[owner[y, x]]
            if set(r.groups) & set(below.groups):
                continue
            policy = overrides.get(below.name, r.line)
            if policy == "ink":
                keys[y, x] = OUTLINE_KEY
            elif policy == "shade":
                keys[y, x] = fig.ramps[below.material][3]
    ring = _dilate4(union) & ~union
    keys[ring] = OUTLINE_KEY
    if fig.light.selout:
        # Eastward leaves ~25% of top-facing and ~14% of side-facing silhouette pixels un-inked on the lit
        # side: an outline pixel directly above a highlighted pixel takes that material's deep tone.
        h, w = owner.shape
        for y, x in zip(*np.nonzero(ring)):
            for dy, dx, max_tone in ((1, 0, 0),):
                yy, xx = y + dy, x + dx
                if yy < h and xx < w and owner[yy, xx] >= 0 and tone[yy, xx] <= max_tone:
                    keys[y, x] = fig.ramps[fig.regions[owner[yy, xx]].material][3]
                    break

    for op in fig.ops:
        apply_op(keys, op)
    return Built(owner, tone, keys, ndl)


def apply_op(keys: np.ndarray, op: tuple) -> None:
    """Hand edits: ("px", key, pts) | ("line", key, pts) polyline | ("poly", key, pts) | ("erase", pts)
    | ("block", (x, y), text): paste ASCII rows at (x, y); '_' keeps the pixel, '.' erases it."""
    kind = op[0]
    h, w = keys.shape
    if kind == "block":
        _, (x0, y0), text = op
        for j, row in enumerate(r.strip() for r in text.strip().splitlines() if r.strip()):
            for i, k in enumerate(row):
                if k != "_" and 0 <= y0 + j < h and 0 <= x0 + i < w:
                    keys[y0 + j, x0 + i] = k
        return
    if kind == "erase":
        pts = op[1]
        key = "."
    elif kind == "poly":
        _, key, pts = op
        m = rasterize(Region("op", "", tuple(pts)), (w, h))
        keys[m] = key
        return
    else:
        _, key, pts = op
    if kind == "line":
        pts = [p for a, b in zip(pts, pts[1:]) for p in bresenham(a, b)]
    for x, y in pts:
        if 0 <= x < w and 0 <= y < h:
            keys[int(y), int(x)] = key


def to_image(fig: Figure, keys: np.ndarray) -> Image.Image:
    w, h = fig.size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if fig.shadow:
        from kit.pixelkit import _shadow_layer
        img.alpha_composite(_shadow_layer(fig.shadow, (w, h)))
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = body.load()
    for y, x in zip(*np.nonzero(keys != ".")):
        px[int(x), int(y)] = hex_rgba(fig.palette[keys[y, x]])
    img.alpha_composite(body)
    return img
