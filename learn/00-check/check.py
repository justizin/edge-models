"""Environment check: confirms numpy, matplotlib, scikit-learn and torch import and run on this CPU.
The Xeon E5-2697 v2 has AVX but not AVX2/FMA; torch's CPU wheel must pick a kernel set that works
here (it reports it as `cpu capability`). If anything below crashes with "Illegal instruction",
the torch halves of the lessons need a different wheel; the numpy halves are unaffected.

Run:  .venv/bin/python learn/00-check/check.py
"""
import platform, sys, time

print("python", sys.version.split()[0], platform.machine())

import numpy as np
print("numpy", np.__version__)
a = np.random.default_rng(0).standard_normal((512, 512)).astype(np.float32)
t = time.perf_counter(); (a @ a).sum(); print(f"  512x512 matmul {(time.perf_counter() - t) * 1e3:.1f} ms")

import matplotlib
matplotlib.use("Agg")
print("matplotlib", matplotlib.__version__, "(Agg backend: plots are written to PNG files)")

import sklearn
print("scikit-learn", sklearn.__version__)

try:
    import torch
    print("torch", torch.__version__, "cpu capability", torch.backends.cpu.get_cpu_capability(),
          "threads", torch.get_num_threads())
    b = torch.from_numpy(a)
    t = time.perf_counter(); (b @ b).sum().item(); print(f"  512x512 matmul {(time.perf_counter() - t) * 1e3:.1f} ms")
    x = torch.tensor([3.0], requires_grad=True)
    (x ** 2).backward()
    assert x.grad.item() == 6.0, x.grad
    print("  autograd ok: d(x^2)/dx at x=3 is", x.grad.item())
except ImportError:
    print("torch: not installed (numpy lessons still work; torch twins will be skipped)")

print("ok")
