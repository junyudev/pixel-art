"""Tiny pixel-art kit: hand-authored ASCII parts -> outlined, composited frames -> sheets/GIFs.

A Part is an ASCII grid where each char is a palette key ('.' or ' ' = transparent).
Frames are lists of Place (part + offset), painted back-to-front. Lighting rules learned from
Eastward references are applied automatically per part:
- outline=True    1px dark ink ring (major body parts: head, torso, limbs).
- outline="shade" ring drawn as a darker step of whatever is beneath (small details: pouches,
                  straps, folds) so they don't add black clutter; dark ink only over empty space.
- cast=(dx, dy)   contact/drop shadow: darkens already-painted layers under the part's shifted
                  silhouette (head on chest, arms on torso, torso on legs).
Darker steps come from Sprite.ramps (key -> one-step-darker key).
"""
from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

TRANSPARENT = {".", " "}
OUTLINE_KEY = "o"


Outline = bool | str  # True (ink), "shade" (darker step of underlying), False (none)


@dataclass(frozen=True)
class Part:
    rows: tuple[str, ...]
    outline: Outline = True
    cast: tuple[int, int] | None = None

    @property
    def size(self) -> tuple[int, int]:
        return len(self.rows[0]), len(self.rows)


def part(text: str, outline: Outline = True, cast: tuple[int, int] | None = None) -> Part:
    """Parse a dedented ASCII block into a Part; all rows must be the same width."""
    rows = [r for r in textwrap.dedent(text).splitlines() if r.strip()]
    widths = {len(r) for r in rows}
    if len(widths) != 1:
        detail = ", ".join(f"{i}:{len(r)}" for i, r in enumerate(rows))
        raise ValueError(f"ragged part rows ({detail})")
    return Part(tuple(rows), outline, cast)


def flip(p: Part) -> Part:
    cast = (-p.cast[0], p.cast[1]) if p.cast else None
    return Part(tuple(r[::-1] for r in p.rows), p.outline, cast)


def recolor(p: Part, mapping: dict[str, str]) -> Part:
    """Swap palette keys, e.g. to reuse a part with another material."""
    table = str.maketrans(mapping)
    return Part(tuple(r.translate(table) for r in p.rows), p.outline, p.cast)


def arc(size: tuple[int, int], cx: float, cy: float, r: float, a0: float, a1: float,
        bands: tuple[tuple[float, str], ...] = ((1.5, "X"), (3.0, "x"))) -> Part:
    """Canvas-sized smear Part: an arc band between angles a0..a1 (degrees, y-down).
    `bands` maps max distance inside the radius -> palette key (thinner bright edge first)."""
    w, h = size
    rows = []
    lo, hi = sorted((a0, a1))
    for y in range(h):
        row = []
        for x in range(w):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            ang = np.degrees(np.arctan2(dy, dx)) % 360
            inside = r - np.hypot(dx, dy)
            key = next((k for d, k in bands if 0 <= inside < d), ".")
            row.append(key if lo <= ang <= hi else ".")
        rows.append("".join(row))
    return Part(tuple(rows), outline=False)


@dataclass(frozen=True)
class Place:
    part: Part
    x: int
    y: int


@dataclass(frozen=True)
class Shadow:
    cx: float
    cy: float
    rx: float
    ry: float
    alpha: int = 90


@dataclass
class Frame:
    places: list[Place]
    shadow: Shadow | None = None
    duration_ms: int = 140


@dataclass
class Sprite:
    """A character: palette + named animations (lists of frames) on a fixed canvas."""
    name: str
    palette: dict[str, str]
    size: tuple[int, int]
    animations: dict[str, list[Frame]] = field(default_factory=dict)
    ramps: dict[str, str] = field(default_factory=dict)


