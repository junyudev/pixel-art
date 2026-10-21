"""Style fingerprint of pixel sprites: the numbers that separate hand-drawn sprites from ours.
Inputs: PNG files, folders of PNGs, or a TexturePacker-style atlas (`atlas.png:atlas.json`).
Only fully opaque pixels count (ground shadows are usually translucent).

Metrics per sprite:
  h, w        opaque bbox                 colors      distinct opaque colors
  dark        share with value < 0.25     edge_ink    share of silhouette-edge pixels that are dark
  inner_dark  dark pixels not on the silhouette edge, as share of opaque pixels
  speckle     share of pixels whose color differs from all 4 neighbours (isolated pixels)
  cluster     mean size of 4-connected same-color clusters (bigger = broader masses)
  tones       mean distinct values (rounded) per hue family — how many steps each material uses
  straight    share of silhouette-edge pixels lying in straight runs >= 5 px (high = ruler-drawn slabs)
  flat_h      share of interior horizontal color boundaries lying in straight runs >= 6 px. Seen from in front and
              above, belts, hems, cuffs and collars are arcs; front-view thinking draws them as flat lines (refs median 0.28)
  checker     share of 2x2 blocks forming a checkerboard of two colors (dithered/woven textures; refs p90 0.015)
  head_w / shoulder_w / feet_w   silhouette width at 20 % / 40 % / 95 % of the height, divided by the max width.
              Seen from slightly above, real sprites are widest around the shoulders-to-hands band and narrow to
              small feet (adult feet_w median 0.43); barrel figures keep their width down to big boots.

Usage: python -I tools/style_stats.py [--each] SRC [SRC ...]"""
import colorsys
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def load(src: str) -> list[tuple[str, Image.Image]]:
    if ":" in src and src.split(":")[1].endswith(".json"):
        png, js = src.split(":")
        atlas = Image.open(png).convert("RGBA")
        frames = json.loads(Path(js).read_text())["frames"]
        return [(k, atlas.crop((f["frame"]["x"], f["frame"]["y"], f["frame"]["x"] + f["frame"]["w"],
                                f["frame"]["y"] + f["frame"]["h"]))) for k, f in frames.items()]
    p = Path(src)
    files = sorted(p.glob("*.png")) if p.is_dir() else [p]
    return [(f.stem, Image.open(f).convert("RGBA")) for f in files]


def fingerprint(img: Image.Image) -> dict[str, float]:
    a = np.asarray(img).astype(int)
    opaque = a[..., 3] == 255
    ys, xs = np.nonzero(opaque)
    rgb = a[..., :3]
    value = rgb.max(axis=2) / 255
    dark = (value < 0.25) & opaque
    edge = opaque & ~ndimage.binary_erosion(opaque, structure=ndimage.generate_binary_structure(2, 1))
    code = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    code = np.where(opaque, code, -1)
    pad = np.pad(code, 1, constant_values=-2)
    same = np.zeros(code.shape, dtype=bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        same |= pad[1 + dy:1 + dy + code.shape[0], 1 + dx:1 + dx + code.shape[1]] == code
    speckle = opaque & ~same
    sizes = []
    for c in np.unique(code[opaque]):
        labels, n = ndimage.label(code == c)
        sizes.extend(np.bincount(labels.ravel())[1:])
    hsv = np.array([colorsys.rgb_to_hsv(*(rgb[y, x] / 255)) for y, x in zip(ys, xs)])
    families = {}
    for h, s, v in hsv:
        if v < 0.25:
            continue  # ink
        fam = "gray" if s < 0.15 else int(h * 12) % 12
        families.setdefault(fam, set()).add(round(v * 10))
    runs_total = runs_straight = 0
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        side = opaque & ~np.pad(opaque, 1)[1 + dy:1 + dy + opaque.shape[0], 1 + dx:1 + dx + opaque.shape[1]]
        for line in (side if dy else side.T):
            for run in "".join("1" if v else "0" for v in line).split("0"):
                runs_total += len(run)
                runs_straight += len(run) if len(run) >= 5 else 0
    top, height = ys.min(), ys.max() - ys.min() + 1
    widths = []
    for frac in (0.2, 0.4, 0.95):
        row = np.nonzero(opaque[top + int(frac * (height - 1))])[0]
        widths.append(row.max() - row.min() + 1 if len(row) else 0)
    max_w = max(np.ptp(np.nonzero(r)[0]) + 1 for r in opaque if r.any())
    hb = opaque[:-1] & opaque[1:] & (code[:-1] != code[1:])
    hb_flat = sum(len(r) for line in hb for r in "".join("1" if v else "0" for v in line).split("0") if len(r) >= 6)
    p00, p01, p10, p11 = code[:-1, :-1], code[:-1, 1:], code[1:, :-1], code[1:, 1:]
    quad = (p00 >= 0) & (p01 >= 0) & (p10 >= 0) & (p11 >= 0)
    checker = (quad & (p00 == p11) & (p01 == p10) & (p00 != p01)).sum() / max(1, quad.sum())
    return {
        "h": ys.max() - ys.min() + 1, "w": xs.max() - xs.min() + 1,
        "colors": len(np.unique(code[opaque])),
        "dark": dark.sum() / opaque.sum(),
        "edge_ink": (edge & dark).sum() / edge.sum(),
        "inner_dark": (dark & ~edge).sum() / opaque.sum(),
        "speckle": speckle.sum() / opaque.sum(),
        "cluster": float(np.mean(sizes)),
        "tones": float(np.mean([len(v) for v in families.values()])) if families else 0.0,
        "straight": runs_straight / runs_total,
        "checker": float(checker),
        "flat_h": hb_flat / max(1, int(hb.sum())),
        "head_w": widths[0] / max_w, "shoulder_w": widths[1] / max_w, "feet_w": widths[2] / max_w,
    }


COLS = ["h", "w", "colors", "dark", "edge_ink", "inner_dark", "speckle", "cluster", "tones", "straight", "checker", "flat_h",
        "head_w", "shoulder_w", "feet_w"]


def fmt(d: dict) -> str:
    return "  ".join(f"{k}={d[k]:.0f}" if k in ("h", "w", "colors") else f"{k}={d[k]:.2f}" for k in COLS)


def main() -> None:
    args = sys.argv[1:]
    each = "--each" in args
    rows = []
    for src in [a for a in args if a != "--each"]:
        for name, img in load(src):
            if (np.asarray(img)[..., 3] == 255).sum() < 20:
                continue
            fp = fingerprint(img)
            rows.append(fp)
            if each:
                print(f"{name[:22]:22s} {fmt(fp)}")
    if len(rows) > 1:
        print(f"n={len(rows)}  p10 / median / p90")
        for k in COLS:
            v = np.array([r[k] for r in rows], dtype=float)
            print(f"  {k:10s} {np.percentile(v, 10):7.2f} {np.median(v):7.2f} {np.percentile(v, 90):7.2f}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
