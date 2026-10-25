# 06: evolution instead of gradients (and where genetic programming fits)

## The idea

Lessons 02 to 04 trained by computing a derivative and stepping against it. That is one way to
search for good weights. Another is to never compute anything *about* the loss, only evaluate it,
and let selection do the work:

1. start with a population of random weight vectors;
2. score each by the loss;
3. keep the better ones; make children by **crossover** (mix two parents' genes) and **mutation**
   (add random noise to some genes);
4. repeat.

Applied to a neural network's weights this is **neuroevolution**. The script runs it on the exact
XOR network from lesson 04 (nine numbers in a flat vector) and on logistic regression from lesson
03 with a growing number of features, comparing three optimizers:

- **gradient descent**, lesson 04's backward pass (one step is counted as three loss evaluations,
  since a backward pass costs about two forwards; this is generous to evolution);
- a **hill climber**, the smallest thing that is still evolution: one individual, mutate it, keep
  the child if it is not worse;
- a **genetic algorithm** with a population of 60, tournament selection, uniform crossover,
  Gaussian mutation, and two elites carried over unchanged.

## The relationship to genetic programming

Three things people confuse:

- **Genetic algorithm (GA)**: evolve a fixed-length vector of numbers. Here: the nine weights.
- **Neuroevolution**: a GA (or relative) whose vector is a network's weights, sometimes also its
  wiring. NEAT, for instance, evolves the topology (which neurons connect to which) and the weights
  together, starting from a minimal network and adding structure through mutation.
- **Genetic programming (GP)**: evolve a *program*, usually a tree of operations (`+`, `*`, `if`,
  `sin`, inputs, constants). Crossover swaps subtrees between parents; mutation replaces a subtree.
  The result is a formula or a small program, not a weight vector. GP can discover the shape of the
  function; a neural network fixes the shape (layers of weighted sums and activations) and only
  tunes numbers.

So: GA and GP are two instances of the same evolutionary loop applied to different representations,
and a neural network can be the thing either loop is applied to. Gradient descent is a different
search method entirely, which is far more efficient *when a derivative exists* and the problem is
big enough for that to matter. The script shows both halves of that sentence.

## What the experiments show

**A. XOR, 9 parameters.** No clear winner. Over 20 random starts the hill climber solves as many
as gradient descent and uses *fewer* evaluations (a few hundred against a couple of thousand). A
random nudge to 9 numbers has a decent chance of pointing somewhere useful. All methods get stuck on
roughly the same starts: the flat regions from lesson 04 belong to the loss surface, and a
population explores them only a little better than a single point does. The GA is the most
expensive because it pays for 60 individuals every generation.

**B. Logistic regression with d = 4, 16, 64, 256 features.** Read across the rows:

- gradient descent's cost does not grow with d (it falls, because more features make the two
  classes easier to separate);
- the hill climber's cost grows roughly in proportion to d: the probability that a random
  perturbation of d numbers is a useful direction shrinks as d grows, so it needs more tries per
  productive step;
- the GA sits in between, its floor set by the population cost.

One sentence to keep: *a gradient tells you how to move all d parameters for roughly the price of
one extra evaluation; a loss value tells you one number and you must guess the direction.*
Backpropagation is how networks with billions of parameters get that deal, and it is why weight
training in modern deep learning is almost never evolutionary.

## When evolution is still the right tool

When there is no derivative to take. The objective is a black box: the win rate of a game-playing
agent, the reward of a robot, the latency of a compiled kernel, whether a crafted input slips past a
detector. Exercise 2 makes the loss non-differentiable and watches gradient descent lose its
footing while the GA carries on. Lesson 12 uses this loop to mutate SQL-injection strings against a
trained classifier, where "the gradient with respect to the input string" does not exist.
Architecture search and parts of reinforcement learning use evolution for the same reason.

There is no torch twin for this lesson. Autograd has nothing to contribute: the loss is only ever
called, never differentiated.

## Run it

```
.venv/bin/python learn/06-evolution/evolution.py        # writes plots/evolution.png; about half a minute
```

The left panel plots best-loss-so-far against evaluations used for one XOR start. The right panel
is the scaling table on log axes: a flat line is "cost independent of parameter count", a rising
line is "cost grows with it".

## Exercises

1. Change the mutation `sigma` for XOR (0.1, 0.5, 2.0) and the GA's `pop_size` (10, 60, 300). Which
   finds a solution in the fewest evaluations? Which never does?
2. Replace `xor_loss_batch` with the number of wrong answers, `np.sum((p > 0.5) != Y_XOR, axis=-1)`.
   Gradient descent is now meaningless (the function is flat with jumps, so `xor_grad` no longer
   matches it). Does the hill climber still solve it? What does its curve look like?
3. Turn off crossover (`children = parent_a.copy()` before mutation). How much does the GA lose?
4. Extend `DIMS` to 1024. Does the hill climber's line keep its slope? How long do you wait?
5. Evolve the architecture: add a gene that selects `H` in {1, 2, 3, 4} and resize the unpacking
   accordingly (pad the vector to the largest size). What `H` does evolution settle on?
6. Harder: write a tiny GP. Represent a formula as nested tuples such as
   `("+", ("*", "x1", "x2"), "x2")`, evaluate it on the four XOR inputs, evolve with subtree
   mutation and crossover, fitness = squared error. Can it find XOR as a formula?

## Check yourself

Both families minimise the same loss on the same parameters. Why does one need the loss to be
smooth and the other does not? What information does a gradient carry that a loss value alone does
not, and why does that advantage grow with the number of parameters?
