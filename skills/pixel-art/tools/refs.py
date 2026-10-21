"""Study real sprites as text: the same medium you draw in.
  extract ATLAS.png ATLAS.json NAME OUT.png   cut one named frame out of a TexturePacker-style atlas
  text    PNG [x y w h] [--map PALETTE.json]  print the sprite (or a window) as ASCII with a ruler + palette
Darkest color prints as 'o' (ink), transparent as '.'; other colors get letters, listed with hex values.
--map gives a style's shared colors fixed letters (e.g. styles/eastward_palette.json), so the same color reads
as the same letter in every sprite; colors outside the map print as digits.
Usage: python -I tools/refs.py extract|text ..."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

KEYS = "ABCDEFGHIJKLMNPQRSTUVWXYZabcdefghijklmnpqrstuvwxyz0123456789"


def as_text(path: str, shared: dict[str, str] | None = None) -> tuple[np.ndarray, dict[str, str]]:
    """shared: hex -> fixed letter; other colors get digits/letters in value order (darkest = 'o' if unmapped)."""
    a = np.asarray(Image.open(path).convert("RGBA")).astype(int)
    opaque = a[..., 3] == 255
    colors = sorted({tuple(int(v) for v in c) for c in a[opaque][:, :3]}, key=sum)
    if shared:
        free = iter("0123456789" + KEYS.lower())
        keys = {c: shared.get("#%02x%02x%02x" % c) or next(free) for c in colors}
    else:
        keys = {c: ("o" if i == 0 else KEYS[i - 1]) for i, c in enumerate(colors)}
    grid = np.full(opaque.shape, ".", dtype="<U1")
    for y, x in zip(*np.nonzero(opaque)):
        grid[y, x] = keys[tuple(int(v) for v in a[y, x, :3])]
    return grid, {k: "#%02x%02x%02x" % c for c, k in keys.items()}


def main() -> None:
    cmd, *args = sys.argv[1:]
    if cmd == "extract":
        f = json.loads(Path(args[1]).read_text())["frames"][args[2]]["frame"]
        Image.open(args[0]).crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"])).save(args[3])
        return
    if cmd != "text":
        sys.exit(__doc__)
    shared = None
    if "--map" in args:
        i = args.index("--map")
        spec = json.loads(Path(args[i + 1]).read_text())
        shared = {hx: k for k, v in spec.items() if not k.startswith("_") for hx in v[0]}
        del args[i:i + 2]
    grid, pal = as_text(args[0], shared)
    x, y, w, h = map(int, args[1:5]) if len(args) >= 5 else (0, 0, grid.shape[1], grid.shape[0])
    print("palette: " + "  ".join(f"{k}={v}" for k, v in pal.items()))
    print("     " + "".join(str((x + i) // 10 % 10) for i in range(w)))
    print("     " + "".join(str((x + i) % 10) for i in range(w)))
    for j in range(h):
        if 0 <= y + j < grid.shape[0]:
            print(f"{y + j:3d}  " + "".join(grid[y + j, x:x + w]))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
