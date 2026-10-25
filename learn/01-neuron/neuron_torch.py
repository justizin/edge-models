"""Lesson 01, torch twin: the same neuron as a PyTorch layer.

`torch.nn.Linear(2, 1)` is exactly  z = w . x + b  for 2 inputs and 1 output. A "layer" of n neurons
is Linear(inputs, n): the same thing done n times at once as a matrix multiply. There is nothing to
learn with autograd here (the perceptron rule is not a gradient step), so this twin only shows that
the hand-set AND/OR weights produce the same truth tables when loaded into a Linear layer.

Run:  .venv/bin/python learn/01-neuron/neuron_torch.py
"""
import torch

INPUTS = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])     # 4 examples x 2 inputs
AND = [0, 0, 0, 1]
OR = [0, 1, 1, 1]

layer = torch.nn.Linear(2, 1)          # holds layer.weight (shape 1x2) and layer.bias (shape 1)
print("fresh Linear(2,1) has random weights:", layer.weight.data.tolist(), layer.bias.data.tolist())

for name, w, b, want in (("AND", (1.0, 1.0), -1.5, AND), ("OR", (1.0, 1.0), -0.5, OR)):
    with torch.no_grad():               # we are setting weights by hand, not training
        layer.weight[:] = torch.tensor([w])
        layer.bias[:] = torch.tensor([b])
    z = layer(INPUTS)                   # all four weighted sums at once, shape 4x1
    out = (z > 0).int().flatten().tolist()   # the step activation
    print(f"  {name}: z={z.flatten().tolist()} -> outputs {out}")
    assert out == want, (name, out, want)

# The matrix form, written out so Linear is not a black box:  z = X @ W^T + b
with torch.no_grad():
    manual = INPUTS @ layer.weight.T + layer.bias
    assert torch.allclose(manual, layer(INPUTS))
print("  Linear(x) == x @ W.T + b  confirmed")
print("ok")
