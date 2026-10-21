"""Fidelity of a converted sprite to its concept: paint every sprite cell back over its own concept region
(elastic grid from elastic2px) and take the mean RGB abs error over the figure. Lower = more faithful;
a fresh elastic2px conversion typically scores ~8-12. Hand fixes must not raise it.
Usage: python -I tools/fidelity.py CONCEPT.png SPRITE_native.png GRID.json"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def grid_error(concept: Image.Image, sprite: Image.Image, grid: dict) -> float:
    xs, ys, (cx, cy, _, _) = grid["xs"], grid["ys"], grid["crop"]
    ref = np.asarray(concept.convert("RGB")).astype(int)
    cells = np.asarray(sprite.convert("RGBA")).astype(int)
    total, count = 0.0, 0
    for v in range(cells.shape[0]):
        for u in range(cells.shape[1]):
            i, j = u + cx, v + cy
            if cells[v, u, 3] != 255 or not (0 <= i < len(xs) - 1 and 0 <= j < len(ys) - 1):
                continue
            block = ref[ys[j]:ys[j + 1], xs[i]:xs[i + 1]]
            total += np.abs(block - cells[v, u, :3]).mean(axis=2).sum()
            count += block.shape[0] * block.shape[1]
    return total / max(count, 1)


def main() -> None:
    concept, sprite, grid = sys.argv[1:4]
    print(f"error vs concept: {grid_error(Image.open(concept), Image.open(sprite), json.loads(Path(grid).read_text())):.1f}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
