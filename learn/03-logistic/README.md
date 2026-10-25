# 03: a neuron that outputs a probability

## The idea

Lesson 01's step function cannot be trained by gradient descent: its slope is zero everywhere
except at the jump, so the gradient carries no information. Swap it for the **sigmoid**, a smooth
S-curve from 0 to 1:

```
sigmoid(z) = 1 / (1 + e^(-z))
```

Now the neuron's output is a number in (0, 1) that we read as "probability of class 1". Combine it
with a loss made for probabilities and lesson 02's recipe trains a classifier. A single sigmoid
neuron is called **logistic regression**. It is sixty years old and still the first thing to try on a
security classification problem, because it is fast, stable, and you can read the weights.

The toy data: for each source host, failed logins per minute and distinct usernames tried. Normal
hosts have small values of both; a brute-forcer has large values of both.

## Standardizing inputs

Before training, each feature is shifted to mean 0 and scaled to standard deviation 1. Lesson 02
showed why: large inputs make the loss steep in that weight's direction and force a tiny learning
rate. Standardized inputs also make the learned weights comparable with each other. Every later
lesson does this (or an equivalent) to its inputs; forgetting it is the most common reason a small
network "does not train".

## The loss: binary cross-entropy

```
L = -(1/N) * sum_i [ y_i * log(p_i) + (1 - y_i) * log(1 - p_i) ]
```

For a point whose truth is 1 only the first term survives: `-log(p)`, near 0 when `p` is near 1,
huge when `p` is near 0. For truth 0 the mirror image. Confident and right costs nothing; confident
and wrong costs a lot. At the start (`w = 0`, every `p = 0.5`) the loss is `-log(0.5) = 0.693`,
the loss of pure guessing. Any run should get well below that number.

## The gradient, once

Chain rule from the loss back to the weights for one point, then average:

```
dL/dp = -y/p + (1-y)/(1-p)
dp/dz = p * (1 - p)                  the sigmoid's derivative
dL/dz = dL/dp * dp/dz = p - y        the two fractions cancel into this. Check it by hand once.
dz/dw = x,  dz/db = 1

dL/dw = mean_i (p_i - y_i) * x_i
dL/db = mean_i (p_i - y_i)
```

`p - y` is the signed error: positive when the model said "attack" too strongly, negative when too
weakly. The update pushes the weights of the inputs that were on in the direction that fixes it.
Compare with lesson 01's perceptron rule: same shape, but `p - y` is a graded quantity instead of
-1/0/+1, and the loss it descends is a smooth surface. The script checks this formula against the
numerical derivative before using it.

## Run it

```
.venv/bin/python learn/03-logistic/logistic.py           # writes plots/logistic.png
.venv/bin/python learn/03-logistic/logistic_torch.py
```

Read the "probability of brute force" lines at the end. The output is a probability, so the alert
threshold is a policy choice you make after training, not something baked into the model: a SOC
that is drowning in alerts moves it up; one that cannot afford a miss moves it down.

The plot shows the sigmoid beside the step (and the sigmoid's derivative, a bump that vanishes in
both tails, which matters in lesson 04), the data with the probability map and the `p = 0.5` line,
and the loss curve.

The torch twin does three things: checks autograd against the `(p - y) x` formula at the start,
trains with the hand-written loop and asserts the final weights equal the numpy ones, then trains
again the way PyTorch code is usually written, `nn.Linear` plus `BCEWithLogitsLoss` plus an
optimizer. `BCEWithLogitsLoss` takes `z` before the sigmoid and fuses sigmoid and log into one
numerically safe operation; it is the form you will see in real code.

## Exercises

1. Move the attack cluster closer: `loc=[4.0, 3.0]`. Watch accuracy drop and the loss floor rise.
   The model is not failing; the classes overlap and no line separates them. What does the
   probability map look like in the overlap?
2. Remove the standardization (use `X = X_raw`). Find a learning rate that still trains. How many
   steps does it need now?
3. Add a third, useless feature: a column of random noise. What weight does it get? Add a fourth
   that is an exact copy of the first. What happens to the two weights?
4. Print the loss *per point* and find the five points the model is most wrong about. Where are
   they on the plot?

## Check yourself

The decision boundary is still a straight line, exactly as in lesson 01. What did the sigmoid buy
us, then? (Two things: a trainable gradient, and a calibrated score instead of a yes/no.)
