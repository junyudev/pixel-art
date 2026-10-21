"""Crop a native-res image and upscale with nearest-neighbor, drawing a faint 8px grid for counting.
Usage: zoom.py SRC OUT x0 y0 x1 y1 [scale=10]"""
import sys
from PIL import Image, ImageDraw

if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
    sys.exit(__doc__)
src, out, *rest = sys.argv[1:]
x0, y0, x1, y1 = map(int, rest[:4])
s = int(rest[4]) if len(rest) > 4 else 10
img = Image.open(src).convert("RGB").crop((x0, y0, x1, y1))
big = img.resize((img.width * s, img.height * s), Image.NEAREST)
d = ImageDraw.Draw(big)
for gx in range(0, img.width + 1, 8):
    d.line([(gx * s, 0), (gx * s, big.height)], fill=(255, 0, 255), width=1)
for gy in range(0, img.height + 1, 8):
    d.line([(0, gy * s), (big.width, gy * s)], fill=(255, 0, 255), width=1)
big.save(out)
