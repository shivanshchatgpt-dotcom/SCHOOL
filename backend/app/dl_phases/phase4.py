"""Convolution and sequences, days 120-134: local structure, recurrence, attention.

The same discipline as the foundations phase: every idea is a small list
operation written with explicit loops, stdlib only, offline and deterministic.
Shapes are asserted, outputs are rounded, and the printed result is short enough
to check by hand before trusting any framework version of it.
"""

PHASE = (
    "Convolution and Sequences",
    "See how local filters, recurrent state and attention turn structured data into vectors, and check every shape by hand.",
    {
        120: dict(
            topic="Orientation: structure in data",
            idea=(
                "Real data is not a bag of independent numbers; it has neighbourhoods, and most of the meaning "
                "lives in them. In an image, a pixel says little alone, but the pixel next to it tells you about "
                "edges, corners and textures. In audio, a sample matters because of the samples beside it. A plain "
                "fully connected layer throws this structure away: it flattens the input into one long vector and "
                "gives every position its own weight, so moving the same pattern one step sideways looks like a "
                "completely new input. Convolution fixes that by making a small filter look at local windows and "
                "reusing the same weights everywhere. Before writing any convolution, it helps to see the "
                "structure explicitly. Today you take a short one-dimensional signal and measure how it changes "
                "from position to position. Large changes mark boundaries between regions, small changes mark "
                "smooth stretches. That difference pattern is exactly the kind of local feature a filter will later "
                "detect. The exercise is deliberately simple and has no learning and no framework, just a list and "
                "a loop. Once you can read local structure from a list, a kernel, a stride and a feature map all "
                "become natural consequences rather than library jargon."
            ),
            code=(
                'signal = [1, 2, 3, 4, 0, 0, 1, 2]\n'
                '\n'
                'changes = []\n'
                'for i in range(len(signal) - 1):\n'
                '    changes.append(signal[i + 1] - signal[i])\n'
                '\n'
                'print("signal:", signal)\n'
                'print("adjacent changes:", changes)\n'
                'print("large jumps:", [i for i, d in enumerate(changes) if abs(d) > 1])\n'
                '\n'
                'assert changes[3] == -4\n'
                'print("local differences reveal where the signal changes regime")'
            ),
            variant_b="use a signal with two separate jumps and check that both boundaries are reported",
            variant_c="smooth the signal by replacing each value with its neighbour average and show the jumps shrink",
            mistakes=[
                "Treating each position as independent, so a pattern that shifts by one looks like a new input.",
                "Flattening a structured signal too early and losing which values were neighbours.",
                "Confusing a large value with a large change; boundaries live in differences, not magnitudes.",
            ],
            q1=(
                "Why does measuring adjacent differences reveal structure that the raw values hide?",
                "Differences show where the signal changes regime, separating smooth stretches from boundaries regardless of the absolute values.",
            ),
            homework=(
                "Write `local_changes(values)` that returns the adjacent differences, plus `boundaries(values, "
                "threshold)` that returns the indices where the absolute change exceeds the threshold. Run both on "
                "an eight-value signal with one sharp jump, print the differences and the boundary indices, and "
                "assert that the jump is found exactly once."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "A convolutional layer learns exactly these local difference patterns, sharing one small kernel "
                "across every position instead of measuring each neighbour pair separately."
            ),
        ),
        121: dict(
            topic="Convolution as a sliding dot product",
            idea=(
                "A convolution is a sliding dot product: a small list of weights called a kernel moves across a "
                "signal, and at each position you multiply the overlapping values by the kernel weights and sum "
                "them. The result is a new list, the feature map, whose length is the number of valid positions. If "
                "the signal has length n and the kernel has length k, there are n minus k plus one valid positions "
                "when you do not pad. The kernel encodes a pattern. A kernel like one, zero, minus one responds "
                "strongly where the signal rises or falls, so it acts as an edge detector; a kernel of equal "
                "weights computes a local average, so it smooths. The critical difference from a dense layer is "
                "weight sharing: the same kernel is used at every position, which is why convolution has few "
                "parameters and why a pattern detected at one location is detected everywhere. Today you implement "
                "convolution with two explicit loops and no libraries, run a three-tap edge kernel over a short "
                "signal, and check the arithmetic by hand. Keep the values small integers so every output is exact. "
                "Print the signal, the kernel and the feature map, and notice how a spike in the original signal "
                "becomes a pair of opposite responses in the output."
            ),
            code=(
                'def conv1d(signal, kernel):\n'
                '    out = []\n'
                '    for start in range(len(signal) - len(kernel) + 1):\n'
                '        total = 0\n'
                '        for i, weight in enumerate(kernel):\n'
                '            total += signal[start + i] * weight\n'
                '        out.append(total)\n'
                '    return out\n'
                '\n'
                'signal = [1, 2, 3, 2, 1, 0, 1, 2]\n'
                'kernel = [1, 0, -1]\n'
                'features = conv1d(signal, kernel)\n'
                '\n'
                'print("signal:", signal)\n'
                'print("kernel:", kernel)\n'
                'print("feature map:", features)\n'
                'assert features == [-2, 0, 2, 2, 0, -2]\n'
                'print("a convolution is a sliding dot product")'
            ),
            variant_b="replace the kernel with [1, 2, 1] and explain why the output is now a local weighted sum",
            variant_c="reverse the kernel and show that convolution flips the pattern relative to correlation",
            mistakes=[
                "Letting the window run off the end instead of stopping at the last fully covered position.",
                "Summing with the kernel reversed by accident and then misreading which side of an edge fires.",
                "Flattening the feature map before checking that its length equals n minus k plus one.",
            ],
            q1=(
                "What does each output value of a one-dimensional convolution represent?",
                "The dot product between the kernel and one local window of the signal, measuring how strongly that pattern matches there.",
            ),
            homework=(
                "Write `conv1d(signal, kernel)` returning the feature map with two explicit loops and no libraries. "
                "Run it on an eight-value signal with the edge kernel `[1, 0, -1]`, print the signal, kernel and "
                "result, then assert that the output length is the signal length minus the kernel length plus one."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "`nn.Conv1d` is this loop with learned kernels and batch dimensions added; the sliding-window "
                "arithmetic is unchanged when the model scales up."
            ),
        ),
        122: dict(
            topic="Padding and stride",
            idea=(
                "Padding and stride are the two knobs that control the size of a convolution's output. Padding adds "
                "zeros around the signal before the kernel slides, which lets the kernel treat the boundaries as if "
                "the signal continued. Without padding, edge positions are visited by fewer windows, so the output "
                "shrinks and boundary information is underused. Stride is how far the kernel jumps between "
                "positions. A stride of one visits every position and preserves resolution; a stride of two skips "
                "every other position and roughly halves the output. The size formula ties them together: output "
                "length equals input length plus twice the padding, minus the kernel length, divided by the stride, "
                "plus one, using floor division. That formula is worth memorising because it explains most "
                "unexpected shape errors in real models. Today you write a convolution function that accepts "
                "padding and stride, then run the same signal and kernel under three settings: valid, padded and "
                "strided. Print each output and the length predicted by the formula. The important habit is to "
                "predict the length before running the code. If your prediction and the printed length disagree, "
                "the bug is in your understanding of the formula, not in the library, and that is much cheaper to "
                "fix now."
            ),
            code=(
                'def conv1d(signal, kernel, padding=0, stride=1):\n'
                '    padded = [0] * padding + signal + [0] * padding\n'
                '    out = []\n'
                '    start = 0\n'
                '    while start + len(kernel) <= len(padded):\n'
                '        total = 0\n'
                '        for i, weight in enumerate(kernel):\n'
                '            total += padded[start + i] * weight\n'
                '        out.append(total)\n'
                '        start += stride\n'
                '    return out\n'
                '\n'
                'def out_len(n, k, padding, stride):\n'
                '    return (n + 2 * padding - k) // stride + 1\n'
                '\n'
                'signal = [1, 2, 3, 4, 3, 2]\n'
                'kernel = [1, 0, -1]\n'
                'print("valid :", conv1d(signal, kernel), "len", out_len(6, 3, 0, 1))\n'
                'print("padded:", conv1d(signal, kernel, 1, 1), "len", out_len(6, 3, 1, 1))\n'
                'print("stride:", conv1d(signal, kernel, 1, 2), "len", out_len(6, 3, 1, 2))\n'
                'assert len(conv1d(signal, kernel, 1, 2)) == out_len(6, 3, 1, 2)\n'
                'print("padding and stride set the output length")'
            ),
            variant_b="set padding to two and predict the output length before running the padded case",
            variant_c="use stride three on the same signal and explain where the skipped positions go",
            mistakes=[
                "Adding padding on one side only, so the output length does not match the two-sided formula.",
                "Forgetting that stride sits in the denominator and therefore shrinks the output faster than padding grows it.",
                "Assuming a stride-two output is exactly half the input when the final window is incomplete.",
            ],
            q1=(
                "How do padding and stride change the output length of a convolution?",
                "Padding adds positions and grows the output, while stride skips positions and shrinks it; both appear in the same floor-division formula.",
            ),
            homework=(
                "Write `conv1d(signal, kernel, padding, stride)` plus `output_length(n, k, padding, stride)`. Run "
                "the same six-value signal under valid, padded and stride-two settings, print each output with its "
                "predicted length, and assert that every printed length matches the formula."
            ),
            patterns=["def ", "while ", "print("],
            mapping=(
                "Real CNN configurations are chosen from this formula, and reading a model diagram means recalculating "
                "each layer's spatial size with the same padding and stride arithmetic."
            ),
        ),
        123: dict(
            topic="Pooling",
            idea=(
                "Pooling reduces a feature map by summarising small neighbourhoods, and it does so without any "
                "learned weights. Max pooling takes the largest value in each window, keeping the strongest "
                "response to a pattern. Mean pooling averages the window, keeping a smoothed summary. Both shrink "
                "the signal, which lowers computation and makes later layers look at a wider span of the original "
                "input. Pooling also adds a small amount of translation robustness: if a feature shifts by one "
                "position inside a window, the maximum often stays the same. The trade-off is resolution: pooling "
                "throws away precise location, so too much of it makes tasks that need exact positions, like "
                "segmentation, harder. Today you implement max pooling and mean pooling with explicit loops over "
                "non-overlapping windows, run both on the same short feature map, and compare. Pick a stride equal "
                "to the window size so the windows tile the input exactly; otherwise the final partial window "
                "needs a rule, and silent disagreement about that rule is a common bug. Keep the numbers small and "
                "round any averages. Print the input, both pooled outputs, and assert that the max-pooled list is "
                "never larger than the input. That assert is the beginning of shape discipline."
            ),
            code=(
                'def max_pool(values, size):\n'
                '    out = []\n'
                '    for start in range(0, len(values) - size + 1, size):\n'
                '        out.append(max(values[start:start + size]))\n'
                '    return out\n'
                '\n'
                'def mean_pool(values, size):\n'
                '    out = []\n'
                '    for start in range(0, len(values) - size + 1, size):\n'
                '        window = values[start:start + size]\n'
                '        out.append(round(sum(window) / size, 2))\n'
                '    return out\n'
                '\n'
                'features = [1, 3, 2, 4, 0, 5, 2, 1]\n'
                'print("features:", features)\n'
                'print("max pool:", max_pool(features, 2))\n'
                'print("mean pool:", mean_pool(features, 2))\n'
                'assert max_pool(features, 2) == [3, 4, 5, 2]\n'
                'assert len(max_pool(features, 2)) <= len(features)\n'
                'print("pooling summarises each window without learning weights")'
            ),
            variant_b="use window size four and print both pooled lists, checking the halved length",
            variant_c="make one feature huge and show that it survives max pooling but barely moves the mean",
            mistakes=[
                "Stepping by one instead of by the window size, which creates overlapping windows and a longer output than intended.",
                "Silently dropping or padding the last partial window without deciding the rule explicitly.",
                "Applying pooling before checking the feature map length, so the resulting shape surprises later layers.",
            ],
            q1=(
                "What is the difference between max pooling and mean pooling?",
                "Max pooling keeps the strongest value in each window while mean pooling averages the window; the first sharpens, the second smooths.",
            ),
            homework=(
                "Write `max_pool(values, size)` and `mean_pool(values, size)` using explicit window loops. Run both "
                "on an eight-value feature map with size two, print the two pooled lists, and assert that the "
                "max-pooled list is no longer than the input and that each output came from its own window."
            ),
            patterns=["def ", "range", "print("],
            mapping=(
                "PyTorch's `MaxPool1d` and `AvgPool1d` implement this same tiling; the window and stride choices are "
                "where most pooling shape bugs originate."
            ),
        ),
        124: dict(
            topic="Channels and feature maps",
            idea=(
                "Real inputs have channels. A colour image has red, green and blue planes; an audio feature might "
                "have several frequency bands. A convolution layer therefore receives several input channels and "
                "produces several output channels. Each output channel has its own kernel, and that kernel has one "
                "small matrix per input channel. At every position the layer multiplies each input channel by the "
                "corresponding kernel slice, sums across channels, and adds a bias. This is why a convolution over "
                "three input channels with sixty-four output channels has sixty-four separate three-dimensional "
                "kernels, not one. The output is a stack of feature maps, one per filter, and each map records where "
                "that filter's pattern fired. Early filters often learn edges, later ones combine edges into "
                "textures and parts, but the mechanics are the same at every depth. Today you build a tiny "
                "two-channel signal and two filters, run the explicit loop, and print both feature maps. Watch the "
                "summation across channels: skipping it, or pairing the wrong channel with the wrong kernel slice, "
                "produces plausible but wrong numbers. Keep the data to a handful of positions so you can check one "
                "output by hand. The mental model to keep is that channels are stacked, not concatenated, and a "
                "filter always sees all of them."
            ),
            code=(
                'def conv_channels(channels, kernels, bias):\n'
                '    length = len(channels[0]) - len(kernels[0][0]) + 1\n'
                '    out = []\n'
                '    for f, kernel in enumerate(kernels):\n'
                '        feature = []\n'
                '        for start in range(length):\n'
                '            total = bias[f]\n'
                '            for c, channel in enumerate(channels):\n'
                '                for i, weight in enumerate(kernel[c]):\n'
                '                    total += channel[start + i] * weight\n'
                '            feature.append(total)\n'
                '        out.append(feature)\n'
                '    return out\n'
                '\n'
                'channels = [[1, 2, 3, 2, 1], [0, 1, 2, 1, 0]]\n'
                'kernels = [[[1, 0], [0, 1]], [[0, 1], [1, 0]]]\n'
                'maps = conv_channels(channels, kernels, [0, 1])\n'
                'for index, feature in enumerate(maps):\n'
                '    print("map", index, feature)\n'
                'assert maps[0] == [2, 4, 4, 2]\n'
                'print("each filter sums over all input channels")'
            ),
            variant_b="add a third input channel of zeros and confirm the feature maps do not change",
            variant_c="swap the two kernel slices and show that the second feature map becomes the first",
            mistakes=[
                "Summing only the first input channel, so the filter ignores most of its input.",
                "Pairing kernel slices with channels in the wrong order, which yields plausible but wrong maps.",
                "Confusing the number of output channels with the number of input channels in the parameter count.",
            ],
            q1=(
                "How does one output channel combine several input channels?",
                "Its filter has one kernel slice per input channel, and the layer sums the per-channel products at each position before adding a bias.",
            ),
            homework=(
                "Write `conv_channels(channels, kernels, bias)` that loops over filters, input channels and kernel "
                "taps. Run two two-value kernels over two five-value input channels, print each feature map, and "
                "assert that each output channel sums contributions from both input channels rather than only the "
                "first."
            ),
            patterns=["def ", "enumerate", "print("],
            mapping=(
                "`nn.Conv2d` stores a weight tensor of shape out-channels by in-channels by height by width; this "
                "loop is that tensor's forward pass written out."
            ),
        ),
        125: dict(
            topic="CNN shape accounting",
            idea=(
                "Shape accounting is the skill that separates people who debug CNNs quickly from people who guess. "
                "Given an input height and width, a kernel size, a padding and a stride, the output size follows one "
                "formula per spatial dimension: floor of input plus twice padding minus kernel, divided by stride, "
                "plus one. A convolution with kernel three, padding one and stride one keeps the spatial size "
                "unchanged, which is why it is so common. The same formula applies to pooling if you treat pooling "
                "as a convolution with no weights, with the important detail that pooling usually has no padding. "
                "Parameter counts follow a separate rule: kernel height times kernel width times input channels "
                "times output channels, plus one bias per output channel. Mixing up output channels and input "
                "channels is the classic mistake, and it only shows up later as a runtime error in a framework. "
                "Today you write functions that compute output size and parameter count, then print a small table "
                "for several configurations. Predict each row before running the code. The aim is not to memorise "
                "numbers but to make the arithmetic automatic, so that when a real model reports an unexpected "
                "shape you can locate the offending layer in seconds rather than adding print statements "
                "everywhere."
            ),
            code=(
                'def out_size(size, kernel, padding, stride):\n'
                '    return (size + 2 * padding - kernel) // stride + 1\n'
                '\n'
                'def params(kernel, in_channels, out_channels):\n'
                '    return kernel * kernel * in_channels * out_channels + out_channels\n'
                '\n'
                'configs = [(8, 3, 0, 1), (8, 3, 1, 1), (8, 3, 1, 2), (8, 5, 2, 2)]\n'
                'for size, kernel, padding, stride in configs:\n'
                '    result = out_size(size, kernel, padding, stride)\n'
                '    print("in", size, "k", kernel, "p", padding, "s", stride, "->", result)\n'
                '\n'
                'print("params 3x3, 3->8:", params(3, 3, 8))\n'
                'assert out_size(8, 3, 1, 1) == 8\n'
                'assert params(3, 3, 8) == 3 * 3 * 3 * 8 + 8\n'
                'print("shape and parameter arithmetic before any training")'
            ),
            variant_b="add a second convolution after the first and compute the size after both layers",
            variant_c="try kernel seven on an input of size six and show that the formula gives zero positions",
            mistakes=[
                "Swapping input and output channel counts in the parameter formula.",
                "Forgetting the twice-padding term and then blaming the framework for a shrunk output.",
                "Using float division and rounding instead of floor division when the window does not divide evenly.",
            ],
            q1=(
                "What is the output-size formula for one spatial dimension of a convolution?",
                "Floor of input plus twice padding minus kernel, all divided by stride, plus one.",
            ),
            homework=(
                "Write `output_size(size, kernel, padding, stride)` and `parameter_count(kernel, in_channels, "
                "out_channels)`. Print a four-row table of configurations, predict each output size before "
                "running, and assert both a same-size configuration and the parameter count for a 3x3 kernel "
                "mapping three channels to eight."
            ),
            patterns=["def ", "//", "print("],
            mapping=(
                "This is the arithmetic behind every `Conv2d` layer in a model summary; doing it by hand turns shape "
                "errors from mysteries into one-line corrections."
            ),
        ),
        126: dict(
            topic="Sequences and windows",
            idea=(
                "Sequences break the assumption that every example has a fixed size. A sentence can have five words "
                "or fifty, a recording can run for one second or ten minutes, and the order of the elements carries "
                "meaning that a bag of features destroys. The first practical move is windowing: slide a "
                "fixed-length window over the sequence and use each window as one example. If you are predicting the "
                "next value, the window is the input and the following value is the target. The window length is a "
                "modelling choice, not a property of the data; it decides how much context the model can see. A "
                "stride controls overlap: a stride of one produces many overlapping windows and more training "
                "examples, while a stride equal to the window length produces disjoint chunks. Windowing also "
                "handles variable-length inputs by turning them into many fixed-length ones, at the cost of edge "
                "effects at the sequence boundaries, where the window is short or the target is missing. Today you "
                "write a windowing function over a short numeric sequence, print the inputs and targets, and assert "
                "the count. Keep the sequence tiny so you can verify each pair by eye. The habit to build is "
                "explicit indexing: know exactly which positions are input and which is target, because off-by-one "
                "errors here are silent and poison every later step."
            ),
            code=(
                'def make_windows(sequence, size):\n'
                '    inputs = []\n'
                '    targets = []\n'
                '    for start in range(len(sequence) - size):\n'
                '        inputs.append(sequence[start:start + size])\n'
                '        targets.append(sequence[start + size])\n'
                '    return inputs, targets\n'
                '\n'
                'sequence = [1, 2, 3, 4, 5, 6, 7]\n'
                'windows, targets = make_windows(sequence, 3)\n'
                'for window, target in zip(windows, targets):\n'
                '    print(window, "->", target)\n'
                'assert len(windows) == len(sequence) - 3\n'
                'assert windows[0] == [1, 2, 3] and targets[0] == 4\n'
                'print("windowing turns one sequence into many fixed-size examples")'
            ),
            variant_b="use a stride of two and print only the disjoint windows and their targets",
            variant_c="predict two steps ahead instead of one and explain which part of the window logic changes",
            mistakes=[
                "Reading one value past the sequence end because the loop bound forgot the target position.",
                "Letting the target overlap the input window, so the model is asked to predict something it can already see.",
                "Using a window longer than the sequence and silently producing no examples.",
            ],
            q1=(
                "Why does windowing make a variable-length sequence usable by a fixed-size model?",
                "It turns the sequence into many fixed-length input windows, each paired with a target, so every example has the same shape.",
            ),
            homework=(
                "Write `make_windows(sequence, size)` returning a list of input windows and a parallel list of "
                "next-value targets. Run it on a seven-value sequence with window three, print every pair, and "
                "assert that the two lists have equal length and that no target overlaps its own input window."
            ),
            patterns=["def ", "range", "print("],
            mapping=(
                "Data loaders for time series and language models do exactly this sliding-window indexing before "
                "batching, and the target offset is where most silent label bugs live."
            ),
        ),
        127: dict(
            topic="A recurrent update",
            idea=(
                "A recurrent network processes a sequence one element at a time while carrying a hidden state, a "
                "vector of numbers that summarises everything seen so far. The update is small: combine the current "
                "input with the previous hidden state using two weight matrices and a bias, pass the result through "
                "a non-linearity such as tanh, and that becomes the new hidden state. The same weights are reused "
                "at every step, so the model can handle sequences of any length without growing its parameter "
                "count. That sharing is the recurrent analogue of convolution's weight sharing, and it is the "
                "source of both the model's power and its weakness. The power is memory: information from early "
                "steps can influence later ones. The weakness is that gradients flowing back through many steps "
                "tend to shrink or explode, which is why long-range dependencies are hard and why gated variants "
                "exist. Today you implement one recurrent step with explicit loops and run it over a short sequence "
                "of numbers, printing the hidden state after each position. Initialise the hidden state to zeros so "
                "the first output is reproducible and easy to check by hand. Round the values before printing. Look "
                "at how the state changes fastest early and then settles; that is the memory filling up."
            ),
            code=(
                'def tanh(x):\n'
                '    e = 2.718281828459045 ** (2 * x)\n'
                '    return (e - 1) / (e + 1)\n'
                '\n'
                'def step(hidden, value, w_h, w_x, bias):\n'
                '    return tanh(w_h * hidden + w_x * value + bias)\n'
                '\n'
                'sequence = [1, 0, 1, 0]\n'
                'hidden = 0.0\n'
                'w_h, w_x, bias = 0.5, 1.0, -0.2\n'
                'for position, value in enumerate(sequence):\n'
                '    hidden = round(step(hidden, value, w_h, w_x, bias), 4)\n'
                '    print("position", position, "input", value, "hidden", hidden)\n'
                '\n'
                'assert -1.0 < hidden < 1.0\n'
                'print("the hidden state is the sequence summary carried forward")'
            ),
            variant_b="set the recurrent weight to zero and show that each state depends only on the current input",
            variant_c="run the same sequence twice without resetting and observe that the second pass starts from memory",
            mistakes=[
                "Resetting the hidden state inside the loop, which erases the memory the recurrence is supposed to carry.",
                "Using the new hidden state to update an old one before computing the current output, mixing two time steps.",
                "Forgetting the non-linearity, so the state grows without bound and stops acting like a summary.",
            ],
            q1=(
                "What two pieces of information does a recurrent update combine?",
                "The current input element and the previous hidden state, each with its own weight, plus a bias and a non-linearity.",
            ),
            homework=(
                "Write `rnn_step(hidden, value, w_h, w_x, bias)` using a hand-written tanh, then "
                "`run_rnn(sequence, w_h, w_x, bias)` that returns every hidden state. Run it on a four-value 0/1 "
                "sequence, print each state, and assert that every state stays strictly between minus one and one."
            ),
            patterns=["def ", "for ", "print("],
            mapping=(
                "`nn.RNN` and `nn.GRU` cells perform this update with matrices and gates; the single scalar version is "
                "the cleanest place to see what the hidden state carries."
            ),
        ),
        128: dict(
            topic="Sequence to vector",
            idea=(
                "Many sequence tasks need one vector at the end, not one vector per step. A sentiment classifier "
                "reads a review and emits a label; a keyword spotter listens to a clip and emits a class. The "
                "recurrent loop already produces a hidden state at every position, so the question is how to "
                "collapse that sequence of states into a single summary. The simplest choice is the last state, "
                "which works when the important information is near the end and the recurrence has not forgotten "
                "the beginning. A second choice is the mean of all states, which treats every position as equally "
                "important and is surprisingly strong on short sequences. A third is to keep all states and let a "
                "later layer decide. Each choice has a failure mode: the last state overweights recency, the mean "
                "blurs sharp events, and keeping everything costs memory. Today you run a tiny recurrence over a "
                "short input and compare the last hidden state with the mean hidden state, printing both. Then use "
                "each summary to make a trivial decision and see whether they agree. The exercise is about the "
                "interface between sequence processing and ordinary vector models: once you have one vector, every "
                "earlier tool, from a dense layer to a loss function, applies unchanged."
            ),
            code=(
                'def tanh(x):\n'
                '    e = 2.718281828459045 ** (2 * x)\n'
                '    return (e - 1) / (e + 1)\n'
                '\n'
                'def run(sequence, w_h=0.6, w_x=0.9):\n'
                '    hidden = 0.0\n'
                '    states = []\n'
                '    for value in sequence:\n'
                '        hidden = round(tanh(w_h * hidden + w_x * value), 4)\n'
                '        states.append(hidden)\n'
                '    return states\n'
                '\n'
                'sequence = [1, 0, 1, 1]\n'
                'states = run(sequence)\n'
                'last = states[-1]\n'
                'mean = round(sum(states) / len(states), 4)\n'
                'print("states:", states)\n'
                'print("last summary:", last)\n'
                'print("mean summary:", mean)\n'
                'assert len(states) == len(sequence)\n'
                'assert min(states) <= mean <= max(states)\n'
                'print("a sequence collapses to one vector before a dense decision")'
            ),
            variant_b="weight the states by position so later steps count more, then compare with the plain mean",
            variant_c="run a longer sequence and show that the last state and the mean summary diverge further",
            mistakes=[
                "Averaging states that were not reset between examples, which mixes separate sequences.",
                "Taking the last state before the loop finishes, so the sequence is only partly read.",
                "Claiming the mean preserves order when averaging is itself order-insensitive.",
            ],
            q1=(
                "What is the trade-off between using the last hidden state and the mean of all hidden states?",
                "The last state favours recent information, while the mean treats all positions equally and can blur sharp events.",
            ),
            homework=(
                "Write `run_rnn(sequence)` returning the list of hidden states plus `last_state(states)` and "
                "`mean_state(states)`. Run it on a four-value sequence, print both summaries, and assert that the "
                "mean lies between the smallest and largest hidden state so you know it is a real average."
            ),
            patterns=["def ", "sum", "print("],
            mapping=(
                "Sequence classifiers in practice pool the final states or use a learned readout; choosing that "
                "pooling is a design decision with the same trade-offs you see here."
            ),
        ),
        129: dict(
            topic="Attention scores",
            idea=(
                "Attention starts by asking how relevant each position is to a query. You represent each position "
                "with a key vector and each query with its own vector, then take the dot product between the query "
                "and every key. A large positive dot product means the directions agree, so that position is "
                "relevant; a near-zero product means the query does not care about it; a negative product means "
                "disagreement. These raw numbers are called attention scores, and computing them is just a small "
                "matrix multiplication, or a set of explicit dot products. The scores are not yet weights: they can "
                "be any real number, and they do not sum to one. That is fine for ranking, but for mixing "
                "information you need a normalised distribution, which is the next lesson. The useful mental model "
                "today is retrieval. The query is what you are looking for, the keys are labels on stored items, "
                "and the score measures match quality. Unlike a recurrence, attention looks at all positions at "
                "once, so the path between distant positions is short and the computation parallelises well. The "
                "cost is that it has no built-in notion of order, which is why positional information must be added "
                "separately. Today you compute scores between one query and three keys by hand and sort them to see "
                "which key wins."
            ),
            code=(
                'def attention_scores(query, keys):\n'
                '    scores = []\n'
                '    for key in keys:\n'
                '        total = 0.0\n'
                '        for q, k in zip(query, key):\n'
                '            total += q * k\n'
                '        scores.append(round(total, 2))\n'
                '    return scores\n'
                '\n'
                'query = [1.0, 0.0]\n'
                'keys = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]\n'
                'scores = attention_scores(query, keys)\n'
                'print("query:", query)\n'
                'print("keys:", keys)\n'
                'print("scores:", scores)\n'
                'print("best key:", scores.index(max(scores)))\n'
                'assert scores == [1.0, 0.0, 1.0]\n'
                'print("attention scores rank keys by dot-product match")'
            ),
            variant_b="change the query to [1, 1] and show that all three scores rise but the ranking changes",
            variant_c="negate the query and explain why the best match becomes the worst key",
            mistakes=[
                "Treating raw scores as weights even though they can be negative and do not sum to one.",
                "Computing the dot product without matching the query and key dimensions, so zip silently truncates.",
                "Forgetting that a high score means alignment, not necessarily a frequent or important token.",
            ],
            q1=(
                "What does the dot product between a query and a key measure?",
                "Their alignment: a large positive value means the two vectors point in similar directions, so the key is relevant to the query.",
            ),
            homework=(
                "Write `attention_scores(query, keys)` that computes one dot product per key with explicit loops. "
                "Run it with a two-dimensional query and three keys, print each score beside its key index, and "
                "assert that the key most aligned with the query receives the largest score."
            ),
            patterns=["def ", "zip", "print("],
            mapping=(
                "Scaled dot-product attention computes a whole matrix of these scores at once; the dot-product "
                "similarity and its ranking behaviour are exactly the same."
            ),
        ),
        130: dict(
            topic="Softmax attention weights",
            idea=(
                "Raw attention scores need to become a weighted average, and softmax is the standard way to do it. "
                "Softmax exponentiates each score, which makes every value positive, and then divides by the sum, "
                "which makes the values add to one. Exponentiating is not arbitrary: it turns differences into "
                "ratios, so a score that is two points higher gets a weight roughly seven times larger, while a "
                "small lead stays a small lead. The result is a probability distribution over positions. Once you "
                "have weights, the attention output is the weighted sum of the value vectors, one value per "
                "position. A position with weight near one dominates the output; a position with weight near zero "
                "is effectively ignored. This is the core of scaled dot-product attention, with the scale factor in "
                "the denominator keeping the scores from growing too large as dimensions increase. Today you take a "
                "few hand-written scores, apply softmax with explicit loops, print the weights, and use them to mix "
                "three small value vectors. Check that the weights sum to one within rounding, and notice that the "
                "largest score does not get all the mass unless it is far ahead. That distinction between ranking "
                "and weighting is the lesson."
            ),
            code=(
                'def softmax(scores):\n'
                '    top = max(scores)\n'
                '    exps = []\n'
                '    for score in scores:\n'
                '        exps.append(2.718281828459045 ** (score - top))\n'
                '    total = sum(exps)\n'
                '    return [round(value / total, 3) for value in exps]\n'
                '\n'
                'def mix(weights, values):\n'
                '    out = []\n'
                '    for position in range(len(values[0])):\n'
                '        total = 0.0\n'
                '        for index, weight in enumerate(weights):\n'
                '            total += weight * values[index][position]\n'
                '        out.append(round(total, 3))\n'
                '    return out\n'
                '\n'
                'scores = [1.0, 2.0, 0.5]\n'
                'weights = softmax(scores)\n'
                'values = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]\n'
                'print("scores:", scores)\n'
                'print("weights:", weights, "sum:", round(sum(weights), 3))\n'
                'print("context:", mix(weights, values))\n'
                'assert abs(sum(weights) - 1.0) < 0.01\n'
                'print("softmax turns scores into weights that mix the values")'
            ),
            variant_b="scale all scores up by ten and show that the distribution becomes much sharper",
            variant_c="pass equal scores and confirm that every position receives the same weight",
            mistakes=[
                "Exponentiating without subtracting the maximum, which overflows for large scores.",
                "Normalising before exponentiating, so negative scores do not become positive weights.",
                "Mixing the raw scores instead of the normalised weights, which stops the output being a weighted average.",
            ],
            q1=(
                "Why does softmax exponentiate the scores before normalising?",
                "Exponentiation makes every score positive and turns score differences into multiplicative ratios, so the result is a valid distribution that sharpens with larger differences.",
            ),
            homework=(
                "Write `softmax(scores)` and `weighted_sum(weights, values)` with explicit loops only. Run softmax "
                "on three scores, print the weights and their sum, mix three two-dimensional values, and assert "
                "that the weights are positive and sum to one within rounding error."
            ),
            patterns=["def ", "sum", "print("],
            mapping=(
                "Every transformer attention block applies softmax to scaled scores before mixing values; the "
                "stability trick of subtracting the maximum is identical in production code."
            ),
        ),
        131: dict(
            topic="Positional ideas",
            idea=(
                "Attention and recurrence both process a set of positions, but neither knows where those positions "
                "are unless you tell it. The dot product between a query and a key depends only on their values, so "
                "shuffling the sequence would leave the scores unchanged. Convolution has an implicit sense of "
                "position through its sliding window, but attention does not. Positional information fixes this by "
                "adding or concatenating a position-dependent vector to each token representation before attention "
                "runs. A common choice uses sine and cosine waves of different frequencies, which gives every "
                "position a distinct pattern and lets the model generalise to lengths it never saw. Another choice "
                "learns a separate embedding per position, which is simpler but cannot extrapolate beyond the "
                "training length. The key point is that position is data, not magic: you compute a vector and add "
                "it. Today you build simple position vectors from the index, add them to the same token embedding at "
                "two positions, and print the results to show that identical tokens become distinguishable. Do the "
                "arithmetic by hand for one coordinate. The exercise also shows the cost: the model must learn to "
                "separate value information from position information, which is why the scale of the added vector "
                "matters."
            ),
            code=(
                'import math\n'
                '\n'
                'def position_vector(position, size=4):\n'
                '    vector = []\n'
                '    for index in range(size):\n'
                '        angle = position / (2 ** (index // 2))\n'
                '        if index % 2 == 0:\n'
                '            vector.append(round(math.sin(angle), 3))\n'
                '        else:\n'
                '            vector.append(round(math.cos(angle), 3))\n'
                '    return vector\n'
                '\n'
                'embedding = [0.5, 0.5, 0.5, 0.5]\n'
                'for position in (0, 1):\n'
                '    encoded = [round(e + p, 3) for e, p in zip(embedding, position_vector(position))]\n'
                '    print("position", position, "->", encoded)\n'
                'assert position_vector(0) != position_vector(1)\n'
                'print("position information must be added; attention has none by itself")'
            ),
            variant_b="use a longer sequence and confirm that every position vector is distinct",
            variant_c="scale the position vector by ten and explain why the token values may become harder to recover",
            mistakes=[
                "Adding the same position vector to every token, which provides no positional signal at all.",
                "Using positions that repeat within the training length, so two different tokens become indistinguishable.",
                "Concatenating position after attention instead of before, so the scores never see the order.",
            ],
            q1=(
                "Why does attention need positional information added to its inputs?",
                "Its dot-product scores depend only on token values, so without a position signal a shuffled sequence produces the same attention weights.",
            ),
            homework=(
                "Write `position_vector(position, size)` using sine and cosine terms, then "
                "`add_positions(embeddings, start)` that adds one vector per position. Run it on the same embedding "
                "at positions zero and one, print both results, and assert the two encoded vectors differ even "
                "though the input token is identical."
            ),
            patterns=["def ", "math", "print("],
            mapping=(
                "Transformers add sinusoidal or learned position embeddings to token embeddings before the first "
                "block, exactly as this loop does at toy scale."
            ),
        ),
        132: dict(
            topic="Comparing architectures",
            idea=(
                "Convolution, recurrence and attention are three answers to the same question: how do you let a "
                "model use context? A convolution sees a fixed local window, uses shared weights, and is cheap and "
                "parallel; stacking layers widens the window. A recurrence sees everything through a fixed-size "
                "state, processes steps in order, and is naturally sequential, which limits parallelism and makes "
                "long-range gradients fragile. Attention sees every position at once, weighs them by relevance, and "
                "parallelises well, but its cost grows with the square of the sequence length and it needs "
                "positional information. Comparing them on tiny inputs makes the trade-offs concrete. You can count "
                "parameters and operations for a one-layer version of each and see why a convolution is tiny, a "
                "recurrent layer is moderate, and attention is expensive at long lengths but constant in path "
                "length. You can also compare what each can represent: a convolution cannot relate two distant "
                "positions without depth, a recurrence can in principle but may forget, and attention can directly. "
                "Today you write a small comparison that prints parameter counts and a rough operation count for "
                "the same input length, then decide which architecture suits a local pattern task and which suits a "
                "long-range one. The goal is judgement, not memorising a table."
            ),
            code=(
                'def conv_params(kernel, in_channels, out_channels):\n'
                '    return kernel * in_channels * out_channels + out_channels\n'
                '\n'
                'def rnn_params(hidden, input_size, output_size):\n'
                '    return hidden * input_size + hidden * hidden + hidden + hidden * output_size\n'
                '\n'
                'def attention_params(width):\n'
                '    return 3 * width * width + width\n'
                '\n'
                'print("conv 3x1 8ch -> 8ch:", conv_params(3, 8, 8))\n'
                'print("rnn hidden 8, input 8:", rnn_params(8, 8, 8))\n'
                'print("attention width 8:", attention_params(8))\n'
                'assert conv_params(3, 8, 8) == 3 * 8 * 8 + 8\n'
                'print("local + shared vs sequential state vs global pairwise")'
            ),
            variant_b="double the hidden width and show which architecture's parameter count grows fastest",
            variant_c="compare the same three counts at sequence length four and at length sixteen",
            mistakes=[
                "Comparing parameter counts without noting that operation counts and path lengths differ too.",
                "Assuming attention is always better because it is newer, ignoring its quadratic sequence cost.",
                "Forgetting that convolution needs depth to relate distant positions, not a single wide layer.",
            ],
            q1=(
                "What is the main structural trade-off between convolution, recurrence and attention?",
                "Convolution is local and cheap, recurrence carries a sequential state, and attention is global and parallel but quadratic in sequence length.",
            ),
            homework=(
                "Write `conv_params(kernel, in_channels, out_channels)`, `rnn_params(hidden, input_size, "
                "output_size)` and `attention_params(width)`. Print all three counts for comparable small sizes, "
                "then write two sentences deciding which architecture suits a local edge pattern and which suits "
                "relating two distant positions."
            ),
            patterns=["def ", "print(", "return"],
            mapping=(
                "Choosing a backbone in practice is this comparison at scale: locality and inductive bias versus "
                "global mixing and data requirements."
            ),
        ),
        133: dict(
            topic="Debugging a sequence model",
            idea=(
                "Sequence models fail in ways that are quiet, and debugging them is mostly about making shapes and "
                "lengths explicit. The classic bug is an off-by-one: the input window is length three but the code "
                "reads four values, or the target is taken from the same position as the last input, so the model is "
                "asked to predict something it has already seen. Another is a length mismatch between a sequence and "
                "its mask or labels, which either raises an index error or, worse, silently pairs the wrong target "
                "with the wrong input. A third is a hidden state carried between independent examples, which leaks "
                "information and makes evaluation optimistic. The cure is boring: assert lengths, assert that "
                "inputs and targets align, and reset state at every example boundary. Today you write a small "
                "sequence function with explicit checks, run a correct case, then run a deliberately broken case and "
                "catch the error. Print the error message so you see the failure mode. Do not test only the happy "
                "path; the value of a guard is what it does when the data is wrong. This habit carries directly to "
                "real frameworks, where shape errors surface late and the stack trace points at a layer far from the "
                "actual mistake."
            ),
            code=(
                'def safe_windows(sequence, size):\n'
                '    if len(sequence) <= size:\n'
                '        raise ValueError("sequence must be longer than the window")\n'
                '    pairs = []\n'
                '    for start in range(len(sequence) - size):\n'
                '        window = sequence[start:start + size]\n'
                '        target = sequence[start + size]\n'
                '        assert len(window) == size\n'
                '        pairs.append((window, target))\n'
                '    return pairs\n'
                '\n'
                'print("correct:", safe_windows([1, 2, 3, 4, 5], 2))\n'
                'try:\n'
                '    safe_windows([1, 2], 3)\n'
                'except ValueError as error:\n'
                '    print("caught:", error)\n'
                'assert len(safe_windows([1, 2, 3, 4], 2)) == 2\n'
                'print("guards turn silent misalignment into loud failures")'
            ),
            variant_b="add a check that the target index is inside the sequence and show which guard fires first",
            variant_c="reset hidden state between two examples and show that the second result stops depending on the first",
            mistakes=[
                "Checking only the first window's length and trusting every later window to match.",
                "Carrying hidden state across independent examples, which leaks information between them.",
                "Catching an exception and printing nothing, so the failure disappears instead of teaching you the bug.",
            ],
            q1=(
                "Why is an off-by-one target offset in windowing so dangerous?",
                "It silently pairs each input with a target it already contains or the wrong next value, so training looks normal while learning the wrong mapping.",
            ),
            homework=(
                "Write `safe_windows(sequence, size)` that validates the sequence length and raises `ValueError` "
                "when it is too short, then returns aligned input-target pairs. Run one correct case and one "
                "too-short case inside try/except, print the caught message, and assert that the correct case's "
                "targets never reuse input positions."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "Production sequence pipelines log and assert lengths at the dataset boundary because a silent "
                "off-by-one costs far more than a failed batch."
            ),
        ),
        134: dict(
            topic="Review: convolution and sequences checklist",
            idea=(
                "Today is a checklist and review day, not a day for a new idea. The goal is to prove that you can run the whole small "
                "pipeline yourself: take a signal, convolve it, pool it, collapse it to a vector, and score it, "
                "while checking shapes at every step. Each stage has one thing worth verifying. After convolution, "
                "the output length must match the formula. After pooling, every window must be complete and the "
                "length must be the floor of the input divided by the window. After flattening, the feature count "
                "must equal the product of the remaining dimensions. For a sequence model, the checks are "
                "different: windows must align with targets, the hidden state must reset between examples, and "
                "attention weights must sum to one. Write these as asserts, not comments, because an assertion fails "
                "loudly and a comment does not. The review also asks you to explain each stage in one sentence, "
                "which is the real test of understanding. If you cannot say what a stage does without reading its "
                "code, you do not yet own the idea. Keep the example tiny so the whole pipeline fits on one screen "
                "and the printed numbers can be checked by hand."
            ),
            code=(
                'def conv1d(signal, kernel):\n'
                '    out = []\n'
                '    for start in range(len(signal) - len(kernel) + 1):\n'
                '        total = 0\n'
                '        for i, weight in enumerate(kernel):\n'
                '            total += signal[start + i] * weight\n'
                '        out.append(total)\n'
                '    return out\n'
                '\n'
                'def max_pool(values, size):\n'
                '    out = []\n'
                '    for start in range(0, len(values) - size + 1, size):\n'
                '        out.append(max(values[start:start + size]))\n'
                '    return out\n'
                '\n'
                'signal = [1, 2, 3, 2, 1, 0, 1, 2]\n'
                'kernel = [1, 0, -1]\n'
                'features = conv1d(signal, kernel)\n'
                'pooled = max_pool(features, 2)\n'
                'print("signal:", signal)\n'
                'print("conv:", features)\n'
                'print("pool:", pooled)\n'
                'print("vector length:", len(pooled))\n'
                'assert len(features) == len(signal) - len(kernel) + 1\n'
                'assert len(pooled) == len(features) // 2\n'
                'assert len(pooled) == 3\n'
                'print("pipeline checked: conv shape, pool shape, flattened size")'
            ),
            variant_b="reuse the same pipeline on a six-value signal and recompute every expected length first",
            variant_c="add a mean-pool branch beside max pooling and decide which summary a classifier should use",
            mistakes=[
                "Checking the final vector length but not the intermediate feature-map length.",
                "Writing shape checks as comments, so a later edit can break them without any failure.",
                "Memorising the pipeline order without being able to explain what each stage contributes.",
            ],
            q1=(
                "What should you verify after each stage of a convolution pipeline?",
                "The output length against the formula, the pooled window count, and the flattened feature count against the product of the remaining dimensions.",
            ),
            homework=(
                "Write `pipeline(signal, kernel, pool_size)` that convolves, max-pools, flattens and prints each "
                "stage with its length. Run it on an eight-value signal, assert the convolution length, the pooled "
                "length and the flattened length against the formulas, and finish with one printed checklist line "
                "confirming every shape was checked."
            ),
            patterns=["def ", "assert", "print("],
            mapping=(
                "This checklist is the same one to run when a real CNN or sequence model raises a shape error: find "
                "the stage whose length stopped matching its formula."
            ),
        ),
    },
)
