"""Inspection sheet for one sprite: the views a pixel artist flips between while drawing.
1x on ground, 3x, 8x with a labelled coordinate grid (for precise edits), silhouette,
squint (blurred values), grayscale, and horizontal flip."""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from kit.pixelkit import hex_rgba, on_bg, upscale

BG = "#c8b98c"


def grid_view(img: Image.Image, s: int = 8, step: int = 4) -> Image.Image:
    big = upscale(on_bg(img, BG), s)
    pad = 18
    out = Image.new("RGBA", (big.width + pad, big.height + pad), (29, 26, 34, 255))
    out.alpha_composite(big, (pad, pad))
    d = ImageDraw.Draw(out)
    for x in range(0, img.width + 1, step):
        d.line([(pad + x * s, pad), (pad + x * s, out.height)], fill=(255, 0, 255, 90 if x % 8 else 170))
        if x < img.width:
            d.text((pad + x * s + 1, 3), str(x), fill=(240, 230, 210, 255))
    for y in range(0, img.height + 1, step):
        d.line([(pad, pad + y * s), (out.width, pad + y * s)], fill=(255, 0, 255, 90 if y % 8 else 170))
        if y < img.height:
            d.text((1, pad + y * s + 1), str(y), fill=(240, 230, 210, 255))
    return out


def sheet(img: Image.Image) -> Image.Image:
    alpha = img.getchannel("A").point(lambda a: 255 if a > 200 else 0)
    sil = Image.new("RGBA", img.size, hex_rgba(BG))
    sil.paste((30, 22, 34, 255), mask=alpha)
    ground = on_bg(img, BG)
    squint = ground.resize((img.width // 2, img.height // 2), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.8))
    squint = squint.resize(img.size, Image.BILINEAR)
    gray = ImageOps.grayscale(ground.convert("RGB")).convert("RGBA")
    flipped = ImageOps.mirror(ground)
    small = [ground, sil, squint, gray, flipped]
    s = 4
    tiles = [upscale(t, s) for t in small]
    g = grid_view(img)
    w = max(g.width, sum(t.width for t in tiles) + 4 * (len(tiles) - 1))
    out = Image.new("RGBA", (w + g.width + 8, max(g.height, tiles[0].height + img.height * 3 + 8)), (29, 26, 34, 255))
    out.alpha_composite(g, (0, 0))
    x = g.width + 8
    out.alpha_composite(on_bg(img, BG), (x, 0))
    out.alpha_composite(upscale(on_bg(img, BG), 3), (x + img.width + 8, 0))
    y = img.height * 3 + 8
    for t in tiles:
        out.alpha_composite(t, (x, y))
        x += t.width + 4
    return out.crop(out.getbbox())
