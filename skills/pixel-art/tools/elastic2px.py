"""Concept image -> true pixel sprite, faithful to the concept's own colors and 1-pixel features.
1. block size: typical run length of the concept's 1-pixel outline (or --pixel P image px per sprite px)
2. elastic grid: per axis, grid lines placed on edge-energy peaks by dynamic programming with spacing in
   [0.75P, 1.25P], so the grid follows the generator's uneven blocks instead of drifting
3. cell color: dominant color of each cell's interior (20% margin ignored)
4. background: cells close to the border color become transparent, also where the figure encloses them
   (largest figure component kept)
5. palette: merge near-duplicate colors (--merge T); then, only if over --max-colors K, merge the pair that adds
   the least squared error (Ward) until K. No snapping to other palettes, no despeckling (eyes and glints survive).
Writes PREFIX_native.png (figure crop with a 1px transparent border) and PREFIX_grid.json (for fidelity,
overlay, probe and cellfix). Prints figure size, colors and fidelity error vs the concept.
Usage: python -I tools/elastic2px.py CONCEPT.png PREFIX [--pixel P] [--merge 16] [--max-colors 16]"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fidelity import grid_error  # noqa: E402


def outline_period(g: np.ndarray) -> float:
    dark = g < 70
    runs = [len(r) for line in (*dark, *dark.T) for r in "".join("1" if v else "0" for v in line).split("0")
            if 4 <= len(r) <= 48]
    counts = np.convolve(np.bincount(runs), [1, 2, 3, 2, 1], mode="same")
    peak = int(np.argmax(counts))
    return float(np.mean([r for r in runs if abs(r - peak) <= 2]))


def elastic_lines(profile: np.ndarray, p: float) -> list[int]:
    """Boundary positions maximizing summed edge energy; each line costs the profile mean, so lines only pay
    off on real edges (otherwise the shortest allowed spacing always wins)."""
    profile = profile - profile.mean()
    n = len(profile)
    lo, hi = max(2, int(round(0.75 * p))), int(round(1.25 * p))
    score = np.full(n, -np.inf)
    prev = np.full(n, -1)
    score[: hi + 1] = profile[: hi + 1]
    for j in range(n):
        if not np.isfinite(score[j]):
            continue
        for d in range(lo, hi + 1):
            k = j + d
            if k >= n:
                break
            if score[j] + profile[k] > score[k]:
                score[k], prev[k] = score[j] + profile[k], j
    tail = score[max(0, n - 1 - hi):]
    end = max(0, n - 1 - hi) + int(np.argmax(tail))
    lines = [end]
    while prev[lines[-1]] >= 0:
        lines.append(int(prev[lines[-1]]))
    return sorted(lines)


def dominant(block: np.ndarray) -> np.ndarray:
    h, w = block.shape[:2]
    my, mx = max(1, int(h * 0.2)), max(1, int(w * 0.2))
    core = block[my:h - my, mx:w - mx].reshape(-1, 3)
    if len(core) == 0:
        core = block.reshape(-1, 3)
    keys = (core // 24).astype(int) @ np.array([10_000, 100, 1])
    vals, counts = np.unique(keys, return_counts=True)
    return core[keys == vals[np.argmax(counts)]].mean(axis=0)


def merge_colors(colors: np.ndarray, weights: np.ndarray, t: float, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Agglomerative merge with weighted-mean centers: first every pair closer than t (near-duplicates); then,
    while over the budget k, the pair whose merge adds the least squared error (Ward), so stray shades of a few
    cells go before two big distinct materials do (closest-pair merging pulled lit skin into rope tan)."""
    centers = colors.astype(float).copy()
    w = weights.astype(float).copy()
    labels = np.arange(len(colors))
    alive = np.ones(len(colors), dtype=bool)

    def cost_row(i: int, ward: bool) -> np.ndarray:
        if not alive[i]:
            return np.full(len(colors), np.inf)
        d2 = ((centers - centers[i]) ** 2).sum(axis=1)
        row = d2 * w * w[i] / (w + w[i]) if ward else np.sqrt(d2)
        row[~alive] = np.inf
        row[i] = np.inf
        return row

    for ward in (False, True):
        cost = np.array([cost_row(i, ward) for i in range(len(colors))])
        while alive.sum() > 1:
            i, j = divmod(int(np.argmin(cost)), len(colors))
            if (ward and alive.sum() <= k) or (not ward and cost[i, j] >= t):
                break
            i, j = min(i, j), max(i, j)
            centers[i] = (centers[i] * w[i] + centers[j] * w[j]) / (w[i] + w[j])
            w[i], w[j] = w[i] + w[j], 0
            alive[j] = False
            labels[labels == j] = i
            cost[j, :] = cost[:, j] = np.inf
            cost[i, :] = cost[:, i] = cost_row(i, ward)
    return labels, centers


