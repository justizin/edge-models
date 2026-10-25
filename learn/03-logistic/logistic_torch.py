"""Lesson 03, torch twin: logistic regression with autograd, then the idiomatic PyTorch version.

Three passes over the same data:
  1. hand-built: a weight tensor, torch.sigmoid, the cross-entropy written out; autograd gradient
     compared to the (p - y) x formula from logistic.py at the starting point.
  2. the same training loop; final weights must match the numpy lesson.
  3. the way PyTorch code is normally written: nn.Linear + BCEWithLogitsLoss + an optimizer.
     BCEWithLogitsLoss takes z (before the sigmoid) and applies sigmoid + log in one numerically
     safe step, which is why real code almost never calls sigmoid then BCELoss.

Run:  .venv/bin/python learn/03-logistic/logistic_torch.py
"""
import os, sys
import numpy as np
import torch
import torch.nn.functional as F
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import seed, sparkline

seed(0)
N_PER_CLASS = 100                                                                    # same data as logistic.py
benign = np.random.normal(loc=[2.0, 1.5], scale=[1.2, 0.8], size=(N_PER_CLASS, 2))
attack = np.random.normal(loc=[7.0, 5.5], scale=[1.8, 1.6], size=(N_PER_CLASS, 2))
X_raw = np.clip(np.vstack([benign, attack]), 0, None)
y_np = np.array([0] * N_PER_CLASS + [1] * N_PER_CLASS, dtype=float)
X_np = (X_raw - X_raw.mean(axis=0)) / X_raw.std(axis=0)
X = torch.tensor(X_np)                 # float64, like numpy
y = torch.tensor(y_np)
N = len(y)

# --- 1. one gradient, autograd vs formula --------------------------------------------------------
w = torch.zeros(2, dtype=torch.float64, requires_grad=True)
b = torch.zeros(1, dtype=torch.float64, requires_grad=True)
p = torch.sigmoid(X @ w + b)
loss = -(y * torch.log(p) + (1 - y) * torch.log(1 - p)).mean()
loss.backward()
formula_w = X_np.T @ ((p.detach().numpy() - y_np) / N)                        # dL/dw = mean (p - y) x
formula_b = ((p.detach().numpy() - y_np) / N).sum()
print(f"autograd dL/dw={w.grad.numpy().round(6)} dL/db={b.grad.item():.6f}")
print(f"formula  dL/dw={formula_w.round(6)} dL/db={formula_b:.6f}")
assert np.allclose(w.grad.numpy(), formula_w) and abs(b.grad.item() - formula_b) < 1e-10

# --- 2. the training loop ------------------------------------------------------------------------
LR, STEPS = 0.5, 300
w = torch.zeros(2, dtype=torch.float64, requires_grad=True)
b = torch.zeros(1, dtype=torch.float64, requires_grad=True)
history = []
for _ in range(STEPS):
    p = torch.sigmoid(X @ w + b)
    loss = F.binary_cross_entropy(p, y)                 # same formula as the line above, built in
    loss.backward()
    with torch.no_grad():
        w -= LR * w.grad; b -= LR * b.grad
    w.grad.zero_(); b.grad.zero_()
    history.append(loss.item())
print(sparkline(history, label="loss"))
acc = ((torch.sigmoid(X @ w + b) > 0.5).double() == y).double().mean().item()
print(f"hand-built : w={w.detach().numpy().round(3)} b={b.item():.3f} loss={history[-1]:.4f} acc={acc:.3f}")

# numpy twin inline, so the assertion is self-contained
wn, bn = np.zeros(2), 0.0
for _ in range(STEPS):
    pn = 1 / (1 + np.exp(-(X_np @ wn + bn)))
    dz = (pn - y_np) / N
    wn -= LR * (X_np.T @ dz); bn -= LR * dz.sum()
assert np.allclose(w.detach().numpy(), wn, atol=1e-8) and abs(b.item() - bn) < 1e-8, "must match logistic.py"

# --- 3. idiomatic PyTorch ------------------------------------------------------------------------
model = torch.nn.Linear(2, 1).double()                 # w (1x2) and b (1), randomly initialised
with torch.no_grad():
    model.weight.zero_(); model.bias.zero_()           # start from zeros like the lesson
opt = torch.optim.SGD(model.parameters(), lr=LR)
loss_fn = torch.nn.BCEWithLogitsLoss()                 # sigmoid + cross-entropy, fused and stable
for _ in range(STEPS):
    opt.zero_grad()
    z = model(X).squeeze(1)                            # logits: the z before the sigmoid, shape (N,)
    loss = loss_fn(z, y)
    loss.backward()
    opt.step()
print(f"nn.Linear  : w={model.weight.detach().numpy().round(3)[0]} b={model.bias.item():.3f} loss={loss.item():.4f}")
assert np.allclose(model.weight.detach().numpy()[0], wn, atol=1e-8)
print("ok")
