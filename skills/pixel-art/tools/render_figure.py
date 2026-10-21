"""Render a construct Figure module and print the numbers you need to critique it.
Writes NAME_1x.png (transparent), NAME_x6.png (on ground), NAME_views.png (grid + silhouette/squint/
gray/flip), NAME_light.png (N·L | tone bands), NAME_head.png (12x grid crop of the top third).
Usage: python -I tools/render_figure.py path/to/figure_module.py OUT_DIR [NAME] [--window x y w h] [--budget N]
  --window prints that area of the final sprite as ASCII (with a ruler) to write a ("block", ...) op.
The module must define figure() -> kit.construct.Figure."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from kit.construct import build, to_image  # noqa: E402
from kit.pixelkit import on_bg, upscale  # noqa: E402
from kit.views import BG, grid_view, sheet  # noqa: E402
from style_stats import fingerprint  # noqa: E402

# Guardrails = p10..p90 of clean Eastward sprites (styles/eastward.md), split by size: 34 small (h < 44,
# kids) and 186 adults. Outside = warn; inside does not mean good.
GUARD = {
    "small": {"dark": (0.18, 0.31), "speckle": (0.05, 0.07), "cluster": (4.3, 6.5), "edge_ink": (0.58, 0.96),
              "straight": (0.05, 0.27), "w": (17, 28), "head_w": (0.0, 0.92), "checker": (0.0, 0.015),
              "flat_h": (0.0, 0.32)},
    "adult": {"dark": (0.17, 0.32), "speckle": (0.03, 0.08), "cluster": (5.1, 7.8), "edge_ink": (0.72, 0.99),
              "straight": (0.09, 0.32), "w": (23, 46), "shoulder_w": (0.56, 1.0), "feet_w": (0.0, 0.55),
              "checker": (0.0, 0.015), "flat_h": (0.0, 0.33)},
}
WHY = {
    ("speckle", "hi"): "too many single pixels: merge them into shapes",
    ("speckle", "lo"): "almost no small marks: faces, hands and clothes probably lack drawn detail",
    ("cluster", "hi"): "masses too flat and empty (blown-up icon look): draw features, folds, stains",
    ("cluster", "lo"): "masses broken up into noise: use bigger flat shadow shapes",
    ("dark", "hi"): "too much ink/deep tone: drop lines around small details",
    ("dark", "lo"): "too little ink: outline the silhouette and draw features in ink",
    ("edge_ink", "hi"): "uniform black ring around everything: let lit top edges take the material's deep tone",
    ("edge_ink", "lo"): "silhouette barely inked: it will dissolve into backgrounds",
    ("straight", "hi"): "ruler-drawn slabs: break long straight contours with folds, notches, clumps and tapers",
    ("straight", "lo"): "contour is all jaggies: some straight runs (hems, boot soles) help it read",
    ("w", "hi"): "wider than most references of this size: slim the torso, head or props",
    ("w", "lo"): "narrower than most references of this size",
    ("head_w", "hi"): "the head is the widest part: shrink it or widen the shoulders/arms band",
    ("shoulder_w", "lo"): "still narrow at 40% height: the head/neck is too tall, shoulders start too low",
    ("flat_h", "hi"): "front-view thinking: hems, belts, cuffs, collars and bands are flat lines; seen from in front "
                      "and above they are arcs sagging toward the viewer (arc_pts / band)",
    ("flat_h", "lo"): "",
    ("checker", "hi"): "checkerboard/woven texture (rope, beard, trousers): make each texture one or two shapes",
    ("checker", "lo"): "",
    ("feet_w", "hi"): "barrel figure: seen from slightly above, legs taper to small feet close together",
}


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(mod)
    return mod


def print_window(keys: np.ndarray, x: int, y: int, w: int, h: int) -> None:
    print("     " + "".join(str((x + i) // 10 % 10) for i in range(w)))
    print("     " + "".join(str((x + i) % 10) for i in range(w)))
    for j in range(h):
        if 0 <= y + j < keys.shape[0]:
            print(f"{y + j:3d}  " + "".join(keys[y + j, x:x + w]))


def main() -> None:
    args = sys.argv[1:]
    window = budget = None
    if "--window" in args:
        i = args.index("--window")
        window = tuple(map(int, args[i + 1:i + 5]))
        del args[i:i + 5]
    if "--budget" in args:
        i = args.index("--budget")
        budget = int(args[i + 1])
        del args[i:i + 2]
    src, out = Path(args[0]), Path(args[1])
    name = args[2] if len(args) > 2 else src.stem
    out.mkdir(parents=True, exist_ok=True)
    fig = load(src).figure()
    b = build(fig)
    img = to_image(fig, b.keys)
    img.save(out / f"{name}_1x.png")
    upscale(on_bg(img, BG), 6).save(out / f"{name}_x6.png")
    sheet(img).save(out / f"{name}_views.png")

    ndl = np.clip((b.ndl + 1) / 2 * 255, 0, 255).astype(np.uint8)
    ndl[b.owner < 0] = 0
    tone = np.select([b.tone == k for k in range(4)], [230, 160, 90, 40], 0).astype(np.uint8)
    upscale(Image.fromarray(np.concatenate([ndl, tone], axis=1)), 6).save(out / f"{name}_light.png")

    painted = b.keys != "."
    ys, xs = np.nonzero(painted)
    top, bottom, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    grid_view(img.crop((max(left - 2, 0), max(top - 2, 0), right + 3, top + (bottom - top) // 3 + 3)),
              s=12, step=2).save(out / f"{name}_head.png")

    body = img.copy()
    body.putalpha(body.getchannel("A").point(lambda a: 255 if a == 255 else 0))
    fp = fingerprint(body)
    used = len(set(b.keys[painted]))
    print(f"bbox: x {left}..{right} y {top}..{bottom}  -> {right - left + 1}w x {bottom - top + 1}h (incl. ink)")
    print(f"colors used: {used}" + (f" (budget {budget}){'  <-- OVER' if used > budget else ''}" if budget else ""))
    print("fingerprint: " + "  ".join(f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}" for k, v in fp.items()))
    size = "small" if fp["h"] < 44 else "adult"
    print(f"guardrails: {size} sprites (h {'<' if size == 'small' else '>='} 44)")
    for k, (lo, hi) in GUARD[size].items():
        if fp[k] < lo:
            print(f"WARN {k}={fp[k]:.2f} < {lo}: {WHY[(k, 'lo')]}")
        elif fp[k] > hi:
            print(f"WARN {k}={fp[k]:.2f} > {hi}: {WHY[(k, 'hi')]}")
    print("region          px   bbox(x0,y0,x1,y1)     mean N·L   hi/base/shade/deep")
    for i, r in enumerate(fig.regions):
        m = b.owner == i
        if not m.any():
            print(f"{r.name:14s}   0   (fully hidden)")
            continue
        ry, rx = np.nonzero(m)
        t = b.tone[m]
        bands = "/".join(f"{(t == k).mean():.0%}" for k in range(4))
        print(f"{r.name:14s} {m.sum():3d}   ({rx.min()},{ry.min()},{rx.max()},{ry.max()})".ljust(40)
              + f"{b.ndl[m].mean():5.2f}     {bands}")
    if window:
        print_window(b.keys, *window)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
