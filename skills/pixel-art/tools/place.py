"""Place a sprite on the delivery canvas: trim to the figure, center horizontally, feet on the bottom row.
Fails (exit 1) if the figure does not fit — regenerate the concept smaller instead of shrinking pixels.
Usage: python -I tools/place.py SPRITE_native.png W H OUT.png"""
import sys

from PIL import Image


def main() -> None:
    src, w, h, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    sprite = Image.open(src).convert("RGBA")
    sprite = sprite.crop(sprite.getchannel("A").getbbox())
    if sprite.width > w or sprite.height > h:
        sys.exit(f"figure {sprite.width}x{sprite.height} does not fit {w}x{h}: regenerate the concept smaller")
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.alpha_composite(sprite, ((w - sprite.width) // 2, h - sprite.height))
    canvas.save(out)
    print(f"placed {sprite.width}x{sprite.height} figure on {w}x{h} -> {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
