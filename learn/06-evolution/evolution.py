"""Lesson 06: training by evolution instead of by gradient, and when each one wins.

Gradient descent needs a derivative. Evolution does not: keep a population of candidate weight
vectors, score each by the loss, keep the better ones, make children by mixing (crossover) and
randomly perturbing (mutation), repeat. Nothing here knows what a derivative is; the loss could be
accuracy, a count of alerts, the score of a game, or the output of a black box.

Two experiments:
  A. the XOR network from lesson 04 (9 parameters): gradient descent vs a one-individual hill
     climber vs a genetic algorithm. Spoiler: on 9 parameters random mutation is competitive.
  B. logistic regression (lesson 03) with 4, 16, 64 and 256 input features: how the cost of each
     method grows with the number of parameters. This is where gradients earn their keep.

A genetic algorithm on a network's weights is called neuroevolution. Genetic *programming* is the
same loop on program trees; the README spells out the relationship. No torch twin: autograd has
nothing to do here, which is the point.

Run:  .venv/bin/python learn/06-evolution/evolution.py
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import sparkline, save_plot, lesson_dir

HERE = lesson_dir(__file__)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def bce(p, y):
    """Binary cross-entropy, averaged over the last axis, for a batch of candidate models."""
    return -np.mean(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12), axis=-1)


# ======================================================================= the three optimizers
# Each takes a `loss_batch(Theta)` function that scores a whole (P, n) array of candidate parameter
# vectors at once (so a population costs one numpy call), a starting point, and a target loss.
# Each returns (best-loss-so-far curve, number of loss evaluations used, best theta).

def hill_climber(loss_batch, theta0, target, rng, steps, sigma):
    """(1+1) evolution strategy: one individual; mutate it; keep the child if it is not worse.
    Population of one, no crossover. The smallest thing that still counts as evolution."""
    theta = theta0[None, :]; L = loss_batch(theta)[0]; curve = [L]
    for _ in range(steps):
        child = theta + rng.normal(0, sigma, theta.shape)
        Lc = loss_batch(child)[0]
        if Lc <= L:
            theta, L = child, Lc
        curve.append(L)
        if L < target:
            break
    return np.array(curve), len(curve), theta[0]


def genetic_algorithm(loss_batch, theta0, target, rng, generations, sigma,
                      pop_size=60, elite=2, tournament=3, mutation_rate=0.3):
    """Population, selection, crossover, mutation. theta0 only sets the dimension; the population
    starts from the same N(0,1) distribution the other methods draw their single start from."""
    n = len(theta0)
    pop = rng.normal(0, 1, (pop_size, n)); pop[0] = theta0
    evals = 0; curve = []
    for _ in range(generations):
        fitness = loss_batch(pop); evals += pop_size
        order = np.argsort(fitness)                               # best first
        curve.append(fitness[order[0]])
        if fitness[order[0]] < target:
            break
        n_children = pop_size - elite
        # selection: for each child, two tournaments of `tournament` random individuals; the fittest wins
        contestants = rng.integers(0, pop_size, (n_children, 2, tournament))
        winners = np.take_along_axis(contestants, np.argmin(fitness[contestants], axis=2)[:, :, None], axis=2)[:, :, 0]
        parent_a, parent_b = pop[winners[:, 0]], pop[winners[:, 1]]
        # crossover: each gene comes from one parent or the other
        children = np.where(rng.random((n_children, n)) < 0.5, parent_a, parent_b)
        # mutation: perturb some genes with gaussian noise
        children += (rng.random((n_children, n)) < mutation_rate) * rng.normal(0, sigma, (n_children, n))
        pop = np.vstack([pop[order[:elite]], children])           # elitism: the best survive unchanged
    best = pop[np.argmin(loss_batch(pop))]
    return np.array(curve), evals, best


def gradient_descent(loss_batch, grad, theta0, target, steps, lr):
    """Lesson 02-04's loop. One step costs a forward and a backward pass; we count it as 3 loss
    evaluations (a backward pass costs roughly twice a forward), which is generous to evolution."""
    theta = theta0.copy(); curve = []
    for _ in range(steps):
        theta = theta - lr * grad(theta)
        L = loss_batch(theta[None, :])[0]; curve.append(L)
        if L < target:
            break
    return np.array(curve), 3 * len(curve), theta


# ======================================================================= A. the XOR network
X_XOR = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
Y_XOR = np.array([0, 1, 1, 0], dtype=float)
H = 2
N_XOR = 2 * H + H + H + 1              # W1 (2xH), b1 (H), W2 (Hx1), b2 (1) = 9
TARGET_XOR = 0.05                      # same "solved" bar as lesson 04


def xor_loss_batch(Theta):
    """Theta: (P, 9). Evaluate P candidate networks on the 4 XOR points in one shot."""
    P = Theta.shape[0]
    W1 = Theta[:, :2 * H].reshape(P, 2, H); b1 = Theta[:, 2 * H:3 * H]
    W2 = Theta[:, 3 * H:4 * H]; b2 = Theta[:, 4 * H]
    h = sigmoid(np.einsum("ni,pih->pnh", X_XOR, W1) + b1[:, None, :])     # (P, 4, H)
    p = sigmoid(np.einsum("pnh,ph->pn", h, W2) + b2[:, None])              # (P, 4)
    return bce(p, Y_XOR)


def xor_grad(theta):
    """Lesson 04's backward pass on the flat vector."""
    W1 = theta[:2 * H].reshape(2, H); b1 = theta[2 * H:3 * H]; W2 = theta[3 * H:4 * H].reshape(H, 1); b2 = theta[4 * H:]
    h = sigmoid(X_XOR @ W1 + b1); p = sigmoid(h @ W2 + b2)[:, 0]
    dz2 = ((p - Y_XOR) / 4)[:, None]; dh = dz2 @ W2.T; dz1 = dh * h * (1 - h)
    return np.concatenate([(X_XOR.T @ dz1).ravel(), dz1.sum(0), (h.T @ dz2).ravel(), dz2.sum(0)])


