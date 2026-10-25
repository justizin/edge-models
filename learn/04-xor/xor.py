"""Lesson 04: a hidden layer, and backpropagation derived by hand.

Lesson 01 ended with a single neuron unable to learn XOR because it can only draw one line.
Put two sigmoid neurons side by side, each drawing its own line, and feed their two outputs into a
third neuron: now the third neuron sees a *transformed* version of the inputs in which XOR is
linearly separable. That middle pair is a hidden layer. Training it needs the gradient of the loss
with respect to weights that are two steps away from the output, which is where the chain rule gets
applied layer by layer: backpropagation.

The network:   x (2)  --W1,b1-->  z1 --sigmoid-->  h (H)  --W2,b2-->  z2 --sigmoid-->  p (1)

Run:  .venv/bin/python learn/04-xor/xor.py
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import seed, sparkline, save_plot, lesson_dir

HERE = lesson_dir(__file__)
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y = np.array([0, 1, 1, 0], dtype=float)
N = len(y)
H = 2                   # hidden units. 2 is the minimum that can do XOR; try 1 (fails) and 4 (easier).
SEED = 3                # some seeds with H=2 get stuck in a flat region; see the README exercises
LR, STEPS = 1.0, 5000


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


# ------------------------------------------------------------------ parameters
def init(seed_):
    rng = np.random.default_rng(seed_)
    return dict(W1=rng.normal(0, 1, (2, H)),     # one column per hidden unit: W1[:, j] is unit j's two weights
                b1=rng.normal(0, 1, H),
                W2=rng.normal(0, 1, (H, 1)),     # the output neuron's weight on each hidden unit
                b2=rng.normal(0, 1, 1))


# --------------------------------------------------------------------- forward
def forward(P, X=X):
    """Returns every intermediate value, because backward needs them."""
    z1 = X @ P["W1"] + P["b1"]       # (N, H)   each hidden unit's weighted sum, lesson 01's z, H times
    h = sigmoid(z1)                  # (N, H)   hidden activations: the "bent" version of the input
    z2 = h @ P["W2"] + P["b2"]       # (N, 1)   the output neuron sees h instead of x
    p = sigmoid(z2)[:, 0]            # (N,)
    return z1, h, z2, p


def loss(P):
    p = forward(P)[-1]
    return -np.mean(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12))


# -------------------------------------------------------------------- backward
def backward(P):
    """The chain rule, one layer at a time, from the loss back to W1. Everything with a 'd' in front
    is 'dL/d(that thing)' and has the same shape as the thing.

      output layer (identical to lesson 03, with h in place of x):
        dz2 = (p - y) / N                      (N, 1)
        dW2 = h.T @ dz2                         (H, 1)   sum over points of  h_i * dz2_i
        db2 = sum(dz2)                          (1,)
      through to the hidden layer:
        dh  = dz2 @ W2.T                        (N, H)   how much the loss cares about each hidden value:
                                                         dz2 scaled by the weight that carried h to z2
        dz1 = dh * h * (1 - h)                  (N, H)   through the sigmoid: multiply by its derivative
      hidden layer (lesson 03 again, now with dz1 playing the role of (p - y)):
        dW1 = X.T @ dz1                         (2, H)
        db1 = sum(dz1, axis=0)                  (H,)

    Notice the pattern: each layer's gradient is  (input to that layer).T @ (gradient at its output),
    and passing a gradient back through a layer is  (gradient) @ W.T, then times the activation's
    derivative. That pattern is all a deep network's backward pass is."""
    z1, h, z2, p = forward(P)
    dz2 = ((p - y) / N)[:, None]                     # (N, 1)
    dW2 = h.T @ dz2
    db2 = dz2.sum(axis=0)
    dh = dz2 @ P["W2"].T                             # (N, H)
    dz1 = dh * h * (1 - h)
    dW1 = X.T @ dz1
    db1 = dz1.sum(axis=0)
    return dict(W1=dW1, b1=db1, W2=dW2, b2=db2)


def gradient_check(P, h=1e-6):
    """Nudge every single parameter and compare with backward(). The test that catches wrong backprop."""
    G = backward(P)
    worst = 0.0
    for k in P:
        for idx in np.ndindex(P[k].shape):
            old = P[k][idx]
            P[k][idx] = old + h; up = loss(P)
            P[k][idx] = old - h; dn = loss(P)
            P[k][idx] = old
            num = (up - dn) / (2 * h)
            worst = max(worst, abs(num - G[k][idx]))
    return worst


