"""Lesson 01: one neuron, no libraries.

A neuron takes some inputs, multiplies each by a weight, adds them up with a bias, and passes the
sum through an activation function. With a step activation this is the 1957 perceptron. That is the
whole thing; everything later is many of these, wired together, trained by better rules.

Run:  .venv/bin/python learn/01-neuron/neuron.py
"""
import random

# ---------------------------------------------------------------- the neuron

def step(z: float) -> int:
    """Activation: fire (1) if the weighted sum is positive, else stay quiet (0)."""
    return 1 if z > 0 else 0


def neuron(x, w, b) -> int:
    """x: inputs, w: one weight per input, b: bias. Returns the neuron's output, 0 or 1."""
    z = sum(xi * wi for xi, wi in zip(x, w)) + b     # the weighted sum, usually written  z = w . x + b
    return step(z)


INPUTS = [(0, 0), (0, 1), (1, 0), (1, 1)]            # every combination of two binary inputs
AND = [0, 0, 0, 1]
OR  = [0, 1, 1, 1]
XOR = [0, 1, 1, 0]


def show(name, w, b, targets=None):
    """Print the truth table a neuron with weights w and bias b produces."""
    outs = [neuron(x, w, b) for x in INPUTS]
    ok = "" if targets is None else ("  <- correct" if outs == targets else f"  <- wrong, wanted {targets}")
    print(f"  {name:<14} w={tuple(round(v, 2) for v in w)} b={b:+.2f}  outputs {outs}{ok}")
    return outs


# ------------------------------------------------- part 1: weights set by hand
print("Part 1: hand-set weights")
# AND: fire only when both inputs are 1. Sum of inputs is 2 only then, so threshold between 1 and 2.
#      w . x + b > 0  <=>  x1 + x2 > 1.5
assert show("AND by hand", (1.0, 1.0), -1.5, AND) == AND
# OR: fire when at least one input is 1. Threshold between 0 and 1.
assert show("OR by hand", (1.0, 1.0), -0.5, OR) == OR
# NOT (one input): negative weight flips the sense.
print(f"  {'NOT by hand':<14} outputs {[neuron((x,), (-1.0,), 0.5) for x in (0, 1)]}")


# ---------------------------------------- part 2: the perceptron learning rule
def train_perceptron(targets, lr=0.1, epochs=50, seed=1):
    """Rosenblatt's rule. For each example: if the neuron is wrong, nudge the weights toward
    making it right.  err = target - output  is +1 (fired too little), -1 (fired too much) or 0.
        w_i <- w_i + lr * err * x_i       only inputs that were 'on' get blamed
        b   <- b   + lr * err
    Returns (w, b, mistakes_per_epoch)."""
    rng = random.Random(seed)
    w = [rng.uniform(-1, 1), rng.uniform(-1, 1)]
    b = rng.uniform(-1, 1)
    history = []
    for _ in range(epochs):
        mistakes = 0
        for x, t in zip(INPUTS, targets):
            err = t - neuron(x, w, b)
            if err:
                mistakes += 1
                w = [wi + lr * err * xi for wi, xi in zip(w, x)]
                b = b + lr * err
        history.append(mistakes)
        if mistakes == 0:            # a full pass with no errors: done
            break
    return w, b, history


print("\nPart 2: learning the weights with the perceptron rule")
for name, targets in (("AND", AND), ("OR", OR)):
    w, b, hist = train_perceptron(targets)
    print(f"  {name}: converged after {len(hist)} epochs, mistakes per epoch {hist}")
    assert show(f"{name} learned", w, b, targets) == targets


# ------------------------------------------------- part 3: XOR cannot be done
print("\nPart 3: XOR")
w, b, hist = train_perceptron(XOR, epochs=200)
show("XOR attempt", w, b, XOR)
print(f"  mistakes per epoch never reach 0 (last 10 epochs: {hist[-10:]})")
assert min(hist) > 0, "a single neuron must not be able to learn XOR"

print("""
  Why: the neuron fires when  w1*x1 + w2*x2 + b > 0.  That inequality describes one side of a
  straight line in the (x1, x2) plane. AND and OR each need one line separating the 1s from the 0s.
  XOR wants (0,1) and (1,0) on the 'fire' side and (0,0) and (1,1) on the other:

        x2
        1 |  1    0          no single straight line puts the two 1s
          |                  on one side and the two 0s on the other.
        0 |  0    1
          +---------- x1
             0    1

  Fixing this needs more than one line, which means more than one neuron. That is lesson 04.""")
print("\nok")