def hex_rgba(h: str) -> tuple[int, int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255


def _mask(p: Part) -> np.ndarray:
    return np.array([[c not in TRANSPARENT for c in r] for r in p.rows], dtype=bool)


def _dilate4(m: np.ndarray) -> np.ndarray:
    d = m.copy()
    d[1:, :] |= m[:-1, :]
    d[:-1, :] |= m[1:, :]
    d[:, 1:] |= m[:, :-1]
    d[:, :-1] |= m[:, 1:]
    return d


def render(frame: Frame, sprite: Sprite) -> Image.Image:
    """Composite one frame into an RGBA image of sprite.size."""
    w, h = sprite.size
    keys = np.full((h, w), ".", dtype="<U1")
    for pl in frame.places:
        m = _mask(pl.part)
        grid = np.array([list(r) for r in pl.part.rows])
        if pl.part.cast:
            dx, dy = pl.part.cast
            shifted = np.zeros_like(keys, dtype=bool)
            _or_at(shifted, m, pl.x + dx, pl.y + dy)
            own = np.zeros_like(shifted)
            _or_at(own, _dilate4(np.pad(m, 1)), pl.x - 1, pl.y - 1)
            _darken(keys, shifted & ~own, sprite.ramps, keep_unknown=True)
        if pl.part.outline:
            ring_local = _dilate4(np.pad(m, 1)) & ~np.pad(m, 1)
            ring = np.zeros_like(keys, dtype=bool)
            _or_at(ring, ring_local, pl.x - 1, pl.y - 1)
            empty = np.isin(keys, list(TRANSPARENT))
            if pl.part.outline == "shade":
                _darken(keys, ring & ~empty, sprite.ramps, keep_unknown=False)
                keys[ring & empty] = OUTLINE_KEY
            else:
                keys[ring] = OUTLINE_KEY
        _stamp(keys, np.where(m, grid, "."), pl.x, pl.y)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if frame.shadow:
        img.alpha_composite(_shadow_layer(frame.shadow, (w, h)))
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = body.load()
    for y in range(h):
        for x in range(w):
            k = keys[y, x]
            if k in TRANSPARENT:
                continue
            if k not in sprite.palette:
                raise KeyError(f"{sprite.name}: palette has no key {k!r}")
            px[x, y] = hex_rgba(sprite.palette[k])
    img.alpha_composite(body)
    return img


def _or_at(dst: np.ndarray, src: np.ndarray, x: int, y: int) -> None:
    """OR a local bool mask into dst at offset (x, y), clipping to bounds."""
    h, w = src.shape
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x0 < x1 and y0 < y1:
        dst[y0:y1, x0:x1] |= src[y0 - y:y1 - y, x0 - x:x1 - x]


def _darken(keys: np.ndarray, region: np.ndarray, ramps: dict[str, str], keep_unknown: bool) -> None:
    """Step painted pixels in region one ramp darker; ink and empty pixels are left alone."""
    for yy, xx in zip(*np.nonzero(region)):
        k = keys[yy, xx]
        if k in TRANSPARENT or k == OUTLINE_KEY:
            continue
        keys[yy, xx] = ramps.get(k, k if keep_unknown else OUTLINE_KEY)


def _stamp(dst: np.ndarray, src: np.ndarray, x: int, y: int) -> None:
    h, w = src.shape
    for sy in range(h):
        ty = y + sy
        if not 0 <= ty < dst.shape[0]:
            continue
        for sx in range(w):
            tx = x + sx
            if 0 <= tx < dst.shape[1] and src[sy, sx] not in TRANSPARENT:
                dst[ty, tx] = src[sy, sx]


def _shadow_layer(s: Shadow, size: tuple[int, int]) -> Image.Image:
    """Hard-edged pixel ellipse (no anti-aliasing) for the ground shadow."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    px = layer.load()
    for y in range(size[1]):
        for x in range(size[0]):
            if ((x + 0.5 - s.cx) / s.rx) ** 2 + ((y + 0.5 - s.cy) / s.ry) ** 2 <= 1:
                px[x, y] = (24, 16, 28, s.alpha)
    return layer


def upscale(img: Image.Image, s: int) -> Image.Image:
    return img.resize((img.width * s, img.height * s), Image.NEAREST)


def on_bg(img: Image.Image, color: str) -> Image.Image:
    bg = Image.new("RGBA", img.size, hex_rgba(color))
    bg.alpha_composite(img)
    return bg


def export(sprite: Sprite, out_dir: Path, scale: int = 6, bg: str = "#c8b98c") -> None:
    """Write a 1x sheet, an upscaled labelled sheet, and one GIF per animation."""
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = sprite.size
    rows = list(sprite.animations.items())
    cols = max(len(f) for _, f in rows)
    sheet = Image.new("RGBA", (cols * w, len(rows) * h), (0, 0, 0, 0))
    for r, (_, frames) in enumerate(rows):
        for c, fr in enumerate(frames):
            sheet.alpha_composite(render(fr, sprite), (c * w, r * h))
    sheet.save(out_dir / f"{sprite.name}_sheet_1x.png")

    big = upscale(on_bg(sheet, bg), scale)
    label_w = 90
    labelled = Image.new("RGBA", (big.width + label_w, big.height), hex_rgba("#1d1a22"))
    labelled.alpha_composite(big, (label_w, 0))
    d = ImageDraw.Draw(labelled)
    for r, (name, _) in enumerate(rows):
        d.text((6, r * h * scale + 6), name, fill=(240, 230, 210, 255))
    labelled.save(out_dir / f"{sprite.name}_sheet_x{scale}.png")

    for name, frames in rows:
        imgs = [upscale(on_bg(render(f, sprite), bg), scale).convert("RGB") for f in frames]
        imgs[0].save(out_dir / f"{sprite.name}_{name}.gif", save_all=True, append_images=imgs[1:],
                     duration=[f.duration_ms for f in frames], loop=0, disposal=2)