def run_xor(method, seed):
    rng = np.random.default_rng(seed); theta0 = rng.normal(0, 1, N_XOR)
    if method == "gradient descent":
        return gradient_descent(xor_loss_batch, xor_grad, theta0, TARGET_XOR, steps=5000, lr=1.0)
    if method == "hill climber":
        return hill_climber(xor_loss_batch, theta0, TARGET_XOR, rng, steps=5000, sigma=0.3)
    return genetic_algorithm(xor_loss_batch, theta0, TARGET_XOR, rng, generations=300, sigma=0.5)


METHODS = ("gradient descent", "hill climber", "genetic algorithm")
print(f"A. XOR network, {N_XOR} parameters, solved = loss < {TARGET_XOR}\n")
print("one start (seed 1) each:")
xor_curves = {}
for m in METHODS:
    curve, evals, _ = run_xor(m, 1); xor_curves[m] = (curve, evals)
    print(f"  {m:<18} {'solved' if curve[-1] < TARGET_XOR else 'NOT solved':<10} loss={curve[-1]:.4f}  loss evaluations={evals:>6}")
    print(sparkline(curve, label=""))

print("\n20 random starts each:")
xor_summary = {}
for m in METHODS:
    runs = [run_xor(m, s) for s in range(20)]
    solved = [c[-1] < TARGET_XOR for c, _, _ in runs]
    med = np.median([e for (c, e, _), ok in zip(runs, solved) if ok]) if any(solved) else float("nan")
    xor_summary[m] = (sum(solved), med)
    print(f"  {m:<18} solved {sum(solved):>2}/20   median loss evaluations when solved: {med:>6,.0f}")

print("""
  On 9 parameters there is no clear winner. A random nudge of 9 numbers has a fair chance of
  helping, so the hill climber gets by on a few hundred evaluations, about what gradient descent
  spends. All three get stuck on the same seeds: the flat regions from lesson 04 are a property of
  the loss surface, and a population explores them only slightly better than a single point.
  The GA pays for its population every generation, which is why its count is the highest.""")

# =================================================== B. scaling with the number of parameters
# Logistic regression (lesson 03) on synthetic data: n points with d standardized features, labels
# from a hidden true weight vector, no label noise. One weight per feature plus a bias, so the
# parameter count is d + 1. Solved = loss < TARGET_LR.
TARGET_LR = 0.15
N_POINTS = 200


