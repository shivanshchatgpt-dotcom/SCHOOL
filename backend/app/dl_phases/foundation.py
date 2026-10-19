"""Deep Learning foundations, days 9-14: the maths in plain Python, no frameworks.

Every example is stdlib-only, offline and deterministic (fixed weights or a
seeded `random.Random`, rounded outputs), so the applier can execute it and
produce the same result on every run. The domain phases keep the same discipline:
a tensor is a list, a layer is a function, a loss is a number, and a gradient is
something you can check against a finite difference before trusting it.
"""

FOUNDATION = {
    9: dict(
        topic="A neuron from scratch",
        idea=(
            "A neuron is a weighted sum followed by a non-linearity, and writing it in plain Python removes the "
            "mystery that framework calls create. Given some inputs and a matching list of weights, you multiply "
            "each input by its weight, add a bias, and pass the total through a simple function such as ReLU, "
            "which returns the value if it is positive and zero otherwise. That is the whole unit. The reason to "
            "build it by hand first is that every later topic — layers, forward passes, losses, gradients — is "
            "this same computation repeated and composed, and doing it once with loops makes the tensor shapes "
            "and the arithmetic concrete. You also see immediately why the non-linearity matters: without it, "
            "stacking neurons would collapse into a single linear function, and the network could not learn "
            "anything a line could not express. Today you write a `neuron` function and run it on a few inputs, "
            "including one that produces a negative pre-activation so the ReLU clamps it to zero. Keep numbers "
            "small and round them when printing, because raw floating point tails obscure the idea rather than "
            "explaining it."
        ),
        code=(
            'def relu(x):\n'
            '    return x if x > 0 else 0.0\n'
            '\n'
            'def neuron(inputs, weights, bias):\n'
            '    total = bias\n'
            '    for value, weight in zip(inputs, weights):\n'
            '        total += value * weight\n'
            '    return relu(round(total, 4))\n'
            '\n'
            'print("case A:", neuron([1.0, 2.0], [0.5, 0.5], 0.0))\n'
            'print("case B:", neuron([1.0, 2.0], [-1.0, 0.5], 0.0))\n'
            '\n'
            'assert neuron([1.0, 2.0], [0.5, 0.5], 0.0) == 1.5\n'
            'assert neuron([1.0, 2.0], [-1.0, 0.5], 0.0) == 0.0\n'
            'print("a neuron is a weighted sum plus a non-linearity")'
        ),
        variant_b='add a sigmoid activation and print both outputs for the same two cases',
        variant_c='remove the non-linearity and show that a negative pre-activation is no longer clamped',
        mistakes=[
            "Forgetting the non-linearity, so the unit is linear and stacking adds no expressive power.",
            "Zipping inputs and weights of different lengths, silently dropping values instead of raising.",
            "Printing raw floating point results that hide the arithmetic behind long tails.",
        ],
        q1=(
            "Why does a non-linearity like ReLU matter in a neuron?",
            "Without it a stack of neurons is still one linear function, so the network cannot represent curved relationships.",
        ),
        homework=(
            "Write `neuron(inputs, weights, bias)` that returns a ReLU of the weighted sum, plus `relu(x)`. Test "
            "it with two inputs and two weight sets so one case fires and one clamps to zero, print both, and "
            "comment which line performs the non-linearity."
        ),
        patterns=["def ", "zip", "print("],
        mapping=(
            "PyTorch's `nn.Linear` plus `F.relu` is exactly this, vectorised and differentiable; doing it by "
            "hand is how you debug shapes and activations later."
        ),
    ),
    10: dict(
        topic="Vectors, dot products and matrices",
        idea=(
            "Everything a deep learning framework calls a tensor is, at the level of this course, a nested list. "
            "A vector is a list of numbers, a matrix is a list of vectors, and the two operations that carry the "
            "work are the dot product and matrix multiplication. The dot product pairs up two equal-length "
            "vectors and sums the products, which is exactly the weighted sum inside a neuron. Matrix "
            "multiplication applies that dot product for every row-and-column pair, which is how a whole layer "
            "computes many neurons at once. Getting the shape rule straight here saves hours later: the number "
            "of columns on the left must equal the number of rows on the right, and the result has the left's "
            "rows and the right's columns. That single rule explains most shape errors in real frameworks. Today "
            "you implement a dot product and a small matrix multiply with loops, then check both against a "
            "hand-computed result. Keep values small integers so the arithmetic is checkable and the printed "
            "output is exact, because the goal is to see the rule, not to test floating point."
        ),
        code=(
            'def dot(a, b):\n'
            '    return sum(x * y for x, y in zip(a, b))\n'
            '\n'
            'def matmul(a, b):\n'
            '    columns = list(zip(*b))\n'
            '    return [[dot(row, col) for col in columns] for row in a]\n'
            '\n'
            'w = [[1, 2], [3, 4], [5, 6]]\n'
            'x = [[1], [1]]\n'
            'result = matmul(w, x)\n'
            'print("dot:", dot([1, 2, 3], [4, 5, 6]))\n'
            'print("matmul:", result)\n'
            '\n'
            'assert dot([1, 2, 3], [4, 5, 6]) == 32\n'
            'assert result == [[3], [7], [11]]\n'
            'print("a layer is a matrix multiply over a batch of vectors")'
        ),
        variant_b='multiply the same weights by a batch of two input columns and print the 3x2 result',
        variant_c='try a mismatched shape and explain which dimension breaks the columns-equals-rows rule',
        mistakes=[
            "Mixing up rows and columns so the shapes do not line up, then debugging the numbers instead of the shape.",
            "Zipping vectors of unequal length, truncating silently rather than raising an error.",
            "Transposing the wrong operand, which produces plausible-looking but wrong results.",
        ],
        q1=(
            "What shape rule must hold for two matrices to multiply?",
            "The left matrix's column count must equal the right matrix's row count; the result takes the left's rows and the right's columns.",
        ),
        homework=(
            "Write `matmul(a, b)` for lists of lists plus a `dot(a, b)` helper. Multiply a 2x3 weight matrix by "
            "a 3x1 input, print the result, and comment which line enforces that the inner dimensions agree."
        ),
        patterns=["def ", "zip", "print("],
        mapping=(
            "`torch.matmul` and `numpy.dot` implement exactly this; the shape rule and the transpose traps are "
            "identical at scale."
        ),
    ),
    11: dict(
        topic="A layer as a function",
        idea=(
            "A layer is a reusable function that maps a batch of inputs to a batch of outputs using fixed "
            "parameters, and separating parameters from computation is the design decision that makes training "
            "possible. The layer should not care where its weights came from; it takes weights and a bias, plus "
            "some inputs, and returns outputs. That means the same function works during training and inference, "
            "and it means you can swap the parameters to test hypotheses without rewriting the layer. The batch "
            "axis is the other idea worth fixing now: instead of one vector at a time, the layer receives a list "
            "of vectors and returns a list of results, one per input row. Batching is not just for speed; it "
            "makes the maths uniform and the code shorter, and every framework is built around it. Today you "
            "write a `dense` layer that applies a weight matrix and a bias vector to a batch of inputs, with a "
            "short loop for the bias, and print the outputs. Keeping the batch explicit in the code, rather than "
            "hidden inside a library, is what lets you follow the shapes when the models get deeper."
        ),
        code=(
            'def dense(batch, weights, bias, activation):\n'
            '    outputs = []\n'
            '    for row in batch:\n'
            '        pre = [sum(v * w for v, w in zip(row, w_row)) + b for w_row, b in zip(weights, bias)]\n'
            '        outputs.append([activation(v) for v in pre])\n'
            '    return outputs\n'
            '\n'
            'relu = lambda x: x if x > 0 else 0.0\n'
            'weights = [[1.0, -1.0], [0.5, 0.5]]\n'
            'bias = [0.0, 1.0]\n'
            'batch = [[1.0, 1.0], [2.0, 0.0]]\n'
            '\n'
            'out = dense(batch, weights, bias, relu)\n'
            'for row, result in zip(batch, out):\n'
            '    print(row, "->", result)\n'
            '\n'
            'assert out[0] == [0.0, 2.0]\n'
            'print("the layer maps a batch, one row at a time")'
        ),
        variant_b='swap the activation to identity and print how the negative entry is no longer clamped',
        variant_c='add a second dense layer chained after the first and print the intermediate and final output',
        mistakes=[
            "Adding the bias to the batch instead of to each output unit.",
            "Hard-coding weights inside the layer so there is nothing to train or swap.",
            "Processing one row at a time at call sites, so the batch axis disappears from the design.",
        ],
        q1=(
            "Why should a layer take its weights as arguments instead of defining them internally?",
            "Parameters then become trainable data that can be updated, saved and swapped without changing the layer's code.",
        ),
        homework=(
            "Write `dense(batch, weights, bias, activation)` returning one output row per input row. Run a "
            "two-row batch through a 2x2 weight matrix with a ReLU, print each row's output, and comment which "
            "line adds the bias per unit."
        ),
        patterns=["def ", "for ", "print("],
        mapping=(
            "An `nn.Linear` in PyTorch is this function with parameters as tensors; keeping parameters separate "
            "from the forward computation is the same split optimisers rely on."
        ),
    ),
    12: dict(
        topic="Loss tells you how wrong you are",
        idea=(
            "Training needs a single number that says how bad the current predictions are, because you can only "
            "improve what you can measure. Mean squared error is the simplest such number: subtract each "
            "prediction from its target, square the difference, and average. Squaring removes the sign so errors "
            "cannot cancel, and it punishes large mistakes more than small ones, which is usually the behaviour "
            "you want. Two habits make loss trustworthy. First, define it over the whole batch, not one example, "
            "so the number does not jump around with batch size. Second, write it as a small pure function so you "
            "can test it on known inputs: a perfect prediction must give exactly zero. That zero check catches "
            "sign errors and off-by-one slicing, which are the most common loss bugs. Today you implement mean "
            "squared error and check it against a hand-computed case, then compare a good and a bad prediction. "
            "Notice that the loss itself does not tell you how to change the weights; that is the gradient's job. "
            "But the loss defines the direction of 'better', so it must be right before any optimisation makes "
            "sense."
        ),
        code=(
            'def mse(predictions, targets):\n'
            '    total = 0.0\n'
            '    for pred, target in zip(predictions, targets):\n'
            '        total += (pred - target) ** 2\n'
            '    return round(total / len(predictions), 4)\n'
            '\n'
            'targets = [1.0, 2.0, 3.0]\n'
            'good = [1.0, 2.0, 3.0]\n'
            'bad = [1.0, 2.0, 0.0]\n'
            '\n'
            'print("perfect:", mse(good, targets))\n'
            'print("bad:", mse(bad, targets))\n'
            '\n'
            'assert mse(good, targets) == 0.0\n'
            'assert mse([0.0, 0.0], [1.0, 0.0]) == 0.5\n'
            'print("loss turns predictions into one comparable number")'
        ),
        variant_b='implement mean absolute error and compare the two losses on the bad prediction',
        variant_c='show that making one error twice as large more than doubles the squared loss',
        mistakes=[
            "Forgetting to square, so positive and negative errors cancel to a misleadingly small loss.",
            "Dividing by the wrong count, making loss depend on batch size and confusing comparisons.",
            "Comparing losses computed on different target scalings as if the numbers were directly comparable.",
        ],
        q1=(
            "Why does squaring the errors stop them from cancelling out?",
            "Squaring makes every difference non-negative, so opposite-sign errors add instead of cancelling.",
        ),
        homework=(
            "Write `mse(predictions, targets)` and `mae(predictions, targets)`. Evaluate both on a perfect "
            "prediction and a wrong one, print all four numbers, and comment which line guarantees a perfect "
            "prediction scores zero."
        ),
        patterns=["def ", "return", "print("],
        mapping=(
            "`torch.nn.MSELoss` and `CrossEntropyLoss` are these functions with numerical care added; choosing "
            "and checking a loss is the first thing to verify when a model will not learn."
        ),
    ),
    13: dict(
        topic="Gradient descent on one weight",
        idea=(
            "A gradient answers a narrow, practical question: if I nudge this weight up a little, does the loss "
            "go up or down, and by roughly how much? Once you know that, you move the weight in the opposite "
            "direction of the gradient to reduce the loss, scaled by a learning rate. You can compute a gradient "
            "analytically for a simple loss, and, crucially, you can check it numerically by evaluating the loss "
            "at w+e and w-e and dividing the difference by 2e. That finite-difference check is the single most "
            "useful debugging tool in deep learning, because it catches the sign and factor mistakes that make "
            "training silently fail. Start with a loss that has an obvious minimum, such as (w-3)^2, whose "
            "minimum is at three. Run several steps of descent and watch the weight approach three, then verify "
            "that your analytic gradient and the finite-difference estimate agree. Today you do exactly that for "
            "one weight, printing the weight and loss at each step. Keeping the example to a single parameter "
            "removes every distraction and shows the core loop that later scales to millions of weights."
        ),
        code=(
            'def loss(w):\n'
            '    return (w - 3.0) ** 2\n'
            '\n'
            'def grad(w):\n'
            '    return 2 * (w - 3.0)\n'
            '\n'
            'def finite_difference(w, eps=1e-6):\n'
            '    return round((loss(w + eps) - loss(w - eps)) / (2 * eps), 4)\n'
            '\n'
            'w = 0.0\n'
            'rate = 0.2\n'
            'for step in range(5):\n'
            '    w = round(w - rate * grad(w), 4)\n'
            '    print(f"step {step} w={w} loss={round(loss(w), 4)}")\n'
            '\n'
            'assert abs(grad(w) - finite_difference(w)) < 0.01\n'
            'assert abs(w - 3.0) < 1.0\n'
            'print("descent follows the negative gradient toward the minimum")'
        ),
        variant_b='raise the learning rate and show that the weight overshoots and oscillates',
        variant_c='start at w=6 and confirm descent still moves toward three from the other side',
        mistakes=[
            "Moving weights in the direction of the gradient, which increases the loss instead of reducing it.",
            "Using a learning rate so large the weight overshoots and diverges.",
            "Trusting an analytic gradient without checking it against a finite difference once.",
        ],
        q1=(
            "Why is a finite-difference gradient check worth doing even when you have an analytic formula?",
            "It independently verifies sign and scale, catching subtle derivative mistakes that make training fail quietly.",
        ),
        homework=(
            "Write `descend(start, rate, steps)` that minimises `loss(w) = (w - 3) ** 2` and returns the final "
            "weight plus the loss history. Run it from two starting points, print both histories, and comment "
            "which line moves the weight against the gradient."
        ),
        patterns=["def ", "round", "print("],
        mapping=(
            "Every optimiser in PyTorch performs some version of this subtract-gradient-times-rate step; the "
            "gradient check is what you run when a real model refuses to converge."
        ),
    ),
    14: dict(
        topic="A tiny network, trained end to end",
        idea=(
            "Today you connect the week into a two-layer network trained on a tiny dataset: a forward pass "
            "computes predictions, a loss measures the error, gradients are computed by the chain rule, and the "
            "parameters move a step. The network is deliberately small, one input, a few hidden units and one "
            "output, so you can follow every number by hand and assert on the result. The exercise teaches the "
            "shape of the training loop — forward, loss, backward, update — which is identical whether the model "
            "has twelve parameters or twelve billion. It also teaches a sobering fact: with finite-difference "
            "gradients the loop is correct but slow, and frameworks exist to make step three fast without "
            "changing the algorithm. Keep the learning rate modest and the target simple, such as learning a "
            "linear relationship, and watch the loss fall over a handful of steps. If the loss does not fall, "
            "that is a bug in the sign of a gradient or the size of the step, not a mysterious property of "
            "neural networks. Build the skeleton here; the domain phases scale it up one idea at a time."
        ),
        code=(
            'def forward(x, w1, w2):\n'
            '    hidden = max(0.0, x * w1)\n'
            '    return hidden * w2\n'
            '\n'
            'def loss(x, y, w1, w2):\n'
            '    return (forward(x, w1, w2) - y) ** 2\n'
            '\n'
            'def grad_w1(x, y, w1, w2):\n'
            '    if x * w1 <= 0:\n'
            '        return 0.0\n'
            '    return 2 * (x * w1 * w2 - y) * w2 * x\n'
            '\n'
            'def grad_w2(x, y, w1, w2):\n'
            '    return 2 * (x * w1 * w2 - y) * max(0.0, x * w1)\n'
            '\n'
            'w1, w2, rate = 0.5, 0.5, 0.05\n'
            'x, y = 2.0, 4.0\n'
            'for step in range(20):\n'
            '    w1 = round(w1 - rate * grad_w1(x, y, w1, w2), 4)\n'
            '    w2 = round(w2 - rate * grad_w2(x, y, w1, w2), 4)\n'
            'print("w1:", w1, "w2:", w2, "loss:", round(loss(x, y, w1, w2), 4))\n'
            '\n'
            'assert loss(x, y, w1, w2) < 0.1\n'
            'print("forward, loss, backward, update: the training loop")'
        ),
        variant_b='change the target to 6 and retrain; confirm the loss still falls from its starting value',
        variant_c='zero the w1 gradient function and show that training stalls, proving each gradient matters',
        mistakes=[
            "Updating weights before computing both gradients, so the second uses a half-updated network.",
            "Forgetting the chain-rule factor, so the gradient has the right sign but the wrong magnitude.",
            "Setting the learning rate so high the loss jumps around instead of decreasing.",
        ],
        q1=(
            "What are the four phases of the training loop this example demonstrates?",
            "Forward pass, loss computation, backward gradient computation, and a parameter update, repeated over steps.",
        ),
        homework=(
            "Write `train(x, y, w1, w2, rate, steps)` that runs the forward, loss, gradient and update steps and "
            "returns the final weights and loss. Run it on two inputs, print the final loss for each, and "
            "comment which line performs the parameter update."
        ),
        patterns=["def ", "round", "print("],
        mapping=(
            "This is the same loop `loss.backward()` and `optimizer.step()` run in PyTorch; the framework only "
            "makes the gradient step automatic and fast."
        ),
    ),
}