def convert(src: Path, p: float | None, merge: float, max_colors: int) -> tuple[Image.Image, dict, float]:
    a = np.asarray(Image.open(src).convert("RGB"), dtype=float)
    g = a.mean(axis=2)
    p = p or outline_period(g)
    px = ndimage.uniform_filter1d(np.abs(np.diff(g, axis=1)).sum(0), 3)
    py = ndimage.uniform_filter1d(np.abs(np.diff(g, axis=0)).sum(1), 3)
    xs = sorted({0, a.shape[1], *[b + 1 for b in elastic_lines(px, p)]})
    ys = sorted({0, a.shape[0], *[b + 1 for b in elastic_lines(py, p)]})
    cells = np.array([[dominant(a[y0:y1, x0:x1]) for x0, x1 in zip(xs, xs[1:])] for y0, y1 in zip(ys, ys[1:])])
    bg = np.median(np.concatenate([cells[0], cells[-1], cells[:, 0], cells[:, -1]]), axis=0)
    not_bg = np.linalg.norm(cells - bg, axis=2) > 28
    lab, _ = ndimage.label(not_bg)
    # largest figure component; background enclosed by it (inside a bucket handle) stays transparent
    fg = ndimage.binary_fill_holes(lab == np.argmax(np.bincount(lab.ravel())[1:]) + 1) & not_bg
    uniq, inv, counts = np.unique(np.round(cells[fg]).astype(int), axis=0, return_inverse=True, return_counts=True)
    labels, centers = merge_colors(uniq, counts, merge, max_colors)
    out = np.zeros(cells.shape[:2] + (4,), dtype=np.uint8)
    out[fg, :3] = np.clip(np.round(centers[labels[inv.ravel()]]), 0, 255).astype(np.uint8)
    out[fg, 3] = 255
    yy, xx = np.nonzero(fg)
    box = [int(xx.min() - 1), int(yy.min() - 1), int(xx.max() + 2), int(yy.max() + 2)]
    grid = {"xs": xs, "ys": ys, "crop": box, "pixel": p}
    return Image.fromarray(out).crop(tuple(box)), grid, p


def main() -> None:
    args = sys.argv[1:]
    opts = {"--pixel": None, "--merge": 16.0, "--max-colors": 16}
    for key in list(opts):
        if key in args:
            i = args.index(key)
            opts[key] = float(args[i + 1])
            del args[i:i + 2]
    src, prefix = Path(args[0]), args[1]
    sprite, grid, p = convert(src, opts["--pixel"], opts["--merge"], int(opts["--max-colors"]))
    sprite.save(f"{prefix}_native.png")
    Path(f"{prefix}_grid.json").write_text(json.dumps(grid))
    a = np.asarray(sprite)
    colors = len({tuple(c) for c in a[a[..., 3] == 255][:, :3]})
    ys, xs = np.nonzero(a[..., 3] == 255)
    err = grid_error(Image.open(src), sprite, grid)
    print(f"block {p:.1f}px, grid {len(grid['xs']) - 1}x{len(grid['ys']) - 1} cells -> figure "
          f"{np.ptp(xs) + 1}w x {np.ptp(ys) + 1}h, {colors} colors, error vs concept {err:.1f}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    main()
