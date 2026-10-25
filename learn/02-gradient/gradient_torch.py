"""Lesson 02, torch twin: the same line fit, with autograd computing the derivatives.

Same data, same start, same learning rate. The only change: instead of `grad_analytic`, we mark w
and b as `requires_grad=True`, compute the loss, and call `loss.backward()`. PyTorch recorded every
operation that led from w and b to the loss, and runs the chain rule backwards through them, leaving
the result in `w.grad` and `b.grad`. The numbers must match lesson 02's formula to many decimals.

Run:  .venv/bin/python learn/02-gradient/gradient_torch.py
"""
import os, sys
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import seed, sparkline

seed(0)
N = 50                                                      # identical data to gradient.py
x_np = np.random.uniform(0, 10, N)
y_np = 2.5 * x_np + 1.0 + np.random.normal(0, 2.0, N)
x = torch.tensor(x_np, dtype=torch.float64)                 # float64 so we can compare at 1e-8
y = torch.tensor(y_np, dtype=torch.float64)


def analytic(w, b):
    e = w * x + b - y
    return (2 * e * x).mean().item(), (2 * e).mean().item()


# --- one gradient, two ways -------------------------------------------------------------------
w = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)   # "track what happens to me"
b = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
loss = ((w * x + b - y) ** 2).mean()        # every op here is recorded in a graph behind the scenes
loss.backward()                             # walk that graph backwards: d(loss)/d(everything tracked)
print(f"autograd : dL/dw={w.grad.item():+.6f} dL/db={b.grad.item():+.6f}")
print(f"formula  : dL/dw={analytic(0.0, 0.0)[0]:+.6f} dL/db={analytic(0.0, 0.0)[1]:+.6f}")
assert np.allclose([w.grad.item(), b.grad.item()], analytic(0.0, 0.0), atol=1e-9)


# --- gradient descent with autograd ------------------------------------------------------------
def gradient_descent(lr, steps):
    w = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
    b = torch.tensor(0.0, dtype=torch.float64, requires_grad=True)
    history = []
    for _ in range(steps):
        loss = ((w * x + b - y) ** 2).mean()
        loss.backward()                 # fills w.grad, b.grad
        with torch.no_grad():           # the update itself must not be recorded as part of the model
            w -= lr * w.grad
            b -= lr * b.grad
        w.grad.zero_(); b.grad.zero_()  # .grad ACCUMULATES across backward() calls; reset it every step
        history.append(loss.item())
    return np.array(history), w.item(), b.item()


hist, wf, bf = gradient_descent(0.01, 2000)
print(sparkline(hist, label="lr=0.01"))
print(f"after 2000 steps: w={wf:.6f} b={bf:.6f} loss={hist[-1]:.6f}")

# --- the numpy lesson again, inline, to prove the two paths are the same computation -------------
w_np, b_np = 0.0, 0.0
for _ in range(2000):
    e = w_np * x_np + b_np - y_np
    w_np, b_np = w_np - 0.01 * np.mean(2 * e * x_np), b_np - 0.01 * np.mean(2 * e)
print(f"numpy twin      : w={w_np:.6f} b={b_np:.6f}")
assert np.allclose([wf, bf], [w_np, b_np], atol=1e-9), "autograd and the hand formula must give identical training"

# --- the same loop written the way PyTorch code is normally written -------------------------------
# An optimizer object just does the `w -= lr * w.grad` and `.zero_()` lines for every parameter.
params = [torch.tensor(0.0, dtype=torch.float64, requires_grad=True) for _ in range(2)]
opt = torch.optim.SGD(params, lr=0.01)
for _ in range(2000):
    opt.zero_grad()
    loss = ((params[0] * x + params[1] - y) ** 2).mean()
    loss.backward()
    opt.step()
print(f"torch.optim.SGD : w={params[0].item():.6f} b={params[1].item():.6f}")
assert np.allclose([p.item() for p in params], [w_np, b_np], atol=1e-9)
print("ok")
