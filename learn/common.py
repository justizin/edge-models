"""Tiny helpers shared by the lessons. Deliberately small: the lessons themselves hold all the
neural-network code so nothing important is hidden in here.

  seed(n)                 -> seeds random, numpy (and torch if installed) so runs are repeatable
  sparkline(values)       -> a one-line terminal plot of a loss curve, so you see it over SSH
  save_plot(fig, path)    -> writes a PNG next to the lesson (creates the plots/ dir)
"""
import os, random


def seed(n: int = 0) -> None:
    random.seed(n)
    try:
        import numpy as np
        np.random.seed(n)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(n)
    except ImportError:
        pass


_BARS = " ▁▂▃▄▅▆▇█"


def sparkline(values, width: int = 60, label: str = "") -> str:
    """Downsample `values` to `width` points and draw them with block characters.
    Scaled to the min/max of the series, so it shows the *shape* of a curve, not absolute size;
    the numbers at the ends tell you the scale."""
    vals = [float(v) for v in values]
    if len(vals) > width:
        step = len(vals) / width
        vals = [vals[int(i * step)] for i in range(width)]
    lo, hi = min(vals), max(vals)
    span = hi - lo or 1.0
    line = "".join(_BARS[int((v - lo) / span * (len(_BARS) - 1))] for v in vals)
    return f"{label:>10} {line}  {vals[0]:.4g} -> {vals[-1]:.4g}"


def save_plot(fig, path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    return path


def lesson_dir(file: str) -> str:
    """Absolute directory of the calling lesson script, so plots land next to it however you run it."""
    return os.path.dirname(os.path.abspath(file))
