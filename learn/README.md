# Learning track: neural networks from one neuron to network security

A hands-on course that lives next to the benchmarks. Each lesson is a directory with a `README.md`
(the idea, the math written out once, what to run, what to look for, exercises), a numpy or stdlib
script where every operation is explicit, and a `*_torch.py` twin that builds the same model with
PyTorch and asserts it produces the same numbers. Autograd stops being magic when you have seen it
agree with gradients you derived by hand.

Everything runs on CPU in seconds. Plots are written as PNGs into each lesson's `plots/` directory,
and loss curves are also drawn in the terminal so the lessons work over SSH.

## Setup

From the repo root (same venv as the benchmarks):

```
~/.local/bin/uv pip install --python .venv/bin/python numpy scikit-learn matplotlib
~/.local/bin/uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu
.venv/bin/python learn/00-check/check.py
```

`learn/run_all.sh` runs every lesson; each script ends with assertions, so it doubles as the test suite.

## How to work a lesson

1. Read the lesson README up to "Run it".
2. Run the plain script and read its output alongside the code. Each script is meant to be read top to
   bottom; the comments carry the explanation.
3. Run the torch twin. It prints the same numbers and asserts they match.
4. Do the exercises: each one is a small edit to the script. Breaking things is the point.
5. Answer the check question for yourself before moving on.

## Lessons

| # | lesson | what you learn | status |
|---|---|---|---|
| 01 | [`01-neuron`](01-neuron/) | a neuron is a weighted sum and a threshold; the perceptron rule; why one neuron cannot do XOR | batch 1 |
| 02 | [`02-gradient`](02-gradient/) | loss as a function of the weights; derivatives; gradient descent; the learning rate | batch 1 |
| 03 | [`03-logistic`](03-logistic/) | sigmoid and cross-entropy; a neuron as a probabilistic classifier; first autograd twin | batch 1 |
| 04 | [`04-xor`](04-xor/) | a hidden layer; backpropagation derived by hand; gradient checking; autograd agrees | batch 1 |
| 05 | `05-mlp` | a reusable multi-layer network; train/test split, overfitting, batches, ReLU, init | batch 2 |
| 06 | [`06-evolution`](06-evolution/) | training the XOR net with a genetic algorithm instead; how that relates to genetic programming | batch 1 |
| 07 | `07-log-triage` | bag-of-tokens features on the IDS log set; an MLP beside the rules and naive Bayes baselines | batch 2 |
| 08 | `08-dga-domains` | malicious-domain detection: hand features, then a character-level model that learns them | batch 2 |
| 09 | `09-sqli` | SQL-injection detection on query strings with encoding variants | batch 2 |
| 10 | `10-flow-ids` | NSL-KDD flow features: MLP vs logistic regression vs random forest, per-attack confusion | batch 3 |
| 11 | `11-pcap-features` | tshark flow extraction from your own captures, fed to the lesson-10 model | batch 3 |
| 12 | `12-adversarial` | gradient attacks on the flow model, string mutations on the SQLi model, adversarial training | batch 4 |
| 13 | `13-passwords` | character models of leaked-password patterns as a strength estimator and guesser | batch 4 |
| 14 | `14-anomaly` | autoencoder anomaly detection (fuzzing detection, pending a definition) | batch 4 |

## Glossary (grows with the lessons)

- **weight**: a number multiplied with an input. **bias**: a number added after the sum. Together they are the *parameters* the training changes.
- **activation**: the function applied to the weighted sum (step, sigmoid, tanh, ReLU). Without one, stacking layers is still just one linear map.
- **loss**: a single number saying how wrong the network is on the data. Training is minimizing it.
- **gradient**: the vector of partial derivatives of the loss with respect to every parameter. It points uphill; we step the other way.
- **learning rate**: how far to step. Too small is slow, too large diverges.
- **epoch**: one pass over the training data. **batch**: the subset used for one update.
- **backpropagation**: the chain rule applied layer by layer from the loss back to the inputs, reusing intermediate results.
- **autograd**: PyTorch recording every operation on a tensor so it can run backpropagation for you.