def make_lr(d, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (N_POINTS, d))
    w_true = rng.normal(0, 1, d); w_true /= np.linalg.norm(w_true)
    y = (X @ w_true > 0).astype(float)
    return X, y


def run_lr(method, d, seed):
    X, y = make_lr(d)
    loss_batch = lambda Theta: bce(sigmoid(X @ Theta[:, :-1].T + Theta[:, -1]).T, y)    # Theta (P, d+1)

    def grad(theta):
        dz = (sigmoid(X @ theta[:-1] + theta[-1]) - y) / N_POINTS
        return np.concatenate([X.T @ dz, [dz.sum()]])

    rng = np.random.default_rng(seed); theta0 = rng.normal(0, 1, d + 1)
    sigma = 0.5 / np.sqrt(d)            # mutation size scaled to the dimension, to be fair to evolution
    if method == "gradient descent":
        return gradient_descent(loss_batch, grad, theta0, TARGET_LR, steps=5000, lr=1.0)
    if method == "hill climber":
        return hill_climber(loss_batch, theta0, TARGET_LR, rng, steps=10000, sigma=sigma)
    return genetic_algorithm(loss_batch, theta0, TARGET_LR, rng, generations=500, sigma=sigma)


DIMS = (4, 16, 64, 256)
print(f"\nB. logistic regression with d features (d+1 parameters), {N_POINTS} points, solved = loss < {TARGET_LR}")
print("   median loss evaluations over 5 starts (solved/5 in brackets):\n")
print("  " + "method".ljust(18) + "".join(f"d={d:<10}" for d in DIMS))
scaling = {m: [] for m in METHODS}
for m in METHODS:
    row = []
    for d in DIMS:
        runs = [run_lr(m, d, s) for s in range(5)]
        solved = [c[-1] < TARGET_LR for c, _, _ in runs]
        med = np.median([e for (c, e, _), ok in zip(runs, solved) if ok]) if any(solved) else float("nan")
        scaling[m].append(med)
        row.append(f"{med:>6,.0f} ({sum(solved)}/5)")
    print("  " + m.ljust(18) + "".join(r.ljust(12) for r in row))

print("""
  Read across each row. Gradient descent's cost does not grow with the number of parameters (it
  shrinks: more features make the classes easier to separate). The hill climber's cost grows
  roughly in proportion to d: a random perturbation of d numbers is a good direction with
  probability that falls as d rises, so it needs more tries per useful step. The GA sits in
  between, limited by paying for 60 individuals per generation.

  This is the whole story in one sentence: a gradient tells you how to change every one of the d
  parameters for the price of about one extra evaluation, while a loss value on its own tells you
  one number, and you have to guess the direction. Backpropagation is how networks with billions
  of parameters get the d-numbers-per-step deal. Evolution is what you fall back on when there is
  no derivative to take: lesson 12 uses it to mutate attack strings against a trained detector.""")

hc, gd = scaling["hill climber"], scaling["gradient descent"]
assert hc[-1] > 5 * hc[0], "hill-climber cost should grow with dimension"
assert gd[-1] <= gd[0], "gradient-descent cost should not grow with dimension"
assert xor_summary["genetic algorithm"][0] >= 8 and xor_summary["hill climber"][0] >= 8

# ----------------------------------------------------------------------- plots
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
for m, (curve, evals) in xor_curves.items():
    xs = np.linspace(evals / len(curve), evals, len(curve))         # spread the curve over the evaluations used
    axes[0].plot(xs, curve, label=m)
axes[0].axhline(TARGET_XOR, ls="--", c="gray", label="solved threshold")
axes[0].set(xscale="log", xlabel="loss evaluations", ylabel="best loss so far", title="A. XOR, 9 parameters, one start")
axes[0].legend()
for m in METHODS:
    axes[1].plot(DIMS, scaling[m], "o-", label=m)
axes[1].set(xscale="log", yscale="log", xlabel="number of features d", ylabel="median evaluations to solve",
            title="B. logistic regression: cost vs parameter count")
axes[1].legend()
print("plot:", save_plot(fig, os.path.join(HERE, "plots", "evolution.png")))
print("ok")
