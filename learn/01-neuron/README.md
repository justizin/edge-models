# 01: one neuron

## The idea

A neuron is a tiny calculator. It takes inputs `x1, x2, ...`, multiplies each by its own weight
`w1, w2, ...`, adds a bias `b`, and decides based on the total:

```
z = w1*x1 + w2*x2 + ... + b        (the weighted sum; written  z = w . x + b)
output = 1 if z > 0 else 0         (the step activation)
```

The weights say how much each input matters and in which direction; the bias shifts the threshold.
That is the whole model. A "neural network" is many of these, where outputs of some become inputs of
others. Everything hard in this field is about choosing the weights, which is called *training*.

## Hand-set weights

With two binary inputs, AND fires only when both are 1. The sum `x1 + x2` is 2 only then, so weights
`(1, 1)` and a bias of `-1.5` put the threshold between 1 and 2. OR needs the threshold between 0 and
1, so bias `-0.5`. A negative weight makes NOT. Looking at these three you can see that the neuron
is computing *one inequality*.

## The perceptron rule (1957)

Instead of setting weights by hand, start random and correct after each mistake:

```
err = target - output          +1 if it should have fired but did not, -1 the other way, 0 if right
w_i <- w_i + lr * err * x_i    only inputs that were on get adjusted (x_i = 0 changes nothing)
b   <- b   + lr * err
```

If the data can be separated by a line, this rule is guaranteed to find one eventually. Watch the
"mistakes per epoch" count fall to zero for AND and OR.

## Why XOR fails

`w1*x1 + w2*x2 + b > 0` is one side of a straight line in the input plane. AND and OR each have their
1s on one side of some line. XOR puts its 1s at (0,1) and (1,0) and its 0s at (0,0) and (1,1), on
opposite corners; no single line separates them. The script lets the rule run 200 epochs and it never
gets below 1 mistake. This observation (Minsky and Papert, 1969) stalled the field for a decade. The
fix, a *hidden layer* of neurons whose outputs feed a final neuron, is lesson 04.

## Run it

```
.venv/bin/python learn/01-neuron/neuron.py
.venv/bin/python learn/01-neuron/neuron_torch.py
```

In the torch twin, `torch.nn.Linear(2, 1)` is the same `z = w . x + b` with the weights stored in a
`1x2` matrix. A layer of `n` neurons is `Linear(inputs, n)`: the same sum done `n` times at once as a
matrix multiply, `z = X @ W.T + b`. Hold onto that; every layer in every later lesson is this line.

## Exercises

1. Change `seed=1` in `train_perceptron` to other values. Does the number of epochs change? Do the
   final weights? (Many different lines separate the same four points.)
2. Make the learning rate `lr=1.0` and then `lr=0.001`. For this rule the rate only scales the
   weights; why does convergence still happen? (Compare with lesson 02, where the rate matters a lot.)
3. Add a third input and teach the neuron the three-input majority function
   (fire when at least two of three inputs are 1). Then try three-input parity (odd number of 1s).
   Which one works, and why?

## Check yourself

Draw the four XOR points on paper. Draw the two lines you would need to separate them. Each line is
one neuron's `z = 0`. What would a third neuron have to compute from the two "which side am I on"
answers to produce XOR?
