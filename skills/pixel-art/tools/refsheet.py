"""Style reference sheet for image generation: real sprites on a flat ground, side by side, enlarged --scale
S times (default 8). Use S = the block size B asked of the concept, so the model sees the target pixel size.
Usage: python -I tools/refsheet.py ATLAS.png ATLAS.json OUT.png NAME [NAME ...] [--scale S]
       python -I tools/refsheet.py --files OUT.png SPRITE.png [SPRITE.png ...] [--scale S]"""
import json
import sys
from pathlib import Path

from PIL import Image

GROUND, GAP = "#cdb98a", 6


def main() -> None:
    args = sys.argv[1:]
    scale = 8
    if "--scale" in args:
        i = args.index("--scale")
        scale = int(args[i + 1])
        del args[i:i + 2]
    if args[0] == "--files":
        out, *files = args[1:]
        sprites = [Image.open(p).convert("RGBA") for p in files]
        sprites = [s.crop(s.getchannel("A").getbbox()) for s in sprites]
    else:
        atlas_png, atlas_json, out, *names = args
        atlas = Image.open(atlas_png).convert("RGBA")
        frames = json.loads(Path(atlas_json).read_text())["frames"]
        sprites = [atlas.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
                   for f in (frames[n]["frame"] for n in names)]
    w = sum(s.width for s in sprites) + GAP * (len(sprites) + 1)
    h = max(s.height for s in sprites) + GAP * 2
    sheet = Image.new("RGBA", (w, h), GROUND)
    x = GAP
    for s in sprites:
        sheet.alpha_composite(s, (x, h - GAP - s.height))
        x += s.width + GAP
    sheet.resize((w * scale, h * scale), Image.NEAREST).convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