# -------------------------------------------------------------------- training
P = init(SEED)
print(f"gradient check on {sum(v.size for v in P.values())} parameters: worst |numeric - backprop| = {gradient_check(P):.2e}")
assert gradient_check(P) < 1e-6

history = []
for step in range(STEPS):
    G = backward(P)
    for k in P:
        P[k] -= LR * G[k]               # gradient descent on every parameter at once
    history.append(loss(P))
print(sparkline(history, label="loss"))

z1, h, z2, p = forward(P)
print(f"after {STEPS} steps: loss={history[-1]:.4f}")
print("  x      target  p       hidden h1   h2")
for i in range(N):
    print(f"  {X[i].astype(int)}   {int(y[i])}       {p[i]:.3f}   {h[i, 0]:.3f}      {h[i, 1]:.3f}")
assert history[-1] < 0.05 and np.all((p > 0.5) == (y == 1)), "XOR not learned; try another SEED"

print("""
  Read the hidden columns: the four inputs have been moved to new positions (h1, h2). In that space
  the two 1-targets sit on one side of a line and the two 0-targets on the other, which lesson 01
  said was impossible in the original (x1, x2) space. The output neuron is just lesson 03 on h.""")
for j in range(H):
    w1, w2 = P["W1"][:, j]; b = P["b1"][j]
    print(f"  hidden unit {j + 1} fires when  {w1:+.2f} x1 {w2:+.2f} x2 {b:+.2f} > 0   (its line in the input plane)")
print(f"  output fires when  {P['W2'][0, 0]:+.2f} h1 {P['W2'][1, 0]:+.2f} h2 {P['b2'][0]:+.2f} > 0")

# ------------------------------------------------------------------------ plots
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
g1, g2 = np.meshgrid(np.linspace(-0.5, 1.5, 200), np.linspace(-0.5, 1.5, 200))
grid = np.c_[g1.ravel(), g2.ravel()]
pg = forward(P, grid)[-1].reshape(g1.shape)
axes[0].contourf(g1, g2, pg, levels=np.linspace(0, 1, 11), cmap="RdBu_r", alpha=0.6)
axes[0].contour(g1, g2, pg, levels=[0.5], colors="k")
for j in range(H):                                       # each hidden unit's z1 = 0 line
    w1, w2 = P["W1"][:, j]; b = P["b1"][j]
    xs = np.array([-0.5, 1.5])
    if abs(w2) > 1e-6:
        axes[0].plot(xs, -(w1 * xs + b) / w2, "--", label=f"hidden unit {j + 1}: z=0")
axes[0].scatter(*X[y == 0].T, s=80, c="C0", edgecolor="k", zorder=3, label="target 0")
axes[0].scatter(*X[y == 1].T, s=80, c="C3", edgecolor="k", zorder=3, label="target 1")
axes[0].set(title="input space: output and hidden-unit lines", xlabel="x1", ylabel="x2", xlim=(-0.5, 1.5), ylim=(-0.5, 1.5))
axes[0].legend(loc="upper right", fontsize=8)

hg = forward(P, grid)[1]                                  # where the grid lands in hidden space
axes[1].scatter(hg[:, 0], hg[:, 1], s=2, c=pg.ravel(), cmap="RdBu_r", alpha=0.3)
axes[1].scatter(*h[y == 0].T, s=80, c="C0", edgecolor="k", zorder=3, label="target 0")
axes[1].scatter(*h[y == 1].T, s=80, c="C3", edgecolor="k", zorder=3, label="target 1")
w1, w2 = P["W2"][:, 0]; b = P["b2"][0]
hs = np.array([0, 1])
if abs(w2) > 1e-6:
    axes[1].plot(hs, -(w1 * hs + b) / w2, "k", label="output neuron: z2=0")
axes[1].set(title="hidden space: same points after the hidden layer", xlabel="h1", ylabel="h2", xlim=(-0.05, 1.05), ylim=(-0.05, 1.05))
axes[1].legend(loc="best", fontsize=8)

axes[2].plot(history); axes[2].set(title="training loss", xlabel="step", ylabel="binary cross-entropy")
print("plot:", save_plot(fig, os.path.join(HERE, "plots", "xor.png")))
print("ok")
