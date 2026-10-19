PHASE = ("Tensors and the Forward Pass", "Build the forward pass by hand: nested lists as tensors, layers as functions, stable softmax and losses, with shapes checked at every boundary.", {
    75: dict(
        topic="Orientation: why deep learning works",
        idea=(
            "Deep learning works because a network of simple units can approximate complicated functions when the "
            "units are stacked with non-linearities between them. Each unit computes a weighted sum of its inputs "
            "and then bends the result, and the next layer treats those bent values as its inputs. A single linear "
            "layer can only stretch, rotate and shift its input; stacking two linear layers without a non-linearity "
            "is still one linear layer, with no extra power. Add a ReLU between them and the composition can "
            "represent corners and thresholds, and enough such pieces can approximate almost any reasonable "
            "function. The other half of the story is learning: the weights start arbitrary, a loss measures how "
            "wrong the output is, and gradients tell each weight which way to move. That combination, a flexible "
            "function class plus a reliable way to improve it, is the whole reason deep networks replaced "
            "hand-written feature pipelines. Today you compare a linear stack with a ReLU stack on the same inputs, "
            "see that only the second bends, and record the difference. Keep the numbers small and the output "
            "exact, because the point is the shape of the function, not floating point, and that is why depth with "
            "the right non-linearity is worth the cost."
        ),
        code=(
            'def linear(x, w, b):\n'
            '    return w * x + b\n'
            '\n'
            'def relu(x):\n'
            '    return x if x > 0 else 0.0\n'
            '\n'
            'for x in [-2, -1, 0, 1, 2]:\n'
            '    one = round(linear(x, 2, 1), 4)\n'
            '    two = round(linear(linear(x, 2, 1), 3, 1), 4)\n'
            '    bent = round(linear(relu(linear(x, 2, 1)), 3, 1), 4)\n'
            '    print(f"x={x} one={one} stacked={two} relu={bent}")\n'
            '\n'
            'assert relu(-1) == 0.0\n'
            'assert linear(relu(linear(1, 2, 1)), 3, 1) == 10\n'
            'print("stacking linear layers stays linear; a ReLU between them bends")'
        ),
        variant_b="swap the ReLU for a sigmoid and check that the bent column changes shape while the stacked column does not",
        variant_c="remove the ReLU entirely and confirm the third column now matches the linear stack exactly",
        mistakes=[
            "Stacking linear layers and expecting extra capacity without any non-linearity between them.",
            "Putting the non-linearity before the weighted sum, so the bend happens on the raw input.",
            "Judging the model by the numbers alone instead of checking whether the function actually bends.",
        ],
        q1=(
            "Why does a ReLU between two linear layers change what the network can represent?",
            "Without it the two layers compose into one linear map, so the function stays straight; the ReLU introduces a bend that cannot be collapsed.",
        ),
        homework=(
            "Write `bend_check(xs, w1, b1, w2, b2)` that runs every value in `xs` through a linear layer, a ReLU, "
            "then a second linear layer, and prints one line per value comparing the ReLU stack with a purely "
            "linear stack. Include the full `def bend_check(...)` signature and comment which line inserts the "
            "non-linearity."
        ),
        patterns=["def bend_check", "relu", "print("],
        mapping=(
            "PyTorch's `nn.Linear` plus `nn.ReLU` composes exactly these functions; the reason depth helps is the "
            "same non-linearity you are testing today."
        ),
    ),
    76: dict(
        topic="Scalars, vectors and matrices as lists",
        idea=(
            "A tensor is just a nested list of numbers, and the names scalar, vector and matrix only describe how "
            "many axes that nesting has. A scalar is a single number with no axes; a vector is a list of numbers "
            "with one axis; a matrix is a list of equal-length lists with two axes. Once you can see the nesting, "
            "you can see the shape, which is the length of each axis in order. A batch of inputs adds a third axis: "
            "a list of vectors, or a matrix of rows. Frameworks print shapes like (32, 3), and every error message "
            "you will meet is ultimately about those numbers disagreeing. The useful habit is to say the shape out "
            "loud before writing a loop: this is a 3 by 2 matrix, so it has three rows and two columns. Then a loop "
            "over rows and a loop over columns writes itself, and indexing bugs become visible. Today you build a "
            "scalar, a vector and a matrix, print their shapes and a few entries, and confirm that len alone tells "
            "you only the outermost axis. Keep the values small integers so the printed structure is easy to read, "
            "and say the nesting out loud before you index anything."
        ),
        code=(
            'scalar = 3\n'
            'vector = [1, 2, 3]\n'
            'matrix = [[1, 2], [3, 4], [5, 6]]\n'
            '\n'
            'print("scalar:", scalar)\n'
            'print("vector:", vector, "len:", len(vector))\n'
            'print("matrix:", matrix)\n'
            'print("rows:", len(matrix), "cols:", len(matrix[0]))\n'
            'print("first row:", matrix[0], "second col:", [row[1] for row in matrix])\n'
            '\n'
            'assert matrix[2][1] == 6\n'
            'assert len(matrix) == 3 and len(matrix[0]) == 2\n'
            'print("names describe nesting: scalar, vector, matrix")'
        ),
        variant_b="build a 2x3 matrix, print its rows and columns, and index the last element both ways",
        variant_c="add a batch axis around the matrix and print the resulting three-level nesting",
        mistakes=[
            "Treating len(matrix) as the total number of entries instead of the outermost axis length.",
            "Building rows of different lengths and calling the result a matrix.",
            "Indexing with (row, column) reversed, which still returns a number and hides the mistake.",
        ],
        q1=(
            "What does the shape of a nested list actually measure?",
            "The length of each axis in order, starting from the outermost list and following one row inward.",
        ),
        homework=(
            "Write `describe_tensor(t)` that prints a scalar, vector or matrix together with its outer length and, "
            "for a matrix, its row and column counts. Call it on all three kinds and comment which check tells you "
            "the rows form a rectangle."
        ),
        patterns=["def describe_tensor", "len(", "print("],
        mapping=(
            "A tensor in PyTorch is this nesting plus a dtype and a device; `tensor.shape` reports the same axis "
            "lengths you are printing here."
        ),
    ),
    77: dict(
        topic="Shapes and axes",
        idea=(
            "Shapes and axes are the grammar of tensor code, and most bugs are grammar mistakes rather than maths "
            "mistakes. The shape of a nested list is the tuple of axis lengths: a vector of four numbers has shape "
            "(4,), a matrix of three rows and two columns has shape (3, 2), and a batch of five such matrices has "
            "shape (5, 3, 2). The axis order matters because operations name their axes by position: axis zero is "
            "the batch, axis one is usually features, and reducing along an axis removes it. If you transpose a "
            "matrix, its shape swaps, and every downstream operation sees the new order. Writing a small shape "
            "function that walks the nesting makes this concrete and gives you a tool you can reuse when a real "
            "framework reports a mismatch. The other useful skill is checking that all rows of a matrix have equal "
            "length; a ragged list looks like a matrix in Python but breaks any loop that assumes rectangularity. "
            "Today you print shapes, transpose a matrix, and watch the shape swap. Assert on the shapes so a wrong "
            "mental model fails immediately rather than producing plausible numbers, and keep the values small "
            "integers so the structure stays readable."
        ),
        code=(
            'def shape(t):\n'
            '    dims = []\n'
            '    while isinstance(t, list):\n'
            '        dims.append(len(t))\n'
            '        if not t:\n'
            '            break\n'
            '        t = t[0]\n'
            '    return tuple(dims)\n'
            '\n'
            'def transpose(m):\n'
            '    return [list(col) for col in zip(*m)]\n'
            '\n'
            'matrix = [[1, 2, 3], [4, 5, 6]]\n'
            'print("matrix shape:", shape(matrix))\n'
            'print("transpose shape:", shape(transpose(matrix)))\n'
            'print("transposed:", transpose(matrix))\n'
            'print("vector shape:", shape([1, 2, 3]))\n'
            'print("row lengths:", [len(row) for row in matrix])\n'
            '\n'
            'assert shape(matrix) == (2, 3)\n'
            'assert shape(transpose(matrix)) == (3, 2)\n'
            'print("shape is the length of each axis in order")'
        ),
        variant_b="transpose a 3x1 column into a 1x3 row and print both shapes before and after",
        variant_c="append a short row and show that the ragged list now has an inconsistent shape",
        mistakes=[
            "Confusing shape (3,) with (1, 3): a vector is not the same as a batch of one row.",
            "Forgetting that transposing swaps the axis order, then reusing the old shape in later code.",
            "Assuming a list of lists is rectangular without checking every row length.",
        ],
        q1=(
            "What is the shape of a list containing two rows of three numbers, and what is it after transpose?",
            "It is (2, 3) before transpose and (3, 2) after, because transpose swaps the row and column axes.",
        ),
        homework=(
            "Write `shape(t)` that returns a tuple of axis lengths, plus `transpose(m)`. Print the shape of a 2x3 "
            "matrix, transpose it, print the new shape, and comment which line follows one row inward to discover "
            "the next axis."
        ),
        patterns=["def shape", "while", "print("],
        mapping=(
            "`tensor.shape` and `tensor.T` are the framework versions; reading a shape error backwards to the "
            "first wrong axis is the same skill."
        ),
    ),
    78: dict(
        topic="Broadcasting a bias",
        idea=(
            "Broadcasting is the rule that lets a small tensor combine with a larger one without writing an "
            "explicit loop, and the bias vector is where you meet it first. A dense layer produces a batch of rows, "
            "each row the same width as the bias. Adding the bias to every row means the bias is reused along the "
            "batch axis: its shape (features,) lines up with the trailing axis of the batch (batch, features). The "
            "rule is to compare shapes from the right, treat a missing axis as size one, and stretch any axis of "
            "size one to match the other operand. That is why a scalar adds to everything and a length-three "
            "vector adds to every row of a batch with three columns, but a length-two vector against three columns "
            "is an error. Understanding the rule saves you from writing nested loops by hand and, more importantly, "
            "stops silent mistakes where the wrong axis gets stretched. Today you add a bias to a batch, add a "
            "scalar to a matrix, and then attempt a deliberately mismatched shape so the failure is visible. Print "
            "shapes alongside values, because broadcasting is much easier to trust when you can see which axis "
            "moved and which one stayed put."
        ),
        code=(
            'def add_bias(batch, bias):\n'
            '    out = []\n'
            '    for row in batch:\n'
            '        if len(row) != len(bias):\n'
            '            raise ValueError("bias width must match the feature axis")\n'
            '        out.append([x + b for x, b in zip(row, bias)])\n'
            '    return out\n'
            '\n'
            'def add_scalar(matrix, value):\n'
            '    return [[x + value for x in row] for row in matrix]\n'
            '\n'
            'batch = [[1, 2, 3], [4, 5, 6]]\n'
            'bias = [10, 20, 30]\n'
            'print("batch + bias:", add_bias(batch, bias))\n'
            'print("batch + 1:", add_scalar(batch, 1))\n'
            'print("feature width:", len(batch[0]), "bias length:", len(bias))\n'
            '\n'
            'try:\n'
            '    add_bias(batch, [1, 2])\n'
            'except ValueError as error:\n'
            '    print("rejected:", error)\n'
            '\n'
            'assert add_bias(batch, bias) == [[11, 22, 33], [14, 25, 36]]\n'
            'print("a bias is stretched along the batch axis, not the feature axis")'
        ),
        variant_b="swap the bias for a scalar and confirm every entry moves by the same amount",
        variant_c="use a bias longer than the row and read the error, then explain which axis failed to line up",
        mistakes=[
            "Adding the bias across the batch axis instead of the feature axis.",
            "Relying on zip to truncate a mismatched bias silently and returning a short row.",
            "Forgetting that a scalar broadcasts to every entry while a vector broadcasts per column.",
        ],
        q1=(
            "Why can a length-three bias be added to every row of a 2x3 batch?",
            "The shapes align from the right: the bias matches the trailing feature axis and is reused across the batch axis.",
        ),
        homework=(
            "Write `add_bias(batch, bias)` that raises `ValueError` when the bias width does not match a row, and "
            "`add_scalar(matrix, value)`. Print a normal bias add, a scalar add, and the caught mismatch error, and "
            "comment which line enforces the feature-axis rule."
        ),
        patterns=["def add_bias", "zip(", "print("],
        mapping=(
            "PyTorch broadcasts `bias` of shape (features,) across (batch, features) using this exact right-to-left "
            "alignment; a mismatch is a shape error you can now predict."
        ),
    ),
    79: dict(
        topic="Dot products and matmul",
        idea=(
            "The dot product and matrix multiplication are the two operations that do almost all the arithmetic in "
            "a neural network. A dot product pairs two equal-length vectors, multiplies element by element, and "
            "sums; that is exactly the weighted sum inside one neuron. Matrix multiplication repeats the dot "
            "product for every row of the left operand and every column of the right, so a weight matrix times an "
            "input vector produces all the pre-activations of a layer at once. The shape rule is short and "
            "absolute: the inner dimensions must agree, so an (m, k) matrix times a (k, n) matrix gives (m, n). "
            "Writing the loops by hand shows where that rule comes from and why the result takes its rows from the "
            "left and its columns from the right. It also shows why transposing the wrong operand gives plausible "
            "but wrong numbers rather than an error. Today you implement dot and matmul, multiply a small weight "
            "matrix by an input vector, and assert against hand-computed values. Keep the numbers integers so any "
            "wrong result is unmistakable, and print the shapes next to the result to reinforce that the inner "
            "dimensions are the ones that must match. Treat the shape as the contract and the numbers as a "
            "consequence of it."
        ),
        code=(
            'def dot(a, b):\n'
            '    return sum(x * y for x, y in zip(a, b))\n'
            '\n'
            'def matmul(a, b):\n'
            '    if len(a[0]) != len(b):\n'
            '        raise ValueError("inner dimensions must agree")\n'
            '    columns = list(zip(*b))\n'
            '    return [[dot(row, col) for col in columns] for row in a]\n'
            '\n'
            'weights = [[1, 2, 3], [4, 5, 6]]\n'
            'x = [[1], [1], [2]]\n'
            'result = matmul(weights, x)\n'
            'print("dot:", dot([1, 2, 3], [4, 5, 6]))\n'
            'print("weights:", (len(weights), len(weights[0])))\n'
            'print("input:", (len(x), len(x[0])))\n'
            'print("result:", result)\n'
            '\n'
            'assert dot([1, 2, 3], [4, 5, 6]) == 32\n'
            'assert result == [[9], [21]]\n'
            'print("inner dimensions agree: (2,3) x (3,1) -> (2,1)")'
        ),
        variant_b="multiply the same weights by a 3x2 input and print the 2x2 result with its shape",
        variant_c="pass a 2x2 input and show that the inner-dimension check raises before any arithmetic runs",
        mistakes=[
            "Multiplying rows by rows because the operands happen to have the same length.",
            "Letting zip truncate unequal vectors instead of checking the inner dimension.",
            "Forgetting to transpose the right operand so the result is silently the wrong shape.",
        ],
        q1=(
            "For an (m, k) matrix times a (k, n) matrix, what is the result shape and why?",
            "It is (m, n): each of the m rows takes a dot product with each of the n columns, and the shared k disappears.",
        ),
        homework=(
            "Write `dot(a, b)` and `matmul(a, b)` for lists of lists, with `matmul` raising when the inner "
            "dimensions disagree. Multiply a 2x3 weight matrix by a 3x1 input, print the shapes and result, and "
            "comment which line enforces that the inner dimensions agree."
        ),
        patterns=["def matmul", "def dot", "print("],
        mapping=(
            "`torch.matmul` and NumPy's `dot` run this same inner-dimension rule, just with fast kernels; the "
            "transpose traps are identical at scale."
        ),
    ),
    80: dict(
        topic="Layers as functions",
        idea=(
            "A layer is a function with parameters, and the cleanest way to understand one is to write it as a "
            "function that takes its weights as arguments. The function receives a batch of input rows, multiplies "
            "each row by the weight matrix, adds the bias, applies an activation, and returns a batch of output "
            "rows. Nothing inside it knows or cares whether the weights came from a random initialisation, a "
            "checkpoint or a hand-written test. That separation is what makes training possible: the optimiser "
            "updates parameter data, and the layer code stays fixed. It also makes testing trivial, because you can "
            "pass known weights and check the output by hand. The batch axis should be explicit in the signature, "
            "not implied by a global variable, so the same function works for one example or a hundred. Today you "
            "write a dense layer that takes batch, weights, bias and an activation function, run two rows through "
            "it, and print each input beside its output. Follow one row through the arithmetic by hand and confirm "
            "the code agrees, because that is how you build intuition for what a framework is doing under the hood, "
            "and why swapping the activation is a one-argument change."
        ),
        code=(
            'def relu(x):\n'
            '    return x if x > 0 else 0.0\n'
            '\n'
            'def dense(batch, weights, bias, activation):\n'
            '    outputs = []\n'
            '    for row in batch:\n'
            '        pre = [sum(v * w for v, w in zip(row, w_row)) + b\n'
            '               for w_row, b in zip(weights, bias)]\n'
            '        outputs.append([round(activation(v), 4) for v in pre])\n'
            '    return outputs\n'
            '\n'
            'weights = [[1, -1], [0, 1]]\n'
            'bias = [0, 1]\n'
            'batch = [[1, 2], [3, 0]]\n'
            'result = dense(batch, weights, bias, relu)\n'
            'for row, out in zip(batch, result):\n'
            '    print(row, "->", out)\n'
            '\n'
            'assert result == [[0.0, 3.0], [3.0, 1.0]]\n'
            'print("a layer is a function of batch, weights, bias and activation")'
        ),
        variant_b="pass an identity activation and show that the negative pre-activation survives",
        variant_c="chain a second dense layer after the first and print the intermediate and final batches",
        mistakes=[
            "Hard-coding the weights inside the layer, leaving nothing to train, save or swap.",
            "Adding the bias once per batch instead of once per output unit.",
            "Dropping the batch axis and processing single rows only at the call site.",
        ],
        q1=(
            "Why should a layer receive its weights and bias as arguments?",
            "Parameters then stay separate from computation, so the same layer can be tested, trained, saved and reused with different values.",
        ),
        homework=(
            "Write `dense(batch, weights, bias, activation)` returning one output row per input row. Run a two-row "
            "batch through a 2x2 weight matrix with ReLU, print each row's input and output, and comment which line "
            "adds the bias per unit."
        ),
        patterns=["def dense", "for ", "print("],
        mapping=(
            "`nn.Linear` is this function with parameters stored as tensors; keeping the forward computation "
            "separate from parameter storage is the split optimisers depend on."
        ),
    ),
    81: dict(
        topic="ReLU and other activations",
        idea=(
            "Activations decide what each unit passes on, and ReLU is the default because it is simple and trains "
            "well. ReLU returns its input when that input is positive and zero otherwise, so it keeps the positive "
            "part of the signal and clips everything below zero. That clip is the non-linearity: without it, a "
            "stack of layers collapses into a single linear map. ReLU is cheap, has a constant gradient of one "
            "wherever it is active, and produces sparse activations because roughly half the units output zero for "
            "a typical input. Its weakness is the dead unit problem: a unit whose pre-activation is negative for "
            "every input receives no gradient and stops changing. Variants address that, such as leaky ReLU, which "
            "lets a small fraction through on the negative side. Today you implement ReLU and a leaky version, run "
            "the same values through both, and print where they differ. The comparison makes the trade-off visible: "
            "ReLU is sharper and sparser, leaky ReLU keeps a small signal alive. Round the outputs and use a "
            "handful of values, including zero, because the boundary behaviour is the part worth seeing, and check "
            "that both functions agree on every positive input, and that plateau is a signal to inspect the "
            "activation choice."
        ),
        code=(
            'def relu(x):\n'
            '    return x if x > 0 else 0.0\n'
            '\n'
            'def leaky_relu(x, slope=0.1):\n'
            '    return x if x > 0 else round(slope * x, 4)\n'
            '\n'
            'for value in [-2, -1, 0, 1, 2]:\n'
            '    print(f"x={value} relu={relu(value)} leaky={leaky_relu(value)}")\n'
            '\n'
            'assert relu(-1) == 0.0\n'
            'assert leaky_relu(-1) == -0.1\n'
            'assert relu(2) == leaky_relu(2) == 2\n'
            'print("relu clips negatives; leaky relu keeps a small slope alive")'
        ),
        variant_b="raise the leaky slope to 0.5 and print how the negative outputs change",
        variant_c="add a very negative input and confirm ReLU flattens it while leaky ReLU still passes a little",
        mistakes=[
            "Adding the activation before the weighted sum, which clips the inputs rather than the pre-activations.",
            "Expecting ReLU to output a small negative value instead of exactly zero.",
            "Ignoring dead units whose pre-activation is negative for every example in the batch.",
        ],
        q1=(
            "What does ReLU return for a negative input, and why does that create sparsity?",
            "It returns exactly zero, so every unit with a negative pre-activation contributes nothing and the activation vector contains many zeros.",
        ),
        homework=(
            "Write `relu(x)` and `leaky_relu(x, slope=0.1)`, then `compare_activations(values)` that prints each "
            "input with both outputs. Run it on values from minus two to two including zero, and comment which "
            "line makes leaky ReLU differ on the negative side."
        ),
        patterns=["def compare_activations", "leaky_relu", "print("],
        mapping=(
            "`F.relu` and `nn.LeakyReLU` are the framework versions; knowing the negative-side behaviour is how "
            "you diagnose dead units during training."
        ),
    ),
    82: dict(
        topic="Sigmoid and tanh",
        idea=(
            "Sigmoid and tanh are the classic squashing functions, and both turn an unbounded score into a bounded "
            "output with a smooth curve. Sigmoid maps any real number into zero to one, which makes it natural for "
            "probabilities and for gates that decide how much of a signal to let through. Tanh is a shifted and "
            "scaled sigmoid that maps into minus one to one, so its outputs are centred on zero, which usually "
            "helps optimisation. Both are smooth, so their derivatives exist everywhere and are easy to express in "
            "terms of their own output. That convenience is also their weakness: for large positive or negative "
            "inputs the curve flattens, the gradient becomes tiny, and learning stalls, the vanishing gradient "
            "problem that made deep networks hard before ReLU. Today you implement both with math.exp, print a "
            "small table of inputs and outputs, and check the symmetry of tanh. Use round on every printed value, "
            "because the interesting part is the shape of the curve and the exact tail digits only distract. Notice "
            "that both functions are monotonic: larger input always means larger output, so they preserve order "
            "while compressing range, and both pass through the origin in tanh's case or one half in sigmoid's."
        ),
        code=(
            'import math\n'
            '\n'
            'def sigmoid(x):\n'
            '    return round(1 / (1 + math.exp(-x)), 4)\n'
            '\n'
            'def tanh(x):\n'
            '    return round((math.exp(x) - math.exp(-x)) / (math.exp(x) + math.exp(-x)), 4)\n'
            '\n'
            'for value in [-2, -1, 0, 1, 2]:\n'
            '    print(f"x={value} sigmoid={sigmoid(value)} tanh={tanh(value)}")\n'
            '\n'
            'assert sigmoid(0) == 0.5\n'
            'assert abs(tanh(-1) + tanh(1)) < 0.0001\n'
            'print("sigmoid squashes to (0,1); tanh to (-1,1) and is symmetric")'
        ),
        variant_b="feed values ten and minus ten and show how close both curves are to their flat tails",
        variant_c="compare tanh with two times sigmoid minus one and confirm the two curves agree",
        mistakes=[
            "Using sigmoid for hidden layers in a deep network and then wondering why gradients vanish.",
            "Forgetting that tanh is centred on zero while sigmoid is not.",
            "Computing exp of a large positive value without guarding against overflow in real code.",
        ],
        q1=(
            "What range does each function produce, and which one is centred on zero?",
            "Sigmoid produces values between zero and one; tanh produces values between minus one and one and is centred on zero.",
        ),
        homework=(
            "Write `squash_table(values)` that imports `math`, computes sigmoid and tanh for each value, and prints "
            "a rounded table. Include both formulas, run it on values from minus two to two, and comment which line "
            "shows that tanh is symmetric around zero."
        ),
        patterns=["def squash_table", "math.exp", "print("],
        mapping=(
            "`torch.sigmoid` and `torch.tanh` are these curves; the saturation tails are why hidden layers mostly "
            "moved to ReLU."
        ),
    ),
    83: dict(
        topic="Softmax for scores",
        idea=(
            "Softmax turns a vector of arbitrary scores into a probability distribution, which is why it sits at "
            "the end of classifiers. It exponentiates each score and divides by the sum of the exponentials, so "
            "every output is positive and the whole vector sums to one. The relative order is preserved: a larger "
            "score still gets a larger probability, but the exponential exaggerates differences, so a clear winner "
            "approaches one and the rest approach zero. The naive implementation has a numerical trap: exp of a "
            "large score overflows, and exp of very negative scores underflows to zero. The standard fix is to "
            "subtract the maximum score from every score before exponentiating. That shifts the whole vector, and "
            "because softmax is invariant to adding the same constant to all scores, the result is mathematically "
            "identical while the largest exponent becomes exp(0) equals one. Today you implement softmax both ways "
            "on scores large enough to break the naive version, print the probabilities, and show that subtracting "
            "the maximum gives the same answer without overflow. Softmax reports relative confidence rather than "
            "a decision, so reading the vector is usually more informative than taking the largest entry alone. "
            "This one trick appears in every production implementation, so make it a reflex rather than an "
            "optional detail."
        ),
        code=(
            'import math\n'
            '\n'
            'def softmax(scores):\n'
            '    shifted = [s - max(scores) for s in scores]\n'
            '    exps = [math.exp(s) for s in shifted]\n'
            '    total = sum(exps)\n'
            '    return [round(e / total, 4) for e in exps]\n'
            '\n'
            'scores = [2, 1, 0]\n'
            'print("scores:", scores)\n'
            'print("shifted:", [s - max(scores) for s in scores])\n'
            'print("softmax:", softmax(scores))\n'
            '\n'
            'big = [1000, 1001, 1002]\n'
            'print("big scores:", big)\n'
            'print("stable softmax:", softmax(big))\n'
            '\n'
            'assert softmax([0, 0, 0]) == [0.3333, 0.3333, 0.3333]\n'
            'assert abs(sum(softmax(big)) - 1) < 0.001\n'
            'print("subtracting the max keeps softmax stable and unchanged")'
        ),
        variant_b="pass scores that differ by one hundred and confirm the largest probability dominates",
        variant_c="remove the max subtraction, catch the overflow on the big scores, and print the failure",
        mistakes=[
            "Exponentiating raw scores so large values overflow to infinity and divide into nan.",
            "Forgetting to divide by the sum, leaving positive numbers that do not add to one.",
            "Subtracting the max after exponentiating, which no longer stabilises anything.",
        ],
        q1=(
            "Why does subtracting the maximum score before exp not change the softmax result?",
            "Subtracting the same constant from every score multiplies every exponential by the same factor, which cancels in the division.",
        ),
        homework=(
            "Write `softmax(scores)` that subtracts the maximum before calling `math.exp`, divides by the total, and "
            "returns rounded probabilities. Print the shifted scores and result for a normal case and a case near "
            "one thousand, and comment which line makes the big case safe."
        ),
        patterns=["def softmax", "max(scores)", "print("],
        mapping=(
            "`F.softmax` subtracts the max internally; when you write cross-entropy from logits, frameworks do the "
            "same shift to stay stable."
        ),
    ),
    84: dict(
        topic="The forward pass",
        idea=(
            "The forward pass is the full journey from input to prediction, and writing it end to end is the point "
            "where the individual pieces become a network. You start with a batch of input rows, apply the first "
            "layer's weights and bias, pass the result through an activation, then feed that into the next layer, "
            "and repeat until the output layer produces scores. Each step has a shape, and checking those shapes as "
            "you go is what keeps a forward pass debuggable. The output is not yet a decision; for classification "
            "you would apply softmax, and for regression you might stop at a single number. The important property "
            "is that the forward pass is pure computation: given the same parameters and inputs, it returns the "
            "same output every time, with no learning happening yet. That purity is why you can test it with fixed "
            "weights before ever running an optimiser. Today you build a two-layer network by hand, print the "
            "intermediate activation and the final output for two input rows, and assert on the expected values. "
            "Follow one row through both layers on paper, because the forward pass is the part every later topic, "
            "losses, gradients and training, assumes you can already read."
        ),
        code=(
            'def relu(x):\n'
            '    return x if x > 0 else 0.0\n'
            '\n'
            'def layer(x, weights, bias, activation):\n'
            '    pre = [sum(v * w for v, w in zip(x, w_row)) + b\n'
            '           for w_row, b in zip(weights, bias)]\n'
            '    return [round(activation(v), 4) for v in pre]\n'
            '\n'
            'def forward(batch, w1, b1, w2, b2):\n'
            '    hidden = [layer(row, w1, b1, relu) for row in batch]\n'
            '    output = [layer(h, w2, b2, lambda v: v) for h in hidden]\n'
            '    return hidden, output\n'
            '\n'
            'batch = [[1, 0], [0, 1]]\n'
            'w1, b1 = [[1, -1], [1, 1]], [0, 0]\n'
            'w2, b2 = [[1, 1]], [0]\n'
            'hidden, output = forward(batch, w1, b1, w2, b2)\n'
            'for row, h, out in zip(batch, hidden, output):\n'
            '    print(row, "hidden", h, "out", out)\n'
            '\n'
            'assert output == [[2.0], [1.0]]\n'
            'print("the forward pass chains layers and keeps the batch axis")'
        ),
        variant_b="make the second layer two units wide and print both output columns for each row",
        variant_c="remove the ReLU from the hidden layer and show the output change on the row with a negative score",
        mistakes=[
            "Applying weights to the wrong axis so the batch disappears halfway through the pass.",
            "Reusing stale intermediate values from the previous row instead of the current one.",
            "Adding an activation to the output layer of a regression model by habit.",
        ],
        q1=(
            "What does the forward pass compute, and why is it called pure?",
            "It chains layers and activations from input to output; it is pure because fixed weights and inputs always produce the same result with no parameter updates.",
        ),
        homework=(
            "Write `forward(batch, w1, b1, w2, b2)` returning the hidden batch and the output batch. Use a ReLU on "
            "the first layer and identity on the second, print the intermediate and final rows, and comment which "
            "line hands the first layer's output to the second."
        ),
        patterns=["def forward", "relu", "print("],
        mapping=(
            "A PyTorch model's `forward` method is this chain; `model(x)` runs it without touching gradients when "
            "wrapped in `torch.no_grad()`."
        ),
    ),
    85: dict(
        topic="Batching inputs",
        idea=(
            "Batching means sending several examples through the network at once, and it changes the shape of every "
            "intermediate rather than the maths itself. A single input row has shape (features,); a batch of rows "
            "has shape (batch, features). The weight matrix is shared across the batch, so the first layer turns "
            "(batch, features) into (batch, hidden), and every later layer preserves the leading batch axis. That "
            "shared weight is the whole efficiency argument: one matrix multiply handles many examples, and the "
            "hardware can work on them in parallel. Batching also stabilises the loss, because averaging over "
            "several examples smooths out the noise of any single one. The cost is memory: the batch axis multiplies "
            "everything, including the activations you keep for the backward pass. The practical habit is to state "
            "the batch shape at each stage of the forward pass and confirm it is unchanged except for the feature "
            "width. Today you run a batch of three rows through a dense layer, print the shape before and after, and "
            "verify that the second row's output equals the output you get by running that row alone. That equality "
            "is the clearest proof that batching is just vectorised repetition, and the printed rows make the "
            "repetition obvious."
        ),
        code=(
            'def dense(batch, weights, bias):\n'
            '    return [[round(sum(v * w for v, w in zip(row, w_row)) + b, 4)\n'
            '             for w_row, b in zip(weights, bias)]\n'
            '            for row in batch]\n'
            '\n'
            'weights = [[1, 0], [0, 2]]\n'
            'bias = [1, -1]\n'
            'batch = [[1, 2], [0, 3], [4, 1]]\n'
            'out = dense(batch, weights, bias)\n'
            'print("batch shape:", (len(batch), len(batch[0])))\n'
            'print("output shape:", (len(out), len(out[0])))\n'
            'for row, result in zip(batch, out):\n'
            '    print(row, "->", result)\n'
            '\n'
            'single = dense([batch[1]], weights, bias)\n'
            'assert single[0] == out[1]\n'
            'print("one row through the batch layer equals the batched result")'
        ),
        variant_b="add a fourth row and confirm only the leading shape changes, not the feature width",
        variant_c="run each row separately in a loop and show that concatenating the outputs equals the batch result",
        mistakes=[
            "Putting the batch axis last, so the feature width and batch size swap meaning.",
            "Averaging losses over rows instead of over examples when the batch shape changes.",
            "Assuming one row and a batch of one row have the same shape.",
        ],
        q1=(
            "What shape does a dense layer map (batch, features) to, and which axis is preserved?",
            "It maps to (batch, hidden) and preserves the leading batch axis; only the feature width changes.",
        ),
        homework=(
            "Write `batched_dense(batch, weights, bias)` returning one output row per input row, plus a call that "
            "runs a single row alone. Print the shapes before and after, prove the single row matches its batched "
            "counterpart, and comment which line preserves the batch axis."
        ),
        patterns=["def batched_dense", "for ", "print("],
        mapping=(
            "A PyTorch DataLoader hands you batches with this leading axis; the same weights process all rows, "
            "which is what makes GPU throughput possible."
        ),
    ),
    86: dict(
        topic="Loss functions",
        idea=(
            "A loss function turns predictions into a single number that measures how wrong the model is, and "
            "training is only meaningful once that number is defined. For regression, mean squared error subtracts "
            "each prediction from its target, squares the difference, and averages over the batch. Squaring makes "
            "every term non-negative so errors cannot cancel, and it punishes large mistakes more than small ones. "
            "For classification, cross-entropy compares predicted probabilities with the true class: it is the "
            "negative log of the probability assigned to the correct answer, so a confident correct prediction "
            "costs almost nothing and a confident wrong one costs a lot. Both losses share two habits worth "
            "building now: compute them over the whole batch, and test them on cases whose answer you know. A "
            "perfect prediction must give zero for mean squared error, and a model that assigns probability one to "
            "the right class must give zero cross-entropy. Today you implement mean squared error and a small "
            "cross-entropy, evaluate them on good and bad predictions, and print the numbers side by side. If a "
            "model will not learn, the loss is the first thing to inspect, because a wrong loss silently optimises "
            "the wrong objective no matter how good the layers are."
        ),
        code=(
            'import math\n'
            '\n'
            'def mse(predictions, targets):\n'
            '    total = sum((p - t) ** 2 for p, t in zip(predictions, targets))\n'
            '    return round(total / len(predictions), 4)\n'
            '\n'
            'def cross_entropy(probs, target_index):\n'
            '    return round(-math.log(probs[target_index]), 4)\n'
            '\n'
            'print("mse perfect:", mse([1, 2, 3], [1, 2, 3]))\n'
            'print("mse wrong:", mse([1, 2, 0], [1, 2, 3]))\n'
            'print("ce confident:", cross_entropy([0.9, 0.1], 0))\n'
            'print("ce unsure:", cross_entropy([0.5, 0.5], 0))\n'
            '\n'
            'assert mse([1, 2, 3], [1, 2, 3]) == 0.0\n'
            'assert cross_entropy([1.0, 0.0], 0) == 0.0\n'
            'print("a loss reduces a whole batch to one comparable number")'
        ),
        variant_b="add a mean absolute error function and compare its value with mse on the same wrong prediction",
        variant_c="double one error and show that mse more than doubles while absolute error only doubles",
        mistakes=[
            "Forgetting to divide by the number of examples, so the loss grows with batch size.",
            "Squaring without averaging and then comparing runs with different batch sizes.",
            "Taking the log of a probability that underflowed to zero, producing negative infinity.",
        ],
        q1=(
            "Why does mean squared error give zero only when every prediction matches its target?",
            "Each term is a squared difference, so it is non-negative and can be zero only when that difference is exactly zero.",
        ),
        homework=(
            "Write `loss_report(predictions, targets)` that returns mse and mean absolute error, plus a "
            "`cross_entropy(probs, target_index)` helper. Print all three on a perfect case and a wrong case, and "
            "comment which line guarantees a perfect prediction scores zero."
        ),
        patterns=["def loss_report", "return", "print("],
        mapping=(
            "`nn.MSELoss` and `nn.CrossEntropyLoss` are these functions with stability care; the first thing to "
            "check when training stalls is whether the loss matches the task."
        ),
    ),
    87: dict(
        topic="Numerical stability",
        idea=(
            "Numerical stability is about keeping intermediate numbers inside the range floating point can "
            "represent, because overflow and underflow turn correct formulas into nonsense. The classic example is "
            "softmax: exponentiating a large score like one thousand overflows to infinity, and dividing by "
            "infinity gives zero or nan. The fix is algebraic, not a hack: subtract the maximum score before "
            "exponentiating. Softmax is unchanged by adding a constant to every score, and after subtracting the "
            "maximum the largest exponent is exp(0), so the values stay between zero and one. The same idea appears "
            "in log-sum-exp for log probabilities, where you factor out the maximum before taking the log. "
            "Underflow matters too: a probability that rounds to zero makes its log negative infinity, so "
            "cross-entropy should be computed from logits rather than from already-squashed probabilities. "
            "Frameworks hide these details, which is exactly why you should write them once by hand. Today you run a "
            "naive softmax on large scores, watch it fail or return nan, then run the stabilised version and show "
            "that it returns sensible probabilities. Print the raw exponent sum alongside the result so the reason "
            "for the shift is visible, and remember that this is arithmetic care, not a deep learning trick."
        ),
        code=(
            'import math\n'
            '\n'
            'def naive_softmax(scores):\n'
            '    exps = [math.exp(s) for s in scores]\n'
            '    return [round(e / sum(exps), 4) for e in exps]\n'
            '\n'
            'def stable_softmax(scores):\n'
            '    shifted = [s - max(scores) for s in scores]\n'
            '    exps = [math.exp(s) for s in shifted]\n'
            '    return [round(e / sum(exps), 4) for e in exps]\n'
            '\n'
            'scores = [1000, 1001, 1002]\n'
            'try:\n'
            '    print("naive:", naive_softmax(scores))\n'
            'except OverflowError:\n'
            '    print("naive: OverflowError")\n'
            '\n'
            'print("stable:", stable_softmax(scores))\n'
            'print("largest shifted exponent:", math.exp(0))\n'
            '\n'
            'assert stable_softmax([0, 1]) == [0.2689, 0.7311]\n'
            'print("subtract the max: same answer, no overflow")'
        ),
        variant_b="use scores around minus one thousand and show that the stable version still returns probabilities that sum near one",
        variant_c="shift every score by a constant and confirm both the naive and stable results are unchanged",
        mistakes=[
            "Exponentiating raw logits so large scores overflow before the division.",
            "Subtracting the max only from the numerator instead of from every score.",
            "Calling log on a probability that underflowed to zero and expecting a finite loss.",
        ],
        q1=(
            "What exactly does subtracting the maximum protect against, and why is the result unchanged?",
            "It keeps the largest exponent at exp(0) so nothing overflows; the same constant is subtracted from every score, so the common factor cancels in the division.",
        ),
        homework=(
            "Write `stable_softmax(scores)` and `naive_softmax(scores)`, then feed both a vector near one thousand. "
            "Catch the overflow from the naive version, print the stable probabilities and the largest shifted "
            "exponent, and comment which line prevents overflow."
        ),
        patterns=["def stable_softmax", "max(scores)", "math.exp"],
        mapping=(
            "Framework softmax and log-softmax do this shift internally; when you see nan in a real training run, "
            "overflow or a log of zero is the usual cause."
        ),
    ),
    88: dict(
        topic="Debugging shapes",
        idea=(
            "Shape bugs are the most common failure in tensor code, and the fix is a habit rather than a talent: "
            "print or assert the shape at every boundary before you look at the values. A mismatch usually appears "
            "as an error deep inside a library, far from the line that caused it, so the useful skill is tracing "
            "backwards to the first operation where the shape became wrong. Start by writing down the expected "
            "shape of every input, weight, bias and output, then compare that expectation with reality using a small "
            "shape helper. Pay attention to the difference between a shape of (3,) and (1, 3): one is a vector, the "
            "other is a batch containing one row, and many operations treat them differently. Check the batch axis "
            "survived, that the feature axis matches the weight's input width, and that reductions removed exactly "
            "the axis you meant. Also check for ragged rows, because Python happily builds a list of lists that is "
            "not rectangular and then fails later. Today you write a matmul that validates inner dimensions and "
            "raises a clear error, then trigger it deliberately and read the message. A good error at the boundary "
            "is worth more than an hour of print statements inside the loop."
        ),
        code=(
            'def shape(t):\n'
            '    dims = []\n'
            '    while isinstance(t, list):\n'
            '        dims.append(len(t))\n'
            '        if not t:\n'
            '            break\n'
            '        t = t[0]\n'
            '    return tuple(dims)\n'
            '\n'
            'def checked_matmul(a, b):\n'
            '    if shape(a)[-1] != shape(b)[0]:\n'
            '        raise ValueError(f"inner dimensions disagree: {shape(a)} x {shape(b)}")\n'
            '    return [[sum(x * y for x, y in zip(row, col))\n'
            '             for col in zip(*b)] for row in a]\n'
            '\n'
            'good = checked_matmul([[1, 2], [3, 4]], [[1], [1]])\n'
            'print("good:", good)\n'
            'print("good shapes:", shape([[1, 2], [3, 4]]), "x", shape([[1], [1]]), "->", shape(good))\n'
            '\n'
            'bad_a, bad_b = [[1, 2, 3]], [[1], [1]]\n'
            'print("bad shapes:", shape(bad_a), "x", shape(bad_b))\n'
            'try:\n'
            '    checked_matmul(bad_a, bad_b)\n'
            'except ValueError as error:\n'
            '    print("error:", error)\n'
            '\n'
            'assert good == [[3], [7]]\n'
            'print("assert the shape at every boundary, not just the values")'
        ),
        variant_b="check the bias width before adding it and raise with both shapes in the message",
        variant_c="build a ragged matrix and have the shape helper report the inconsistent row lengths",
        mistakes=[
            "Reading values before checking shapes, so the first error appears far from its cause.",
            "Treating (3,) and (1, 3) as interchangeable when one is a vector and the other a batch.",
            "Assuming a list of lists is rectangular without checking every row length.",
        ],
        q1=(
            "Where should a shape check live, and what should its error message include?",
            "At the boundary of the operation that consumes the shapes, with both operands' shapes so the mismatched axis is obvious.",
        ),
        homework=(
            "Write `checked_matmul(a, b)` that computes shapes, raises `ValueError` with both shapes when the inner "
            "dimensions disagree, and otherwise returns the product. Print one successful product and one caught "
            "error, and comment which line stops the arithmetic before it runs."
        ),
        patterns=["def checked_matmul", "raise", "print("],
        mapping=(
            "PyTorch shape errors read like this check; adding your own `assert x.shape[-1] == w.shape[0]` at the "
            "boundary saves a long debugging session."
        ),
    ),
    89: dict(
        topic="Review: tensors and the forward pass checklist",
        idea=(
            "Today is a review, so the goal is to connect the pieces rather than add a new one. The chain runs like "
            "this: data becomes nested lists with shapes, a layer multiplies by weights and adds a bias, "
            "broadcasting aligns the bias with the feature axis, an activation bends the result, and the output "
            "layer produces scores. For classification, softmax converts scores into probabilities with the maximum "
            "subtracted first for stability, and a loss reduces predictions and targets to one number. Every link in "
            "that chain has a shape you can state in advance, and most bugs are a link where the shape or the "
            "arithmetic care was wrong. The checklist worth memorising is short: know the shape at each stage, keep "
            "the batch axis first, check that inner dimensions agree, shift before exponentiating, and test every "
            "function on a case with a known answer. If you can walk one batch through the whole pipeline on paper "
            "and predict the output, you understand the forward pass. Today you run a compact pipeline end to end, "
            "print the shape and a summary value after each stage, and assert that the hidden activations and loss "
            "match what you expect. That assertion is a small contract that catches many mistakes at once."
        ),
        code=(
            'import math\n'
            '\n'
            'def relu(x):\n'
            '    return x if x > 0 else 0.0\n'
            '\n'
            'def softmax(scores):\n'
            '    shifted = [s - max(scores) for s in scores]\n'
            '    exps = [math.exp(s) for s in shifted]\n'
            '    total = sum(exps)\n'
            '    return [round(e / total, 4) for e in exps]\n'
            '\n'
            'def mse(predictions, targets):\n'
            '    total = sum((p - t) ** 2 for p, t in zip(predictions, targets))\n'
            '    return round(total / len(predictions), 4)\n'
            '\n'
            'weights = [[1, -1], [0, 1]]\n'
            'bias = [0, 1]\n'
            'batch = [[1, 2], [3, 0]]\n'
            'hidden = [[round(relu(sum(v * w for v, w in zip(row, w_row)) + b), 4)\n'
            '           for w_row, b in zip(weights, bias)] for row in batch]\n'
            'print("input shape:", (len(batch), len(batch[0])))\n'
            'print("hidden shape:", (len(hidden), len(hidden[0])))\n'
            'print("hidden:", hidden)\n'
            'for scores in hidden:\n'
            '    print("scores", scores, "probs", softmax(scores))\n'
            'print("loss:", mse([row[0] for row in hidden], [0, 3]))\n'
            '\n'
            'assert softmax([0, 0]) == [0.5, 0.5]\n'
            'print("review: shapes, activation, softmax, loss, all in one pass")'
        ),
        variant_b="add a third input row and confirm every stage keeps the leading batch axis",
        variant_c="replace ReLU with identity, rerun the pipeline, and show which printed stage changes",
        mistakes=[
            "Checking the final number without confirming each intermediate shape.",
            "Applying softmax before the loss when the loss expects logits for stability.",
            "Forgetting the max subtraction and trusting a pipeline that works only on small scores.",
        ],
        q1=(
            "What are the stages of the forward pass checklist in order?",
            "Shapes, layer weights plus bias, broadcasting, activation, output scores, stable softmax, then a batch-wise loss.",
        ),
        homework=(
            "Write `pipeline(batch, weights, bias)` that computes hidden activations with ReLU, returns softmax "
            "probabilities per row and the mse against a target list. Print the shape and values of every stage, "
            "assert the probabilities sum to one, and comment which line keeps the batch axis intact."
        ),
        patterns=["def pipeline", "softmax", "print("],
        mapping=(
            "This is the skeleton of every PyTorch forward pass: shapes in, linear plus bias, activation, logits, "
            "then a loss; the checklist survives even when the layers become prebuilt modules."
        ),
    ),
})
