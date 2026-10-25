# 04: a hidden layer, and backpropagation

## The idea

One neuron draws one line. XOR needs two. So use two neurons side by side, each drawing its own
line, and hand their two outputs to a third neuron. The third neuron no longer sees `(x1, x2)`; it
sees `(h1, h2)`, "which side of line 1, which side of line 2". In that new space the four XOR points
can be separated by one line, which is all the third neuron can do, and that is enough.

```
x (2 inputs)  --W1, b1-->  z1  --sigmoid-->  h (H hidden units)  --W2, b2-->  z2  --sigmoid-->  p
```

The middle pair is a **hidden layer**: hidden because nothing in the data tells it what to compute.
Training has to discover useful lines on its own, driven only by the loss at the output. Run the
script and read the hidden-unit lines it prints. In the shipped run, one unit learned roughly
"x1 AND x2", the other roughly "NOT (x1 OR x2)", and the output fires when neither does. That is
XOR, built from pieces, found by gradient descent and never spelled out.

## Backpropagation, once

Lesson 03 gave the output layer's gradient. The new question is: how does the loss depend on `W1`,
which sits two steps away from it? The chain rule, applied one layer at a time, working backwards.
`d<thing>` means `dL/d<thing>` and has the same shape as the thing.

```
output layer, identical to lesson 03 with h in place of x:
    dz2 = (p - y) / N
    dW2 = h.T @ dz2
    db2 = sum(dz2)

pass the gradient back through W2:
    dh  = dz2 @ W2.T              how much the loss cares about each hidden value

pass it back through the sigmoid:
    dz1 = dh * h * (1 - h)        multiply by the sigmoid's derivative (lesson 03's bump)

hidden layer, lesson 03 again with dz1 in the role of (p - y):
    dW1 = X.T @ dz1
    db1 = sum(dz1, axis=0)
```

Two patterns are worth memorizing because they are the entire backward pass of any depth:

- a layer's weight gradient is `(its input).T @ (gradient at its output)`;
- the gradient passes backward through a layer as `(gradient) @ W.T`, then through the activation
  as `* activation'(z)`.

"Backpropagation" is nothing more than doing this from the last layer to the first, reusing the
values saved during the forward pass. Autograd (the torch twin) does the same bookkeeping
automatically, and the twin asserts its nine gradients match this derivation to 1e-12.

## Gradient checking

The script nudges each of the nine parameters by `1e-6`, measures the loss change, and compares
with the backward pass. When you write your own backward pass, this is the test that catches the
missing transpose or the forgotten sigmoid derivative. Always run it once at a random point before
trusting a training run.

## Why some seeds get stuck

With only two hidden units and sigmoid activations, some random starts land in a region where the
loss surface is nearly flat (both hidden units computing about the same thing, or saturated at 0 or
1 where the sigmoid's derivative is tiny). Gradient descent crawls there. The script's seed is one
that works; with `H = 2` roughly a third of seeds do not within 5000 steps, with `H = 4` almost all
do. This is the first appearance of three recurring facts: initialization matters, extra capacity
makes optimization easier even when it is not needed to represent the answer, and sigmoids in
hidden layers kill gradients (ReLU, in lesson 05, is the fix).

## Run it

```
.venv/bin/python learn/04-xor/xor.py                # writes plots/xor.png
.venv/bin/python learn/04-xor/xor_torch.py
```

The plot's left panel is the input plane: the network's output as colour, the `p = 0.5` boundary in
black, and each hidden unit's `z1 = 0` line dashed. The middle panel is the hidden space: where the
hidden layer moves the whole input plane (the faint dots) and the four XOR points, now separable by
the output neuron's single line. The right panel is the loss.

The torch twin copies the exact initial weights, compares every gradient, trains, and then shows the
usual spelling: `nn.Sequential(Linear, Sigmoid, Linear, Sigmoid)`. Note that `nn.Linear` stores its
weight transposed, `(out, in)`, which is why the twin loads `W1.T`.

## Exercises

1. Set `H = 1`. Confirm it cannot learn XOR, no matter the seed. Then `H = 4`: faster or slower?
2. Change `SEED` until you find a stuck run. Print the hidden activations: are the two units doing
   the same thing, or is one saturated near 0 or 1 for every input? Relate that to the sigmoid's
   derivative in lesson 03's plot.
3. Replace the hidden sigmoid with `tanh` (and its derivative `1 - h^2` in `backward`). Rerun the
   gradient check first. Does it get stuck less often?
4. Deliberately break `backward` (drop the `* h * (1 - h)` factor). The gradient check should fail.
   Does training still sometimes "work"? That is why the check exists.
5. Add a second hidden layer. You need one more application of the two patterns above. Gradient
   check it.

## Check yourself

The output neuron is lesson 03 applied to `h`. The hidden neurons are lesson 03 applied to `x`,
except their gradient arrives from above instead of from a label. Where in the code does the
"label" for a hidden unit come from, and what would happen to `dW1` if `W2` were all zeros?
