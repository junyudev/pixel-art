"""Reference crops (native px) above your sprites, all at the same pixel scale.
Usage: python -I tools/compare.py OUT.png --ref NATIVE.png x0 y0 x1 y1 [--ref ...] --ours A.png [B.png ...] [--scale 4]"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  # noqa: E402

from kit.pixelkit import on_bg, upscale  # noqa: E402

DARK = (29, 26, 34, 255)


def strip(images: list[Image.Image], gap: int = 4) -> Image.Image:
    h = max(i.height for i in images)
    out = Image.new("RGBA", (sum(i.width for i in images) + gap * (len(images) + 1), h + 2 * gap), DARK)
    x = gap
    for im in images:
        out.alpha_composite(im, (x, gap + h - im.height))
        x += im.width + gap
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--ref", nargs=5, action="append", default=[], metavar=("PNG", "X0", "Y0", "X1", "Y1"))
    ap.add_argument("--ours", nargs="+", required=True)
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--ground", default="#cdb98a")
    a = ap.parse_args()
    refs = [Image.open(p).convert("RGBA").crop(tuple(map(int, box))) for p, *box in a.ref]
    ours = [on_bg(Image.open(p).convert("RGBA"), a.ground) for p in a.ours]
    rows = [strip(r) for r in (refs, ours) if r]
    canvas = Image.new("RGBA", (max(r.width for r in rows), sum(r.height for r in rows)), DARK)
    y = 0
    for r in rows:
        canvas.alpha_composite(r, (0, y))
        y += r.height
    upscale(canvas, a.scale).save(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
