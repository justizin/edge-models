# 02: gradient descent

## The idea

The perceptron rule from lesson 01 only applies to a step output on separable data. Modern training
is built on a more general idea with three parts:

1. **A loss**: one number that measures how wrong the model is on the data. Smaller is better.
2. **The gradient**: for each parameter, the derivative of the loss with respect to it. It says
   "if I increase this parameter a tiny bit, the loss changes by this much". The vector of all of
   them points in the direction of steepest increase.
3. **The step**: move every parameter a little in the *opposite* direction of its derivative.
   `w <- w - lr * dL/dw`. The learning rate `lr` sets how far.

Repeat until the loss stops falling. The model here is a line `y = w*x + b`, with only two
parameters, so the loss surface can be drawn and you can see what the algorithm is doing.

## The math, once

Mean squared error on `N` points:

```
L(w, b) = (1/N) * sum_i (w*x_i + b - y_i)^2
```

Call the error on point i `e_i = w*x_i + b - y_i`. Differentiating `e_i^2` gives `2*e_i` times the
derivative of `e_i`, which is `x_i` for `w` and `1` for `b`:

```
dL/dw = (1/N) * sum_i 2*e_i*x_i
dL/db = (1/N) * sum_i 2*e_i
```

The script checks these formulas against a *numerical* derivative: nudge the parameter by a tiny
`h`, measure how much the loss moved, divide. That check is called gradient checking, and it is how
you will verify every hand-written backward pass later. If the two disagree, the formula is wrong.

## The learning rate

Three runs, same start, different step sizes:

- too small: `w` is found quickly but `b` crawls. The bowl is elongated: steep along `w` (because `x`
  is large, `w` has a big effect) and shallow along `b`. One step size has to serve both directions.
- right: it settles near the true line within a hundred steps.
- too large: each step overshoots the bottom of the bowl and lands higher on the other side; the
  loss grows without bound. The script stops that run when the loss passes a million.

For a bowl-shaped loss the critical value is about `1 / curvature`. Here the curvature in `w` is
`2 * mean(x^2)`, roughly 67, so rates above about 0.03 diverge. You almost never compute this in
practice, but it explains why normalizing inputs to a small range (lesson 05) makes training easier:
it shrinks the curvature so a comfortable learning rate works.

## Run it

```
.venv/bin/python learn/02-gradient/gradient.py            # writes plots/gradient.png
.venv/bin/python learn/02-gradient/gradient_torch.py
```

The terminal shows each loss curve as a sparkline. The PNG has the loss bowl with its slope, the
three curves on a log scale, and the fitted line over the data.

The torch twin introduces autograd. `requires_grad=True` tells PyTorch to record every operation
applied to a tensor; `loss.backward()` runs the chain rule backwards through that record and leaves
`dL/dw` in `w.grad`. The script asserts those numbers equal the formula to nine decimals, then runs
the same 2000 training steps both ways and asserts the final `w, b` are identical. Two things to
remember from it: the update must happen inside `torch.no_grad()` (it is not part of the model), and
`.grad` accumulates, so it must be zeroed every step. `torch.optim.SGD` is nothing more than those
two lines wrapped up for a list of parameters.

## Exercises

1. Change the noise from `2.0` to `0.0` and to `10.0`. What happens to the loss at the true line, and
   to the fitted values? The loss cannot go below the noise; that floor is what "irreducible error"
   means.
2. Find the learning rate where lr=0.04's behaviour starts: try 0.025, 0.03, 0.035. Compare with the
   `1/mean(x^2)` number the script prints.
3. Divide `x` by 10 before everything else (so it lies in [0, 1]). Rerun the sweep. Which rates work
   now, and why did the answer change?
4. Replace the squared error with absolute error `|e|`. Derive the gradient (hint: the derivative of
   `|e|` is the sign of `e`). Does the numerical check still agree? What happens near `e = 0`?

## Check yourself

Why do we step against the gradient rather than, say, toward the parameter values that the data
"obviously" wants? For a line you could solve for `w, b` directly with a formula. Why does that stop
being possible once there is a hidden layer (lesson 04)?
