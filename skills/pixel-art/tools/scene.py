"""Paste sprites into a real native-resolution screenshot crop: the most honest fit test.
Usage: python -I tools/scene.py NATIVE.png x0 y0 x1 y1 OUT.png --put SPRITE.png X Y [--put ...] [--scale 5]
X/Y are in crop coordinates (top-left of the sprite canvas)."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  # noqa: E402

from kit.pixelkit import upscale  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("native")
    ap.add_argument("box", nargs=4, type=int)
    ap.add_argument("out")
    ap.add_argument("--put", nargs=3, action="append", required=True, metavar=("PNG", "X", "Y"))
    ap.add_argument("--scale", type=int, default=5)
    a = ap.parse_args()
    bg = Image.open(a.native).convert("RGBA").crop(tuple(a.box))
    for png, x, y in a.put:
        bg.alpha_composite(Image.open(png).convert("RGBA"), (int(x), int(y)))
    upscale(bg, a.scale).save(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
