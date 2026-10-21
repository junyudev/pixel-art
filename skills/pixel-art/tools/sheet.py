"""Critique sheet: your sprite(s) beside real references, the way a judge will see them. View it every loop.
Rows: (1) full sprites at 4x, (2) heads (top 42% of each figure) at 8x, (3) everything at 1x shown 2x (game size).
Pass several --ours to compare variants of the same sprite (pick the one that reads best at 1x).
Usage: python -I tools/sheet.py OUT.png --ours A.png [B.png ...] [--refs PNG ...]
                                [--atlas ATLAS.png ATLAS.json --names "Helen" "Mrs. Sun" ...]"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

GROUND, DARK, TEXT = (205, 185, 138, 255), (29, 26, 34, 255), (240, 230, 210, 255)


def bbox_crop(img: Image.Image) -> Image.Image:
    box = img.getchannel("A").point(lambda a: 255 if a == 255 else 0).getbbox()
    return img.crop(box) if box else img


def on_ground(img: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", img.size, GROUND)
    bg.alpha_composite(img)
    return bg


def labelled(img: Image.Image, scale: int, label: str) -> Image.Image:
    big = on_ground(img).resize((img.width * scale, img.height * scale), Image.NEAREST)
    out = Image.new("RGBA", (max(big.width, 60), big.height + 13), DARK)
    out.alpha_composite(big, (0, 13))
    ImageDraw.Draw(out).text((1, 0), label[:14], fill=TEXT)
    return out


def row(tiles: list[Image.Image], gap: int = 8) -> Image.Image:
    h = max(t.height for t in tiles)
    out = Image.new("RGBA", (sum(t.width + gap for t in tiles) + gap, h + gap), DARK)
    x = gap
    for t in tiles:
        out.alpha_composite(t, (x, h - t.height))
        x += t.width + gap
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--ours", nargs="+", required=True)
    ap.add_argument("--refs", nargs="*", default=[])
    ap.add_argument("--atlas", nargs=2, metavar=("PNG", "JSON"))
    ap.add_argument("--names", nargs="*", default=[])
    a = ap.parse_args()
    items = [(f"{chr(65 + i)} {Path(p).stem}", Image.open(p).convert("RGBA")) for i, p in enumerate(a.ours)]
    items += [("ref " + Path(p).stem, Image.open(p).convert("RGBA")) for p in a.refs]
    if a.atlas and a.names:
        atlas = Image.open(a.atlas[0]).convert("RGBA")
        frames = json.loads(Path(a.atlas[1]).read_text())["frames"]
        for n in a.names:
            f = frames[n]["frame"]
            items.append(("ref " + n, atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))))
    figs = [(name, bbox_crop(img)) for name, img in items]
    heads = [(name, fig.crop((0, 0, fig.width, max(1, round(fig.height * 0.42))))) for name, fig in figs]
    rows = [row([labelled(f, 4, n) for n, f in figs]),
            row([labelled(h, 8, n) for n, h in heads]),
            row([labelled(f, 2, n) for n, f in figs])]
    sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height for r in rows)), DARK)
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y))
        y += r.height
    sheet.save(a.out)
    print("wrote", a.out, sheet.size)


if __name__ == "__main__":
    main()
