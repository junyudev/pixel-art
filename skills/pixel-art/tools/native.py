"""Recover native-resolution pixel art from an upscaled (possibly non-integer, camera-zoomed) screenshot.
Detects grid period via FFT and phase via edge alignment, then samples each cell's inner median.
Usage: native.py SRC OUT"""
import sys
import numpy as np
from PIL import Image

def dominant_period(profile: np.ndarray) -> float:
    p = profile - profile.mean()
    n = len(p) * 8  # zero-pad for finer frequency resolution
    spec = np.abs(np.fft.rfft(p * np.hanning(len(p)), n))
    freqs = np.fft.rfftfreq(n)
    band = (freqs > 1 / 12) & (freqs < 1 / 2.2)
    return 1 / freqs[band][np.argmax(spec[band])]

def best_phase(profile: np.ndarray, period: float) -> float:
    # Edge energy at diff index i sits on the boundary x = i + 1; maximize alignment of boundaries.
    xs = np.arange(len(profile)) + 1.0
    candidates = np.linspace(0, period, 48, endpoint=False)
    score = [np.sum(profile * np.cos(2 * np.pi * (xs - c) / period)) for c in candidates]
    return candidates[int(np.argmax(score))]

def sample(a: np.ndarray, period: float, phase: float, axis: int) -> np.ndarray:
    n = int((a.shape[axis] - phase) / period)
    starts = phase + np.arange(n) * period
    lo = np.clip(np.round(starts + period * 0.25).astype(int), 0, a.shape[axis] - 1)
    hi = np.clip(np.round(starts + period * 0.75).astype(int), lo + 1, a.shape[axis])
    parts = [np.median(np.take(a, range(a0, a1), axis=axis), axis=axis, keepdims=True) for a0, a1 in zip(lo, hi)]
    return np.concatenate(parts, axis=axis)

if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
    sys.exit(__doc__)
src, out = sys.argv[1:3]
a = np.asarray(Image.open(src).convert("RGB"), dtype=float)
g = a.mean(axis=2)
ex = np.abs(np.diff(g, axis=1)).sum(axis=0)
ey = np.abs(np.diff(g, axis=0)).sum(axis=1)
tx, ty = dominant_period(ex), dominant_period(ey)
native = sample(sample(a, ty, best_phase(ey, ty), 0), tx, best_phase(ex, tx), 1)
Image.fromarray(native.astype(np.uint8)).save(out)
print(f"{src.split('/')[-1]:30s} period=({tx:.3f},{ty:.3f}) native={native.shape[1]}x{native.shape[0]}")
