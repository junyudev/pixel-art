"""Cell-by-cell comparison of a converted sprite with its concept, to find conversion artifacts.
Writes OUT.png: [concept, rectified so each uneven cell is one tile] [sprite cells] [per-cell error heatmap],
labelled in sprite coordinates, and prints the worst cells with the concept's two main colors per cell.
Usage: python -I tools/check.py CONCEPT.png SPRITE_native.png GRID.json OUT.png [x0 y0 x1 y1] [--top N]
(box in sprite coordinates; default = whole sprite)"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

LINE, TEXT, S = (255, 0, 255, 100), (255, 255, 255, 255), 24


def cell_colors(block: np.ndarray) -> list[tuple[tuple[int, int, int], float]]:
    px = block.reshape(-1, 3)
    keys = (px // 24) @ np.array([10_000, 100, 1])
    vals, counts = np.unique(keys, return_counts=True)
    order = np.argsort(-counts)[:2]
    return [(tuple(int(c) for c in px[keys == vals[k]].mean(0)), counts[k] / len(px)) for k in order]


def hexc(c) -> str:
    return "#%02x%02x%02x" % tuple(int(v) for v in c)


def main() -> None:
    args = sys.argv[1:]
    top = 20
    if "--top" in args:
        i = args.index("--top")
        top = int(args[i + 1])
        del args[i:i + 2]
    concept_p, sprite_p, grid_p, out_p, *box = args
    g = json.loads(Path(grid_p).read_text())
    xs, ys, (cx, cy, _, _) = g["xs"], g["ys"], g["crop"]
    ref = np.asarray(Image.open(concept_p).convert("RGB")).astype(int)
    spr = np.asarray(Image.open(sprite_p).convert("RGBA")).astype(int)
    h, w = spr.shape[:2]
    bx0, by0, bx1, by1 = map(int, box) if box else (0, 0, w, h)
    bx1, by1 = min(bx1, len(xs) - 1 - cx), min(by1, len(ys) - 1 - cy)

    rows = []
    heat = Image.new("RGBA", ((bx1 - bx0) * S, (by1 - by0) * S), (0, 0, 0, 255))
    dh = ImageDraw.Draw(heat)
    for v in range(by0, by1):
        for u in range(bx0, bx1):
            block = ref[ys[v + cy]:ys[v + cy + 1], xs[u + cx]:xs[u + cx + 1]]
            if spr[v, u, 3] == 255:
                err = float(np.abs(block - spr[v, u, :3]).mean())
                rows.append((err, u, v, hexc(spr[v, u, :3]), cell_colors(block)))
                level = int(min(255, err * 4))
                dh.rectangle([(u - bx0) * S, (v - by0) * S, (u - bx0 + 1) * S - 1, (v - by0 + 1) * S - 1],
                             fill=(level, level // 3, 0, 255))

    # rectified concept: every (uneven) concept cell is resized to one SxS tile, so both panels align cell for cell
    concept = Image.new("RGBA", heat.size, (0, 0, 0, 255))
    for v in range(by0, by1):
        for u in range(bx0, bx1):
            block = ref[ys[v + cy]:ys[v + cy + 1], xs[u + cx]:xs[u + cx + 1]].astype(np.uint8)
            tile = Image.fromarray(block).convert("RGBA").resize((S, S), Image.BILINEAR)
            concept.alpha_composite(tile, ((u - bx0) * S, (v - by0) * S))
    sprite = Image.fromarray(spr[by0:by1, bx0:bx1].astype(np.uint8))
    bg = Image.new("RGBA", sprite.size, (0xCD, 0xB9, 0x8A, 255))
    bg.alpha_composite(sprite)
    sprite = bg.resize(heat.size, Image.NEAREST)
    for panel in (concept, sprite):
        d = ImageDraw.Draw(panel)
        for u in range(bx0, bx1 + 1):
            d.line([((u - bx0) * S, 0), ((u - bx0) * S, panel.height)], fill=LINE)
            if u < bx1 and u % 2 == 0:
                d.text(((u - bx0) * S + 2, 1), str(u), fill=TEXT)
        for v in range(by0, by1 + 1):
            d.line([(0, (v - by0) * S), (panel.width, (v - by0) * S)], fill=LINE)
            if v < by1 and v % 2 == 0:
                d.text((1, (v - by0) * S + 11), str(v), fill=TEXT)
    sheet = Image.new("RGBA", (heat.width * 3 + 16, heat.height), (29, 26, 34, 255))
    for k, p in enumerate((concept, sprite, heat)):
        sheet.alpha_composite(p, (k * (heat.width + 8), 0))
    sheet.save(out_p)
    print(f"mean cell error in box: {np.mean([r[0] for r in rows]):.1f}  (worst {top} below)")
    for err, u, v, col, tops in sorted(rows, reverse=True)[:top]:
        alts = ", ".join(f"{hexc(c)} {f:.0%}" for c, f in tops)
        print(f"  ({u:2d},{v:2d}) err {err:5.1f}  sprite {col}  concept: {alts}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
