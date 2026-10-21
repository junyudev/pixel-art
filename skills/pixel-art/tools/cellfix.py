"""Fix individual sprite cells toward the concept (the only kind of hand edit this route allows).
Each EDIT is one of:
  x,y        cell takes the concept's main color in that cell     x,y:2   its second color
  x,y=#hex   cell takes an explicit color (prefer existing sprite colors)   x,y=.   cell becomes transparent
Concept colors snap to the nearest color already in the sprite, so the palette does not grow.
Prints fidelity before/after; an edit that raises the error is fine only for a clear conversion artifact.
Usage: python -I tools/cellfix.py CONCEPT.png SPRITE_native.png GRID.json EDIT [EDIT ...]"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import cell_colors  # noqa: E402
from fidelity import grid_error  # noqa: E402


def main() -> None:
    concept_p, sprite_p, grid_p, *edits = sys.argv[1:]
    grid = json.loads(Path(grid_p).read_text())
    xs, ys, (cx, cy, _, _) = grid["xs"], grid["ys"], grid["crop"]
    concept = Image.open(concept_p)
    ref = np.asarray(concept.convert("RGB")).astype(int)
    before = grid_error(concept, Image.open(sprite_p), grid)
    spr = np.asarray(Image.open(sprite_p).convert("RGBA")).copy()
    palette = np.unique(spr[spr[..., 3] == 255][:, :3], axis=0).astype(int)
    for edit in edits:
        pos, _, val = edit.partition("=")
        xy, _, rank = pos.partition(":")
        u, v = map(int, xy.split(","))
        if val == ".":
            spr[v, u] = 0
            continue
        if val:
            color = np.array([int(val[i:i + 2], 16) for i in (1, 3, 5)])
        else:
            block = ref[ys[v + cy]:ys[v + cy + 1], xs[u + cx]:xs[u + cx + 1]]
            color = np.array(cell_colors(block)[int(rank or 1) - 1][0])
            color = palette[np.argmin(np.linalg.norm(palette - color, axis=1))]
        spr[v, u, :3], spr[v, u, 3] = color, 255
    Image.fromarray(spr).save(sprite_p)
    after = grid_error(concept, Image.open(sprite_p), grid)
    print(f"{len(edits)} cells edited; error vs concept {before:.2f} -> {after:.2f}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
