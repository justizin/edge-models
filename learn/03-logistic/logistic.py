"""Lesson 03: a neuron that outputs a probability (logistic regression).

Lesson 01's step activation has a problem for gradient descent: its derivative is zero everywhere
(and undefined at the jump), so the gradient says nothing about which way to move. Replace the step
with a smooth S-curve, the sigmoid, and the output becomes "probability that this is class 1".
Pair it with a loss designed for probabilities (binary cross-entropy) and lesson 02's recipe trains
a classifier. This single neuron is also known as logistic regression and it is still a strong
baseline for many security classification jobs.

The toy data has a security flavour: per-source-host counts of failed logins per minute (x1) and
distinct usernames tried (x2). Normal hosts have few of both; a brute-forcer has many of both.

Run:  .venv/bin/python learn/03-logistic/logistic.py
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import seed, sparkline, save_plot, lesson_dir

seed(0)
HERE = lesson_dir(__file__)

# ------------------------------------------------------------------ the data
N_PER_CLASS = 100
benign = np.random.normal(loc=[2.0, 1.5], scale=[1.2, 0.8], size=(N_PER_CLASS, 2))     # few failures, few names
attack = np.random.normal(loc=[7.0, 5.5], scale=[1.8, 1.6], size=(N_PER_CLASS, 2))     # many of both
X_raw = np.clip(np.vstack([benign, attack]), 0, None)          # counts cannot be negative
y = np.array([0] * N_PER_CLASS + [1] * N_PER_CLASS, dtype=float)

# Standardize: subtract the mean, divide by the standard deviation, per feature. Lesson 02 showed
# that large inputs make the loss bowl steep and force a tiny learning rate; this fixes that and
# makes the two weights comparable (both are "per standard deviation of the feature").
MEAN, STD = X_raw.mean(axis=0), X_raw.std(axis=0)
X = (X_raw - MEAN) / STD
N = len(y)


# ----------------------------------------------------------------- the model
def sigmoid(z):
    """Squashes any real number into (0, 1). sigmoid(0) = 0.5; large positive -> 1; large negative -> 0.
    Its derivative is  sigmoid(z) * (1 - sigmoid(z)),  which we will need for backprop in lesson 04."""
    return 1.0 / (1.0 + np.exp(-z))


def forward(w, b):
    z = X @ w + b              # weighted sums for all N points at once: shape (N,)
    return sigmoid(z)          # p[i] = model's probability that point i is an attack


def loss(w, b, eps=1e-12):
    """Binary cross-entropy. For each point: -log(p) if the truth is 1, -log(1-p) if the truth is 0.
    Confident and right -> near 0. Confident and wrong -> huge. Averaged over the points.
    (eps keeps log(0) from happening when p rounds to exactly 0 or 1.)"""
    p = forward(w, b)
    return -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))


def grad(w, b):
    """Derivation (chain rule from the loss back to w and b), for one point then averaged:
        L = -[y log p + (1-y) log(1-p)]        p = sigmoid(z)        z = w.x + b
        dL/dp = -y/p + (1-y)/(1-p)
        dp/dz = p (1 - p)                       (the sigmoid derivative)
        dL/dz = dL/dp * dp/dz = p - y           <- the two simplify to this. Worth checking by hand once.
        dz/dw = x,  dz/db = 1
    so  dL/dw = mean over points of (p - y) x,   dL/db = mean of (p - y)."""
    p = forward(w, b)
    dz = (p - y) / N                      # the 1/N of the mean, folded in here
    return X.T @ dz, dz.sum()             # X.T @ dz  sums (p_i - y_i) x_i over i


def grad_numeric(w, b, h=1e-6):
    gw = np.zeros_like(w)
    for j in range(len(w)):
        e = np.zeros_like(w); e[j] = h
        gw[j] = (loss(w + e, b) - loss(w - e, b)) / (2 * h)
    gb = (loss(w, b + h) - loss(w, b - h)) / (2 * h)
    return gw, gb


w = np.zeros(2); b = 0.0                 # start at "no idea": every p = 0.5
print(f"loss at start: {loss(w, b):.4f}   (= -log(0.5) = {-np.log(0.5):.4f}, the loss of pure guessing)")
ga, gn = grad(w, b), grad_numeric(w, b)
print(f"gradient check: analytic {np.round(ga[0], 6)}, {ga[1]:.6f}   numeric {np.round(gn[0], 6)}, {gn[1]:.6f}")
assert np.allclose(ga[0], gn[0], atol=1e-6) and abs(ga[1] - gn[1]) < 1e-6

# ------------------------------------------------------------------- training
LR, STEPS = 0.5, 300
history = []
for step in range(STEPS):
    gw, gb = grad(w, b)
    w -= LR * gw
    b -= LR * gb
    history.append(loss(w, b))
print(sparkline(history, label="loss"))

p = forward(w, b)
pred = (p > 0.5).astype(float)          # the step comes back at the very end, as a decision rule
acc = np.mean(pred == y)
print(f"after {STEPS} steps: w={np.round(w, 3)} b={b:.3f}  loss={history[-1]:.4f}  accuracy={acc:.3f}")
print("  both weights positive: more failed logins and more usernames both push toward 'attack'.")
assert acc > 0.95 and history[-1] < 0.15

# ------------------------------------------------------- what the model says
print("\nmodel's probability of brute force for some hosts:")
for fails, names in ((1, 1), (3, 2), (5, 3), (5, 6), (9, 7)):
    x_std = (np.array([fails, names]) - MEAN) / STD
    print(f"  {fails} failed logins/min, {names} usernames -> p = {sigmoid(x_std @ w + b):.3f}")
print("  the probability lets you pick a threshold other than 0.5: alert at 0.9 to cut false alarms,")
print("  or at 0.2 if missing an attack costs more than an analyst's time.")

# ------------------------------------------------------------------------ plots
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
zs = np.linspace(-6, 6, 200)
axes[0].plot(zs, sigmoid(zs), label="sigmoid(z)")
axes[0].plot(zs, sigmoid(zs) * (1 - sigmoid(zs)), label="its derivative")
axes[0].step(zs, (zs > 0).astype(float), where="post", ls="--", c="gray", label="step (lesson 01)")
axes[0].set(title="activation functions", xlabel="z = w.x + b"); axes[0].legend()

g1, g2 = np.meshgrid(np.linspace(0, 12, 200), np.linspace(0, 10, 200))
grid = (np.c_[g1.ravel(), g2.ravel()] - MEAN) / STD
pp = sigmoid(grid @ w + b).reshape(g1.shape)
cs = axes[1].contourf(g1, g2, pp, levels=np.linspace(0, 1, 11), cmap="RdBu_r", alpha=0.6)
fig.colorbar(cs, ax=axes[1], label="p(attack)")
axes[1].contour(g1, g2, pp, levels=[0.5], colors="k")
axes[1].scatter(*X_raw[y == 0].T, s=12, c="C0", label="benign")
axes[1].scatter(*X_raw[y == 1].T, s=12, c="C3", label="brute force")
axes[1].set(title="decision boundary (black: p = 0.5)", xlabel="failed logins / min", ylabel="distinct usernames")
axes[1].legend(loc="lower right")

axes[2].plot(history); axes[2].set(title="training loss", xlabel="step", ylabel="binary cross-entropy")
print("plot:", save_plot(fig, os.path.join(HERE, "plots", "logistic.png")))
print("ok")
