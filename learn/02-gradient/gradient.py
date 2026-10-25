"""Lesson 02: gradient descent on the simplest possible model.

The perceptron rule only works for step outputs and separable data. Real training uses a different
idea: write down a number that measures how wrong the model is (the loss), then move the weights a
little in whatever direction makes that number smaller. The direction comes from calculus: the
derivative of the loss with respect to each weight. Repeat. That is gradient descent, and it is the
engine inside every network that follows.

Model here: a line,  prediction = w * x + b.  One weight, one bias, so the loss surface can be drawn.

Run:  .venv/bin/python learn/02-gradient/gradient.py
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import seed, sparkline, save_plot, lesson_dir

seed(0)
HERE = lesson_dir(__file__)

# ------------------------------------------------------------------ the data
# Points scattered around the line  y = 2.5 x + 1.  The job is to recover 2.5 and 1 from the points.
N = 50
x = np.random.uniform(0, 10, N)
y = 2.5 * x + 1.0 + np.random.normal(0, 2.0, N)        # true line plus noise
TRUE_W, TRUE_B = 2.5, 1.0


# ------------------------------------------------------------------ the loss
def predict(w, b):
    return w * x + b


def loss(w, b):
    """Mean squared error: average of (prediction - target)^2 over the data.
    Squaring makes every miss positive and punishes big misses more. The 1/N keeps it comparable
    across data sizes."""
    return np.mean((predict(w, b) - y) ** 2)


# -------------------------------------------- the gradient, two different ways
def grad_numeric(w, b, h=1e-5):
    """A derivative is 'how much does the loss change if I nudge this parameter a tiny bit'.
    Compute exactly that, by nudging. Slow (two loss evaluations per parameter) but needs no math,
    and it is how we will check the hand-derived formulas in every later lesson."""
    dw = (loss(w + h, b) - loss(w - h, b)) / (2 * h)
    db = (loss(w, b + h) - loss(w, b - h)) / (2 * h)
    return dw, db


def grad_analytic(w, b):
    """The same thing from the chain rule.  L = mean( (w x + b - y)^2 ).
    Let e = w x + b - y (the error on each point). Then
        dL/dw = mean( 2 e * x )      the inner derivative of e with respect to w is x
        dL/db = mean( 2 e * 1 )      and with respect to b is 1
    """
    e = predict(w, b) - y
    return np.mean(2 * e * x), np.mean(2 * e)


w0, b0 = 0.0, 0.0                                    # where training will start
print(f"loss at the start (w={w0}, b={b0}): {loss(w0, b0):.3f}")
print(f"loss at the truth (w={TRUE_W}, b={TRUE_B}): {loss(TRUE_W, TRUE_B):.3f}   (not zero: the noise)")
gn, ga = grad_numeric(w0, b0), grad_analytic(w0, b0)
print(f"gradient at the start, numeric : dL/dw={gn[0]:+.4f} dL/db={gn[1]:+.4f}")
print(f"gradient at the start, analytic: dL/dw={ga[0]:+.4f} dL/db={ga[1]:+.4f}")
assert np.allclose(gn, ga, atol=1e-5), "the formula and the nudge test must agree"
print("negative gradient means: increasing w (and b) lowers the loss, so step that way\n")


# ------------------------------------------------------------- gradient descent
def gradient_descent(lr, steps=200, w=0.0, b=0.0):
    """Repeat: compute the gradient, step against it. `lr` (learning rate) is the step size.
    Returns the loss after every step and the final parameters."""
    history = []
    for _ in range(steps):
        dw, db = grad_analytic(w, b)
        w = w - lr * dw                       # minus: the gradient points uphill, we want down
        b = b - lr * db
        L = loss(w, b)
        history.append(L)
        if not np.isfinite(L) or L > 1e6:     # diverged: stop before numbers overflow
            break
    return np.array(history), w, b


print("learning rate sweep (200 steps each)")
runs = {}
for lr in (0.001, 0.01, 0.04):
    hist, w, b = gradient_descent(lr)
    runs[lr] = hist
    verdict = ("DIVERGED after %d steps" % len(hist)) if len(hist) < 200 else f"w={w:.3f} b={b:.3f}"
    print(sparkline(hist, label=f"lr={lr}") + f"   {verdict}")

print("""
  lr=0.001 gets w right fast but b crawls (b=0.4 after 200 steps). The bowl is not round: it is steep
           along w (x is large, so w matters a lot) and shallow along b. One learning rate has to
           serve both directions, which is the central annoyance of gradient descent.
  lr=0.01  settles near w=2.5, b=1.
  lr=0.04  overshoots the bottom of the bowl, lands higher up the other side, overshoots further; loss explodes.
  Rule of thumb for this loss: steps bigger than about 1/(largest curvature) diverge. Here the
  curvature in w is 2*mean(x^2) = %.0f, so lr must stay under about %.3f.""" % (2 * np.mean(x ** 2), 1 / np.mean(x ** 2)))

hist, w, b = gradient_descent(0.01, steps=2000)
print(f"\nlr=0.01 for 2000 steps: w={w:.4f} b={b:.4f}  loss={hist[-1]:.4f}  (truth 2.5, 1.0; noise floor {loss(TRUE_W, TRUE_B):.4f})")
assert abs(w - TRUE_W) < 0.2 and abs(b - TRUE_B) < 1.0
assert len(runs[0.04]) < 200, "lr=0.04 should diverge"
assert runs[0.001][-1] > runs[0.01][-1], "lr=0.001 should be slower than lr=0.01"

# ----------------------------------------------------------------------- plots
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
ws = np.linspace(-1, 6, 200)
axes[0].plot(ws, [loss(wi, TRUE_B) for wi in ws])
axes[0].axvline(TRUE_W, ls="--", c="gray")
axes[0].set(title="loss as a function of w (b fixed at 1)", xlabel="w", ylabel="mean squared error")
axes[0].annotate("slope here is dL/dw", xy=(0, loss(0, TRUE_B)), xytext=(1.2, loss(0, TRUE_B)), arrowprops=dict(arrowstyle="->"))
for lr, h in runs.items():
    axes[1].plot(h[:60], label=f"lr={lr}")
axes[1].set(title="loss per step, three learning rates", xlabel="step", ylabel="loss", yscale="log")
axes[1].legend()
axes[2].scatter(x, y, s=12, label="data")
xs = np.array([0, 10])
axes[2].plot(xs, TRUE_W * xs + TRUE_B, "--", c="gray", label="true line")
axes[2].plot(xs, w * xs + b, c="C3", label=f"fitted w={w:.2f} b={b:.2f}")
axes[2].set(title="the fit", xlabel="x", ylabel="y")
axes[2].legend()
print("plot:", save_plot(fig, os.path.join(HERE, "plots", "gradient.png")))
print("ok")
