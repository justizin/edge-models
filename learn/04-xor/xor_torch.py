"""Lesson 04, torch twin: autograd reproduces the hand-derived backward pass exactly.

The same network with the same initial weights (copied from the numpy init). One forward pass, one
`loss.backward()`, and every one of the nine gradients is compared with xor.py's backward(). Then the
full training run, which must land on the same loss. Finally the usual PyTorch spelling of the same
network, nn.Sequential, so you can recognise it in other people's code.

Run:  .venv/bin/python learn/04-xor/xor_torch.py
"""
import os, sys
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import sparkline

torch.set_default_dtype(torch.float64)
X_np = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y_np = np.array([0, 1, 1, 0], dtype=float)
X, y = torch.tensor(X_np), torch.tensor(y_np)
H, SEED, LR, STEPS = 2, 3, 1.0, 5000


def init_np(seed_):                                   # byte-for-byte the init from xor.py
    rng = np.random.default_rng(seed_)
    return dict(W1=rng.normal(0, 1, (2, H)), b1=rng.normal(0, 1, H),
                W2=rng.normal(0, 1, (H, 1)), b2=rng.normal(0, 1, 1))


def backward_np(P):                                   # xor.py's hand-written backward, for the comparison
    sig = lambda z: 1 / (1 + np.exp(-z))
    h = sig(X_np @ P["W1"] + P["b1"]); p = sig(h @ P["W2"] + P["b2"])[:, 0]
    dz2 = ((p - y_np) / 4)[:, None]
    dh = dz2 @ P["W2"].T; dz1 = dh * h * (1 - h)
    return dict(W1=X_np.T @ dz1, b1=dz1.sum(0), W2=h.T @ dz2, b2=dz2.sum(0))


P0 = init_np(SEED)
P = {k: torch.tensor(v, requires_grad=True) for k, v in P0.items()}   # same numbers, now tracked


def forward(P, X=X):
    h = torch.sigmoid(X @ P["W1"] + P["b1"])
    return torch.sigmoid(h @ P["W2"] + P["b2"])[:, 0]


def loss_fn(P):
    p = forward(P)
    return -(y * torch.log(p) + (1 - y) * torch.log(1 - p)).mean()


# --- one backward pass, nine gradients, compared one by one -------------------------------------
loss_fn(P).backward()
G_hand = backward_np(P0)
for k in P:
    diff = np.abs(P[k].grad.numpy() - G_hand[k]).max()
    print(f"  d loss / d {k}: autograd == hand-derived, max difference {diff:.1e}")
    assert diff < 1e-12, k
print("autograd ran the same chain rule we wrote out in xor.py\n")

# --- training ------------------------------------------------------------------------------------
P = {k: torch.tensor(v, requires_grad=True) for k, v in init_np(SEED).items()}
history = []
for _ in range(STEPS):
    loss = loss_fn(P)
    loss.backward()
    with torch.no_grad():
        for k in P:
            P[k] -= LR * P[k].grad
            P[k].grad.zero_()
    history.append(loss.item())
print(sparkline(history, label="loss"))
p = forward(P).detach().numpy()
print(f"after {STEPS} steps: loss={history[-1]:.4f}  p={p.round(3)}")
assert history[-1] < 0.05 and np.all((p > 0.5) == (y_np == 1))

# --- the same network as PyTorch usually spells it ----------------------------------------------
model = torch.nn.Sequential(
    torch.nn.Linear(2, H),       # W1, b1     (stored transposed: weight is (H, 2))
    torch.nn.Sigmoid(),
    torch.nn.Linear(H, 1),       # W2, b2
    torch.nn.Sigmoid(),
)
with torch.no_grad():            # load the lesson's initial weights so the runs are comparable
    model[0].weight[:] = torch.tensor(P0["W1"].T); model[0].bias[:] = torch.tensor(P0["b1"])
    model[2].weight[:] = torch.tensor(P0["W2"].T); model[2].bias[:] = torch.tensor(P0["b2"])
opt = torch.optim.SGD(model.parameters(), lr=LR)
bce = torch.nn.BCELoss()
for _ in range(STEPS):
    opt.zero_grad()
    loss = bce(model(X)[:, 0], y)
    loss.backward()
    opt.step()
print(f"nn.Sequential: loss={loss.item():.4f}  p={model(X)[:, 0].detach().numpy().round(3)}")
assert abs(loss.item() - history[-1]) < 1e-6, "same init, same steps, same answer"
print(model)
print("ok")
