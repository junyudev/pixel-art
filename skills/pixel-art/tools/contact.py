"""Contact sheet for picking a concept by how its converted sprite reads at game size.
Top row: real reference sprites then the candidates (labelled A, B, C...) at 3x; bottom row: the same at 1x.
Optionally pastes every candidate into a native-resolution game screenshot crop (--scene PNG x0 y0 x1 y1).
Give the sheet (only the image) to a fresh-eyes reviewer, or use it yourself.
Usage: python -I tools/contact.py OUT.png --sprites A.png B.png ... [--ref-files R.png ...]
       [--atlas ATLAS.png ATLAS.json --refs NAME ...] [--scene NATIVE.png x0 y0 x1 y1]"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

GROUND, DARK, TEXT = (0xCD, 0xB9, 0x8A, 255), (29, 26, 34, 255), (240, 230, 210, 255)


def trim(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    return img.crop(img.getchannel("A").getbbox())


def strip(items: list[tuple[str, Image.Image]], scale: int, label: bool) -> Image.Image:
    gap = 6 * scale if scale > 1 else 6
    tiles = []
    for name, im in items:
        bg = Image.new("RGBA", im.size, GROUND)
        bg.alpha_composite(im)
        tiles.append((name, bg.resize((im.width * scale, im.height * scale), Image.NEAREST)))
    top = 16 if label else 4
    h = max(t.height for _, t in tiles) + top + 4
    out = Image.new("RGBA", (sum(t.width + gap for _, t in tiles) + gap, h), DARK)
    d = ImageDraw.Draw(out)
    x = gap
    for name, t in tiles:
        out.alpha_composite(t, (x, h - 4 - t.height))
        if label:
            d.text((x, 2), name, fill=TEXT)
        x += t.width + gap
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--atlas", nargs=2)
    ap.add_argument("--refs", nargs="*", default=[])
    ap.add_argument("--ref-files", nargs="*", default=[])
    ap.add_argument("--sprites", nargs="+", required=True)
    ap.add_argument("--scene", nargs=5)
    a = ap.parse_args()
    refs = [(f"ref {Path(p).stem}", trim(Image.open(p))) for p in a.ref_files]
    if a.atlas and a.refs:
        atlas = Image.open(a.atlas[0]).convert("RGBA")
        frames = json.loads(Path(a.atlas[1]).read_text())["frames"]
        refs += [(f"ref {n}", atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"])))
                 for n in a.refs for f in [frames[n]["frame"]]]
    cands = [(chr(ord("A") + i), trim(Image.open(p))) for i, p in enumerate(a.sprites)]
    rows = [strip(refs + cands, 3, True), strip(refs + cands, 1, False)]
    if a.scene:
        crop = tuple(map(int, a.scene[1:]))
        scenes = []
        for name, im in cands:
            bg = Image.open(a.scene[0]).convert("RGBA").crop(crop)
            bg.alpha_composite(im, (8, bg.height - im.height - 4))
            scenes.append((name, bg))
        rows.append(strip(scenes, 3, True))
    sheet = Image.new("RGBA", (max(r.width for r in rows), sum(r.height + 6 for r in rows)), DARK)
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y))
        y += r.height + 6
    sheet.save(a.out)
    print("wrote", a.out, "candidates:", ", ".join(f"{n}={p}" for (n, _), p in zip(cands, a.sprites)))


if __name__ == "__main__":
    main()
