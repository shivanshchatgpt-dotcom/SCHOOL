"""Backpropagation and gradients, days 90-104: derivatives in plain Python.

Every example is stdlib-only, offline and deterministic (fixed values or a
seeded `random.Random`, rounded outputs), so the applier can execute it and
produce the same result on every run. A gradient is computed analytically,
checked against a central finite difference, and only then used for an update.
That order — compute, check, step — is the habit this phase is built around.
"""

PHASE = (
    "Backpropagation and Gradients",
    "Build a parameter's gradient by hand, verify it numerically, and use it to take a correct update step.",
    {
        90: dict(
            topic="Orientation: learning is gradients",
            idea=(
                "Learning in a neural network means changing parameters so that a loss gets smaller, and the only "
                "reliable guide for that change is a gradient. A gradient is a derivative: at the current value of "
                "a parameter it says how fast the loss rises or falls, and in which direction. If the derivative is "
                "positive, increasing the weight increases the loss, so you decrease the weight; if the derivative "
                "is negative, you increase it. This single rule, applied to every parameter, is all that training "
                "does. The rest of this phase is about computing that derivative accurately, cheaply and safely. "
                "Today you do not train anything. You look at a simple loss curve and sample its slope at several "
                "weights using a central finite difference, which evaluates the loss slightly to either side and "
                "divides the change by the total step. Compare the sign of the slope with the loss values and notice "
                "that the slope always points uphill, toward larger loss. That is the whole orientation: a gradient "
                "is a local direction, not a promise about the far side of the curve. Training repeats the local "
                "decision many times, which is exactly why the step size, the learning rate, matters so much. Keep "
                "the numbers small and rounded."
            ),
            code=(
                'def loss(w):\n'
                '    return (w - 2.0) ** 2\n'
                '\n'
                'def slope(w, eps=1e-6):\n'
                '    return (loss(w + eps) - loss(w - eps)) / (2 * eps)\n'
                '\n'
                'for w in [0.0, 1.0, 2.0, 3.0, 4.0]:\n'
                '    print(f"w={w} loss={round(loss(w), 4)} slope={round(slope(w), 4)}")\n'
                '\n'
                'assert abs(slope(2.0)) < 1e-4\n'
                'assert slope(0.0) < 0 and slope(4.0) > 0\n'
                'print("a positive slope means increasing w raises the loss")'
            ),
            variant_b="shift the loss minimum to 5 and confirm the slope is zero at the new minimum",
            variant_c="use a one-sided difference with eps=0.1 and compare how far it drifts from the central estimate",
            mistakes=[
                "Moving the weight in the direction of the gradient, which increases the loss.",
                "Reading a single slope value as a global property instead of a local one.",
                "Using a step so large that the finite difference measures curvature rather than slope.",
            ],
            q1=(
                "If the derivative of the loss with respect to a weight is negative, which way should the weight move?",
                "Increase it, because a negative slope means the loss falls as the weight rises, so moving up reduces the loss.",
            ),
            homework=(
                "Write `slope_table(w_start, w_end, step)` that prints the loss and central finite-difference slope "
                "for each weight in the range, and `sign_rule(slope)` that returns +1 or -1 for the direction that "
                "reduces the loss. Run it on a quadratic, print the table, and comment which line proves the zero "
                "slope at the minimum."
            ),
            patterns=["def ", "slope", "print("],
            mapping=(
                "This is the intuition behind `loss.backward()` and every optimiser step: a gradient supplies a "
                "local direction, and the training loop trusts it repeatedly."
            ),
        ),
        91: dict(
            topic="Derivatives by intuition",
            idea=(
                "A derivative is the instantaneous rate of change of a function, and the useful mental picture is a "
                "tangent line touching a curve at one point. For a function of one variable, the derivative at x "
                "tells you how much the output changes per unit change in x, in the limit of a tiny step. You do not "
                "need calculus notation to use this idea; you need two facts. First, common functions have known "
                "derivatives, such as three x squared for x cubed. Second, any derivative can be estimated "
                "numerically by evaluating the function just above and just below the point and dividing the "
                "difference by the distance between those evaluations. That estimate is called a finite difference, "
                "and the central version, using both sides, is more accurate than a one-sided version. Today you "
                "compare the analytic derivative of a cubic with its finite-difference estimate at several points. "
                "Where the curve is steep the derivative is large; where it flattens the derivative shrinks; at a "
                "minimum it crosses zero. Watching those three cases makes the derivative feel like a property of the "
                "shape rather than an abstract symbol. Print both values side by side and check that they agree to a "
                "few decimal places, then reason about why the estimate is not exact."
            ),
            code=(
                'def f(x):\n'
                '    return x ** 3\n'
                '\n'
                'def analytic(x):\n'
                '    return 3 * x ** 2\n'
                '\n'
                'def numeric(x, eps=1e-6):\n'
                '    return (f(x + eps) - f(x - eps)) / (2 * eps)\n'
                '\n'
                'for x in [0.0, 0.5, 1.0, 2.0]:\n'
                '    print(f"x={x} f={round(f(x), 4)} analytic={round(analytic(x), 4)} numeric={round(numeric(x), 4)}")\n'
                '\n'
                'assert abs(analytic(2.0) - numeric(2.0)) < 1e-4\n'
                'assert analytic(0.0) == 0.0\n'
                'print("the derivative is the local slope of the curve")'
            ),
            variant_b="differentiate x squared plus 2x and compare the analytic slope with the numeric one at x=3",
            variant_c="try eps=0.5 and show that the central estimate becomes visibly inaccurate",
            mistakes=[
                "Confusing the value of the function with the value of its slope.",
                "Using a one-sided difference and blaming the resulting bias on the function.",
                "Choosing epsilon so small that floating-point cancellation dominates the estimate.",
            ],
            q1=(
                "What does the derivative at a point tell you geometrically?",
                "The slope of the tangent line at that point, which is how fast the output changes per unit change in the input.",
            ),
            homework=(
                "Write `numeric_derivative(f, x, eps=1e-5)` and `check_derivative(f, analytic, points)` that prints "
                "both values and their absolute difference for each point. Test it on a cubic at three points and "
                "comment which line performs the central difference."
            ),
            patterns=["def ", "numeric", "print("],
            mapping=(
                "Frameworks differentiate exactly, but a finite difference is the independent reference used to "
                "verify that exact machinery when a model misbehaves."
            ),
        ),
        92: dict(
            topic="The chain rule",
            idea=(
                "The chain rule is the rule that lets you differentiate a function built out of other functions, and "
                "it is the single most important mechanical idea behind backpropagation. If a quantity z depends on "
                "y, and y depends on x, then a small change in x changes y by the local derivative of y with respect "
                "to x, and that change in y changes z by the local derivative of z with respect to y. The two effects "
                "multiply. In symbols, dz/dx equals dz/dy times dy/dx. The rule sounds trivial but it scales: a deep "
                "network is a long chain of such dependencies, and its gradient is the product of every local "
                "derivative along the path. A practical consequence is that order matters for reading, not for "
                "arithmetic; you can multiply the factors in any order, but you must not add them. Today you "
                "differentiate a squared linear function in two ways, by expanding it and by applying the chain rule "
                "factor by factor, then compare both with a finite difference. The factor-by-factor version is the "
                "one that generalises to a network, so make sure you can point at each factor and name what it "
                "represents. Write the factors down before simplifying, because the unsimplified form is the one "
                "that maps onto code."
            ),
            code=(
                'def f(x):\n'
                '    return (3 * x + 1) ** 2\n'
                '\n'
                'def chain_rule(x):\n'
                '    inner = 3 * x + 1\n'
                '    return 2 * inner * 3\n'
                '\n'
                'def numeric(x, eps=1e-6):\n'
                '    return (f(x + eps) - f(x - eps)) / (2 * eps)\n'
                '\n'
                'for x in [0.0, 1.0, 2.0]:\n'
                '    print(f"x={x} f={round(f(x), 4)} chain={round(chain_rule(x), 4)} numeric={round(numeric(x), 4)}")\n'
                '\n'
                'assert abs(chain_rule(1.0) - numeric(1.0)) < 1e-4\n'
                'assert chain_rule(1.0) == 24.0\n'
                'print("multiply the local derivatives along the chain")'
            ),
            variant_b="differentiate (2x - 1) cubed and name the outer and inner factors in comments",
            variant_c="add the two local factors instead of multiplying them and show the finite-difference mismatch",
            mistakes=[
                "Adding the local derivatives instead of multiplying them.",
                "Forgetting the inner derivative, which leaves the answer off by a constant factor.",
                "Simplifying before checking, so a dropped factor is no longer visible in the expression.",
            ],
            q1=(
                "For z = f(y) and y = g(x), what is dz/dx in terms of local derivatives?",
                "dz/dx equals dz/dy times dy/dx, so the local derivatives along the path multiply.",
            ),
            homework=(
                "Write `chain_rule(x)` for (a*x + b) ** 2 and `numeric_grad(x)` using central differences. Compare "
                "them at two values of x with two different a and b settings, print the results, and comment which "
                "line multiplies the outer and inner derivatives."
            ),
            patterns=["def ", "chain", "print("],
            mapping=(
                "Backpropagation applies this rule once per edge of the computation graph; a deep model's gradient "
                "is a long product of local factors."
            ),
        ),
        93: dict(
            topic="A computational graph",
            idea=(
                "A computational graph turns a calculation into nodes and edges so that the forward pass and the "
                "backward pass become separate, inspectable steps. Each node stores a value produced by a simple "
                "operation, and each edge carries a local derivative describing how the output of that operation "
                "responds to its input. The forward pass evaluates nodes in order and keeps every intermediate value, "
                "because the backward pass will need them. The backward pass starts at the loss with a gradient of "
                "one, then walks the graph in reverse, multiplying the incoming gradient by each local derivative and "
                "adding contributions wherever paths meet. In a tiny graph you can write those steps by hand: "
                "multiply input by weight, add a bias, apply ReLU, subtract the target and square. Print every "
                "intermediate value first, then compute the gradient of the loss with respect to the weight by "
                "multiplying the local factors from the loss back to the weight. Finish by comparing that product "
                "with a finite difference of the whole forward function. Seeing the intermediate values and the "
                "backward factors in the same output is what makes the graph idea concrete rather than metaphorical, "
                "and it shows why the forward pass must retain values that look unused at the time."
            ),
            code=(
                'def forward(x, w, b, y):\n'
                '    a = x * w\n'
                '    z = a + b\n'
                '    out = max(0.0, z)\n'
                '    loss = (out - y) ** 2\n'
                '    return a, z, out, loss\n'
                '\n'
                'def loss_of_w(w):\n'
                '    return forward(2.0, w, 1.0, 4.0)[3]\n'
                '\n'
                'a, z, out, loss = forward(2.0, 0.5, 1.0, 4.0)\n'
                'print(f"a={a} z={z} out={out} loss={round(loss, 4)}")\n'
                '\n'
                'd_w = 2 * (out - 4.0) * (1.0 if z > 0 else 0.0) * 2.0\n'
                'num = (loss_of_w(0.5 + 1e-6) - loss_of_w(0.5 - 1e-6)) / 2e-6\n'
                'print(f"dL/dw by hand={round(d_w, 4)} finite difference={round(num, 4)}")\n'
                '\n'
                'assert abs(d_w - num) < 1e-3\n'
                'print("walk the graph backwards, multiplying local derivatives")'
            ),
            variant_b="set the target to 1.0 so the ReLU is active and print the changed gradient",
            variant_c="change the bias to -2.0 so z is negative and show that the gradient becomes zero",
            mistakes=[
                "Discarding intermediate values after the forward pass, leaving the backward pass nothing to use.",
                "Applying the ReLU derivative when the pre-activation is exactly at the kink.",
                "Forgetting that gradients from multiple paths into a node must be summed.",
            ],
            q1=(
                "Why does the backward pass need the intermediate values from the forward pass?",
                "Local derivatives such as the ReLU mask and the pre-activation depend on those stored values.",
            ),
            homework=(
                "Write `forward(x, w, b, y)` returning the intermediate nodes and loss, plus `backward_w(x, w, b, y)` "
                "returning the hand-computed gradient. Check it against a finite difference for two parameter sets, "
                "print both, and comment which line applies the ReLU mask."
            ),
            patterns=["def ", "forward", "print("],
            mapping=(
                "A framework graph stores tensors and gradient functions in exactly this shape; retaining "
                "activations for backward is why training uses more memory than inference."
            ),
        ),
        94: dict(
            topic="Local gradients",
            idea=(
                "A local gradient is the derivative of one operation with respect to its own input, holding "
                "everything else fixed, and backpropagation is essentially the disciplined multiplication of local "
                "gradients along a path. Consider the expression (x times w plus b) squared. The square operation "
                "has a local gradient of two times its input; the addition passes gradients through unchanged; the "
                "multiplication by w has a local gradient of x with respect to w and of w with respect to x. None of "
                "these pieces knows about the others. The chain rule stitches them together, and the product of the "
                "local gradients from the loss back to a parameter is that parameter's gradient. This decomposition "
                "is why automatic differentiation can handle arbitrary code: every primitive has a small, known "
                "rule, and a traversal combines the rules. Today you compute the local gradient for the weight and "
                "for the bias separately, print each one, then print their product with the upstream derivative and "
                "compare both results against finite differences. Pay attention to the bias: its local derivative "
                "with respect to the pre-activation is one, so its gradient equals the upstream gradient, which is a "
                "useful sanity check when debugging a layer. The path to a parameter, not its own size, decides the "
                "gradient it receives."
            ),
            code=(
                'def f(x, w, b):\n'
                '    return (x * w + b) ** 2\n'
                '\n'
                'def numeric_w(x, w, b, eps=1e-6):\n'
                '    return (f(x, w + eps, b) - f(x, w - eps, b)) / (2 * eps)\n'
                '\n'
                'def numeric_b(x, w, b, eps=1e-6):\n'
                '    return (f(x, w, b + eps) - f(x, w, b - eps)) / (2 * eps)\n'
                '\n'
                'x, w, b = 2.0, 1.5, 0.5\n'
                'upstream = 2 * (x * w + b)\n'
                'local_w = x\n'
                'local_b = 1.0\n'
                'print(f"upstream={upstream} local_w={local_w} local_b={local_b}")\n'
                'print(f"d/dw={round(upstream * local_w, 4)} check={round(numeric_w(x, w, b), 4)}")\n'
                'print(f"d/db={round(upstream * local_b, 4)} check={round(numeric_b(x, w, b), 4)}")\n'
                '\n'
                'assert abs(upstream * local_w - numeric_w(x, w, b)) < 1e-3\n'
                'assert abs(upstream * local_b - numeric_b(x, w, b)) < 1e-3\n'
                'print("each operation contributes one local factor")'
            ),
            variant_b="reuse the same upstream gradient for both parameters and explain why that is valid",
            variant_c="add a second multiplication so a path has three local factors and check the product again",
            mistakes=[
                "Recomputing the upstream gradient separately for each parameter with different values.",
                "Treating the local derivative of addition as something other than one.",
                "Forgetting that a shared upstream value is reused, not averaged, across branches.",
            ],
            q1=(
                "What is the local gradient of addition with respect to each of its inputs, and why?",
                "One for each input, because increasing one input by a small amount increases the sum by exactly that amount.",
            ),
            homework=(
                "Write `local_grads(x, w, b)` returning the upstream value plus the local gradients for w and b, and "
                "`check_local(x, w, b)` comparing the products with finite differences. Print both parameters' "
                "results and comment which line handles the bias."
            ),
            patterns=["def ", "local", "print("],
            mapping=(
                "Every autodiff primitive is a local-gradient rule with a vectorised form; debugging backward "
                "passes usually means finding the one local rule that is wrong."
            ),
        ),
        95: dict(
            topic="Backprop by hand",
            idea=(
                "Backpropagation by hand means running the chain rule through a small network without any library, "
                "writing down each intermediate quantity and each gradient. The network here has two multiplications: "
                "a hidden value equals the input times the first weight, and the output equals the hidden value times "
                "the second weight. The loss is the squared difference between output and target. To get the gradient "
                "of the first weight you start from the loss, differentiate the square to get twice the error, "
                "multiply by the local derivative of the output with respect to the hidden value, which is the second "
                "weight, then multiply by the local derivative of the hidden value with respect to the first weight, "
                "which is the input. The second weight's gradient stops one step earlier. This order, loss to output "
                "to hidden to input, is the backward pass, and it reuses the upstream gradient at every stage, which "
                "is why it is cheap. Today you compute both gradients analytically, print the intermediate values and "
                "the gradients, then check each against a finite difference. If one matches and the other does not, "
                "the error is almost certainly in the factor you forgot rather than in the arithmetic. The printed "
                "intermediate values are your evidence that each factor came from the right place."
            ),
            code=(
                'def forward(x, w1, w2):\n'
                '    h = x * w1\n'
                '    out = h * w2\n'
                '    return h, out\n'
                '\n'
                'def loss(x, y, w1, w2):\n'
                '    return (forward(x, w1, w2)[1] - y) ** 2\n'
                '\n'
                'x, y, w1, w2 = 1.5, 3.0, 2.0, 0.5\n'
                'h, out = forward(x, w1, w2)\n'
                'error = out - y\n'
                'd_w2 = 2 * error * h\n'
                'd_w1 = 2 * error * w2 * x\n'
                'num_w1 = (loss(x, y, w1 + 1e-6, w2) - loss(x, y, w1 - 1e-6, w2)) / 2e-6\n'
                'num_w2 = (loss(x, y, w1, w2 + 1e-6) - loss(x, y, w1, w2 - 1e-6)) / 2e-6\n'
                'print(f"h={h} out={out} loss={round(loss(x, y, w1, w2), 4)}")\n'
                'print(f"d_w1={round(d_w1, 4)} check={round(num_w1, 4)}")\n'
                'print(f"d_w2={round(d_w2, 4)} check={round(num_w2, 4)}")\n'
                '\n'
                'assert abs(d_w1 - num_w1) < 1e-3 and abs(d_w2 - num_w2) < 1e-3\n'
                'print("backprop reuses the upstream gradient at every stage")'
            ),
            variant_b="swap the two weights and confirm the hand-computed gradients still match the checks",
            variant_c="remove the second weight's factor from d_w1 and watch only that gradient fail its check",
            mistakes=[
                "Using the updated first weight when computing the second weight's gradient.",
                "Dropping the input factor when differentiating the hidden value.",
                "Recomputing the error after a partial backward pass so the two gradients see different values.",
            ],
            q1=(
                "Why is the first weight's gradient a product of three factors rather than two?",
                "The path from loss to that weight passes through the output, the hidden value and the input, contributing three local derivatives.",
            ),
            homework=(
                "Write `backward(x, y, w1, w2)` returning both hand-computed gradients and `check_grads(x, y, w1, "
                "w2)` comparing them with finite differences. Run it on two examples, print all four comparisons, "
                "and comment which line multiplies the second weight into the first gradient."
            ),
            patterns=["def ", "backward", "print("],
            mapping=(
                "The same reverse traversal scales to every layer in a network; `loss.backward()` is this process "
                "with tensors and cached activations."
            ),
        ),
        96: dict(
            topic="Gradient checking with finite differences",
            idea=(
                "Gradient checking is the practice of comparing an analytic gradient with a numerical one before "
                "trusting training, and it has saved more debugging sessions than any visualisation. The numerical "
                "gradient is the central finite difference: evaluate the loss at parameter plus a small epsilon and "
                "at parameter minus epsilon, then divide the difference by two epsilon. The analytic gradient should "
                "agree with it to several decimal places. There are two failure modes to watch. If the two differ by "
                "a factor of two, a missing or duplicated term is likely; if they differ in sign, an operation's "
                "local derivative is inverted. If they disagree only in the last digits, the epsilon is too large or "
                "too small, and the check itself is noisy. Always check with the same parameter values that training "
                "will actually use, because a gradient can be correct at zero and wrong elsewhere. Today you check a "
                "two-parameter function, print each analytic and numerical value, and assert that the relative error "
                "is tiny. Run the check after every change to a hand-written backward pass; it is far cheaper than "
                "watching a loss curve behave strangely for an hour. Keep the tolerance generous enough for floating "
                "point but tight enough to catch a real factor error."
            ),
            code=(
                'def f(w1, w2):\n'
                '    return (w1 * w2 + w1) ** 2\n'
                '\n'
                'def analytic(w1, w2):\n'
                '    shared = 2 * (w1 * w2 + w1)\n'
                '    return shared * (w2 + 1), shared * w1\n'
                '\n'
                'def numeric(w1, w2, eps=1e-6):\n'
                '    a = (f(w1 + eps, w2) - f(w1 - eps, w2)) / (2 * eps)\n'
                '    b = (f(w1, w2 + eps) - f(w1, w2 - eps)) / (2 * eps)\n'
                '    return a, b\n'
                '\n'
                'w1, w2 = 1.5, 2.0\n'
                'ga, gb = analytic(w1, w2)\n'
                'na, nb = numeric(w1, w2)\n'
                'print(f"d/dw1 analytic={round(ga, 4)} numeric={round(na, 4)}")\n'
                'print(f"d/dw2 analytic={round(gb, 4)} numeric={round(nb, 4)}")\n'
                'print(f"relative error={round(abs(ga - na) / abs(ga) + abs(gb - nb) / abs(gb), 8)}")\n'
                '\n'
                'assert abs(ga - na) < 1e-4 and abs(gb - nb) < 1e-4\n'
                'print("check every new gradient before trusting it")'
            ),
            variant_b="try epsilon values 1e-3, 1e-6 and 1e-9 and print which relative error is smallest",
            variant_c="flip the sign of one analytic component and show the check rejecting it",
            mistakes=[
                "Comparing only the sign of two gradients instead of their magnitudes.",
                "Using a different parameter value for the numeric check than training uses.",
                "Choosing epsilon so tiny that round-off swamps the finite difference.",
            ],
            q1=(
                "What does it suggest if the analytic gradient is exactly twice the numerical one?",
                "That a factor of two is duplicated or an inner derivative is missing, since a sign error would flip the sign instead.",
            ),
            homework=(
                "Write `check_gradient(f, analytic, params, eps=1e-6)` that evaluates both gradients for every "
                "parameter and returns the largest relative error. Test it on a two-parameter function, print each "
                "pair, and comment which line isolates one parameter for the difference."
            ),
            patterns=["def ", "check", "print("],
            mapping=(
                "In practice you run gradient checks on a small model with double precision before scaling up; "
                "frameworks provide the analytic side, but the numerical reference is yours."
            ),
        ),
        97: dict(
            topic="Vanishing and exploding gradients",
            idea=(
                "Vanishing and exploding gradients come from multiplying many local derivatives together, and they "
                "are the main reason deep networks were hard to train before careful initialisation and "
                "normalisation. If each layer's local derivative has magnitude below one, a product of many such "
                "factors shrinks toward zero, so early layers receive almost no signal and learn extremely slowly. If "
                "each has magnitude above one, the product grows exponentially and updates become enormous, "
                "producing not-a-number losses. The effect is multiplicative, not additive, so six layers with a "
                "factor of a quarter reduce the gradient by more than four thousand, while six layers with a factor "
                "of four amplify it by the same amount. Activations matter because their derivatives set those "
                "factors: sigmoid derivatives are at most a quarter, which is why long sigmoid stacks vanish, while "
                "unbounded linear chains explode. Today you compute the same small linear chain with shrinking and "
                "growing weights, print the forward value and the derivative for each, and verify the derivative "
                "with a finite difference. The lesson is not that depth is impossible, but that the scale of local "
                "derivatives across layers must be managed deliberately. Printing both magnitudes next to the "
                "theoretical product makes the mechanism obvious and gives a baseline for diagnosing a real model."
            ),
            code=(
                'def chain(x, w, layers):\n'
                '    for _ in range(layers):\n'
                '        x = x * w\n'
                '    return x\n'
                '\n'
                'def grad_w(x, w, layers, eps=1e-6):\n'
                '    up = chain(x, w + eps, layers)\n'
                '    down = chain(x, w - eps, layers)\n'
                '    return (up - down) / (2 * eps)\n'
                '\n'
                'for w in [0.25, 4.0]:\n'
                '    value = chain(1.0, w, 6)\n'
                '    g = grad_w(1.0, w, 6)\n'
                '    print(f"w={w} after 6 layers={value} d/dw={round(g, 4)}")\n'
                '\n'
                'assert abs(grad_w(1.0, 0.25, 6) - 6 * 0.25 ** 5) < 1e-4\n'
                'assert chain(1.0, 0.25, 6) < 0.001 and chain(1.0, 4.0, 6) > 1000\n'
                'print("many local factors multiply: below one vanishes, above one explodes")'
            ),
            variant_b="use eight layers and print both magnitudes to show the effect compounds with depth",
            variant_c="mix factors above and below one and check whether the product ends up large or small",
            mistakes=[
                "Treating the gradient problem as additive when the factors multiply.",
                "Assuming a single safe weight scale works for every depth and activation.",
                "Clamping a diverging loss without first checking whether the gradients exploded.",
            ],
            q1=(
                "Why does a stack of local derivatives with magnitude below one make early layers learn slowly?",
                "Their product shrinks toward zero, so the gradient reaching early layers is tiny and the update is negligible.",
            ),
            homework=(
                "Write `chain_grad(w, layers)` computing the derivative of an x-times-w chain by the power rule, and "
                "`compare_depth(w)` printing its value and a finite-difference check for three depths. Print both a "
                "shrinking and a growing weight, and comment which line shows the multiplicative effect."
            ),
            patterns=["def ", "grad", "print("],
            mapping=(
                "Residual connections, careful initialisation and normalisation exist largely to keep this product "
                "near one; gradient clipping handles the exploding direction."
            ),
        ),
        98: dict(
            topic="What autodiff automates",
            idea=(
                "Automatic differentiation is the machinery that lets a framework compute exact gradients of "
                "arbitrary code without you writing the chain rule by hand, and it is smaller than it looks. A "
                "tape-based implementation records every operation during the forward pass, storing its inputs, its "
                "output and a local gradient rule. The backward pass walks the recorded operations in reverse, seeds "
                "the output gradient with one, and accumulates each operation's contribution into its inputs. "
                "Accumulation is essential: when a value feeds several later operations, its gradient is the sum of "
                "the contributions, not just the last one. Two facts follow. First, the result is exact up to "
                "floating point, unlike a finite difference. Second, the cost is roughly a constant multiple of the "
                "forward pass, not proportional to the number of parameters. Today you build a minimal tape with a "
                "node class, record a short expression, run the reverse pass, and compare the accumulated gradients "
                "with finite differences. You are not expected to productionise this; you are expected to recognise "
                "that loss.backward is a traversal like the one you wrote, and that a missing addition in that "
                "traversal is a real, common bug. A tape is not magic; it is a list of operations plus a reverse "
                "loop, and once that is clear the framework becomes far less opaque."
            ),
            code=(
                'class Node:\n'
                '    def __init__(self, value, parents=(), locals_=()):\n'
                '        self.value = value\n'
                '        self.parents = parents\n'
                '        self.locals = locals_\n'
                '        self.grad = 0.0\n'
                '\n'
                'def backward(node):\n'
                '    node.grad = 1.0\n'
                '    stack = [node]\n'
                '    while stack:\n'
                '        current = stack.pop()\n'
                '        for parent, local in zip(current.parents, current.locals):\n'
                '            parent.grad += current.grad * local\n'
                '            stack.append(parent)\n'
                '\n'
                'a, b = Node(2.0), Node(3.0)\n'
                'c = Node(a.value * b.value, (a, b), (3.0, 2.0))\n'
                'loss = Node((c.value + 1.0) ** 2, (c,), (2 * (c.value + 1.0),))\n'
                'backward(loss)\n'
                'print(f"loss={loss.value} da={a.grad} db={b.grad}")\n'
                '\n'
                'assert abs(a.grad - 2 * (2 * 3 + 1) * 3) < 1e-9\n'
                'print("autodiff replays recorded local rules in reverse")'
            ),
            variant_b="make a feed the loss through two paths and confirm its gradient is the sum of both contributions",
            variant_c="remove the accumulation and show that only one path's gradient survives",
            mistakes=[
                "Overwriting a node's gradient instead of accumulating contributions from every path.",
                "Recording operations without their input references, so the backward pass cannot reach the leaves.",
                "Assuming autodiff is a finite difference and avoiding it for accuracy reasons.",
            ],
            q1=(
                "Why must gradients be added, not assigned, when a node feeds more than one operation?",
                "Each path contributes independently, so the total derivative is the sum of all path contributions.",
            ),
            homework=(
                "Write a `Node` class with value, parents, local gradients and a gradient field, plus "
                "`backward(node)` that uses an explicit stack. Build an expression where one input has two paths, "
                "print both leaf gradients, and comment which line accumulates instead of assigns."
            ),
            patterns=["class ", "def ", "grad"],
            mapping=(
                "PyTorch's autograd builds a graph during the forward pass and traverses it in reverse; reverse-mode "
                "autodiff is what makes one backward pass give all parameter gradients."
            ),
        ),
        99: dict(
            topic="A parameter update step",
            idea=(
                "A parameter update is one subtraction: new weight equals old weight minus the learning rate times "
                "the gradient. Everything complicated in deep learning sits around that line, not inside it. The "
                "gradient says which direction increases the loss fastest, so subtracting it moves downhill; the "
                "learning rate says how far to move. One update is worth studying because it exposes the entire "
                "contract: the gradient must be computed at the current parameter value, the sign must be correct, "
                "and the step must be small enough that the linear approximation behind the gradient still holds. "
                "Today you take a single weight, compute its gradient analytically, verify it with a finite "
                "difference, record the loss before the update, apply the subtraction, and record the loss after. "
                "The assertion that the loss decreased is the smallest possible proof that the sign and step size "
                "are sane. If the loss increases, either the sign is wrong or the step is too large for the "
                "curvature at that point, and both are diagnosable from the numbers you printed. This is also a "
                "useful unit-test shape for a new optimiser: one parameter, one step, loss must fall. Rounding only "
                "at print time preserves the arithmetic, while comparing at full precision keeps the test honest."
            ),
            code=(
                'def loss(w):\n'
                '    return (w - 1.5) ** 2\n'
                '\n'
                'def grad(w):\n'
                '    return 2 * (w - 1.5)\n'
                '\n'
                'def numeric(w, eps=1e-6):\n'
                '    return (loss(w + eps) - loss(w - eps)) / (2 * eps)\n'
                '\n'
                'w = 0.0\n'
                'rate = 0.3\n'
                'before = loss(w)\n'
                'g = grad(w)\n'
                'check = numeric(w)\n'
                'print(f"before={before} analytic={g} numeric={round(check, 4)}")\n'
                '\n'
                'w = w - rate * g\n'
                'print(f"after w={round(w, 4)} loss={round(loss(w), 4)}")\n'
                '\n'
                'assert abs(g - check) < 1e-4\n'
                'assert loss(w) < before\n'
                'print("new weight equals old weight minus rate times gradient")'
            ),
            variant_b="start at w=4 and confirm the update still reduces the loss from the other side",
            variant_c="use rate=2.0 and show the loss increasing because the step is too large",
            mistakes=[
                "Adding the gradient instead of subtracting it.",
                "Computing the gradient after changing the weight, so the step uses stale or updated values inconsistently.",
                "Increasing the loss and assuming the gradient formula is wrong when the step size is the cause.",
            ],
            q1=(
                "What two facts must hold for a single update to reduce the loss?",
                "The gradient must have the correct sign and value at the current weight, and the learning rate must be small enough for the local approximation to hold.",
            ),
            homework=(
                "Write `update(w, rate)` that computes the gradient of (w - 1.5) ** 2, verifies it with a finite "
                "difference, applies one step and returns before and after losses. Print both from two starting "
                "points and comment which line performs the subtraction."
            ),
            patterns=["def ", "update", "print("],
            mapping=(
                "Every optimiser wraps this step; the difference is how it transforms the gradient (momentum, "
                "scaling, adaptive denominators) before subtracting."
            ),
        ),
        100: dict(
            topic="The learning rate",
            idea=(
                "The learning rate is the size of the step taken against the gradient, and it is the hyperparameter "
                "that most often decides whether training works at all. Too small and the loss falls so slowly that "
                "the run appears frozen; too large and the parameter jumps across the valley, overshoots, and the "
                "loss grows or oscillates. For a quadratic loss you can see all three regimes in one experiment by "
                "starting from the same weight and running a fixed number of steps at several rates. A rate well "
                "below the stable limit converges smoothly. A rate near the limit bounces from side to side but may "
                "still converge. A rate above the limit diverges, and the printed loss becomes huge rather than "
                "merely wrong. The stable limit depends on the curvature of the loss, which is why the same rate "
                "that works for one problem fails for another. Today you run a small sweep and print the final "
                "weight and loss for each rate, then check the gradient at the starting point with a finite "
                "difference. Reading the four outcomes side by side teaches more than any formula, and it gives you "
                "a diagnostic habit: when a loss curve is strange, suspect the step size before the model."
            ),
            code=(
                'def loss(w):\n'
                '    return (w - 3.0) ** 2\n'
                '\n'
                'def grad(w):\n'
                '    return 2 * (w - 3.0)\n'
                '\n'
                'def numeric(w, eps=1e-6):\n'
                '    return (loss(w + eps) - loss(w - eps)) / (2 * eps)\n'
                '\n'
                'print(f"grad check at 0: {round(grad(0.0), 4)} vs {round(numeric(0.0), 4)}")\n'
                'for rate in [0.01, 0.1, 0.6, 1.1]:\n'
                '    w = 0.0\n'
                '    for _ in range(10):\n'
                '        w = w - rate * grad(w)\n'
                '    print(f"rate={rate} final w={round(w, 4)} loss={round(loss(w), 4)}")\n'
                '\n'
                'assert abs(grad(0.0) - numeric(0.0)) < 1e-4\n'
                'print("too small crawls, just right converges, too large diverges")'
            ),
            variant_b="run twenty steps at rate 0.01 and show the final loss is much closer to zero",
            variant_c="try rate 1.05 and explain the alternating sign of successive weights",
            mistakes=[
                "Choosing a learning rate without checking how it interacts with the loss curvature.",
                "Concluding the model is broken when the loss explodes, instead of lowering the rate first.",
                "Changing several hyperparameters at once, making the effect of the rate impossible to isolate.",
            ],
            q1=(
                "Why can the same learning rate converge on one loss and diverge on another?",
                "The stable range depends on the curvature; a steeper loss amplifies the same step more strongly.",
            ),
            homework=(
                "Write `sweep(start, rates, steps)` that runs gradient descent on a quadratic for every rate and "
                "returns final weights and losses. Print one line per rate in a table, comment which rate diverges, "
                "and include the finite-difference gradient check."
            ),
            patterns=["def ", "rate", "print("],
            mapping=(
                "Learning-rate schedules and warm-up are refinements of this trade-off; a sweep like this is the "
                "first experiment when a real training run stalls."
            ),
        ),
        101: dict(
            topic="SGD and momentum",
            idea=(
                "Stochastic gradient descent updates parameters from a gradient estimated on a small batch, and "
                "momentum adds a running average of past gradients so that consistent directions build speed while "
                "noisy directions cancel. Plain SGD makes progress proportional to the current gradient, which "
                "becomes slow near flat regions and jittery when batches are small. Momentum keeps a velocity term, "
                "usually decaying by a factor such as 0.9 and then adding the new gradient, and applies that velocity "
                "instead of the raw gradient. The effect is that repeated agreement accumulates, while a single "
                "contradictory gradient is damped. On a simple quadratic you can compare the two trajectories from "
                "the same start: plain SGD inches toward the minimum, while momentum arrives in fewer steps but can "
                "overshoot if the rate is high. Today you run both rules on the same loss, print the weight after "
                "each step, and verify the underlying gradient with a finite difference. Then change the momentum "
                "factor to zero and confirm the momentum code reduces exactly to SGD, which is a good way to check "
                "that the extra term is wired correctly. The batch part is simulated here by using the full gradient. "
                "Only printed weights are rounded, so the comparison reflects the recurrence rather than formatting."
            ),
            code=(
                'def loss(w):\n'
                '    return (w - 3.0) ** 2\n'
                '\n'
                'def grad(w):\n'
                '    return 2 * (w - 3.0)\n'
                '\n'
                'def run(rate, momentum, steps):\n'
                '    w = 0.0\n'
                '    velocity = 0.0\n'
                '    path = []\n'
                '    for _ in range(steps):\n'
                '        velocity = momentum * velocity - rate * grad(w)\n'
                '        w = w + velocity\n'
                '        path.append(round(w, 3))\n'
                '    return path\n'
                '\n'
                'print("sgd     :", run(0.1, 0.0, 8))\n'
                'print("momentum:", run(0.1, 0.5, 8))\n'
                '\n'
                'num = (loss(0.0 + 1e-6) - loss(0.0 - 1e-6)) / 2e-6\n'
                'assert abs(grad(0.0) - num) < 1e-4\n'
                'assert run(0.1, 0.5, 8)[-1] > run(0.1, 0.0, 8)[-1]\n'
                'print("momentum accumulates consistent gradient directions")'
            ),
            variant_b="set momentum to 0.0 and confirm the two printed trajectories become identical",
            variant_c="raise the rate to 0.5 with momentum and show the path overshooting the minimum",
            mistakes=[
                "Applying the learning rate to the velocity twice instead of once.",
                "Resetting the velocity every step, which removes all accumulated direction.",
                "Assuming momentum cannot overshoot, then blaming the gradient when it does.",
            ],
            q1=(
                "What does the momentum term add to a plain SGD update?",
                "A decaying running sum of past gradients, so consistent directions accumulate speed and noisy ones damp out.",
            ),
            homework=(
                "Write `trajectory(rate, momentum, steps)` for a quadratic and `compare()` printing SGD and momentum "
                "paths side by side. Verify the analytic gradient with a finite difference, print both paths, and "
                "comment which line accumulates velocity."
            ),
            patterns=["def ", "momentum", "print("],
            mapping=(
                "`torch.optim.SGD(momentum=...)` is this exact recurrence; adaptive methods extend the same idea "
                "with per-parameter scaling."
            ),
        ),
        102: dict(
            topic="Weight initialisation",
            idea=(
                "Weight initialisation sets the scale of activations and gradients before training begins, and a poor "
                "choice can make a correct backward pass useless. If weights are too small, each layer shrinks its "
                "input, and by the time the signal reaches the output it has vanished; if weights are too large, "
                "activations saturate or grow without bound. The standard remedy is to scale the initial weights by "
                "the fan-in, the number of inputs each unit receives, so that the variance of the weighted sum stays "
                "roughly constant across layers. A common choice draws weights uniformly from a range whose width is "
                "inversely proportional to the square root of the fan-in. Zero initialisation is a special trap in "
                "networks with several units: every unit in a layer receives the same gradient and stays symmetric "
                "forever, so the network behaves like a single unit. Today you draw weights from a seeded generator "
                "at two scales, push random inputs through a layer with a bounded activation, and print the standard "
                "deviation of the outputs. The fan-in-scaled version should produce outputs of moderate size; the "
                "unscaled version should be much larger. Repeating the experiment with the same seed keeps the "
                "comparison fair. Judging the spread rather than a single output is what makes it meaningful."
            ),
            code=(
                'import math\n'
                'import random\n'
                '\n'
                'def output_std(scale, trials=200, fan_in=50):\n'
                '    rng = random.Random(7)\n'
                '    outputs = []\n'
                '    for _ in range(trials):\n'
                '        total = 0.0\n'
                '        for _ in range(fan_in):\n'
                '            total += rng.uniform(-1.0, 1.0) * rng.uniform(-scale, scale)\n'
                '        outputs.append(math.tanh(total))\n'
                '    mean = sum(outputs) / trials\n'
                '    return (sum((o - mean) ** 2 for o in outputs) / trials) ** 0.5\n'
                '\n'
                'fan_in = 50\n'
                'scaled = 1.0 / math.sqrt(fan_in)\n'
                'print(f"fan_in={fan_in} unscaled std={round(output_std(1.0), 4)}")\n'
                'print(f"fan_in={fan_in} scaled std={round(output_std(scaled), 4)}")\n'
                '\n'
                'assert output_std(scaled) < output_std(1.0)\n'
                'print("scale initial weights by the square root of fan-in")'
            ),
            variant_b="change fan_in to 200 and confirm the unscaled outputs saturate even harder",
            variant_c="use two different seeds and show the scaled standard deviation stays in a similar range",
            mistakes=[
                "Initialising every weight to zero, which makes units in a layer permanently identical.",
                "Choosing one scale without considering how many inputs each unit sums.",
                "Judging initialisation by the first loss value alone instead of activation spread.",
            ],
            q1=(
                "Why does dividing the initial weight scale by the square root of fan-in help?",
                "It keeps the variance of the weighted sum roughly constant as the number of inputs changes, so activations neither vanish nor explode.",
            ),
            homework=(
                "Write `activation_std(scale, seed, fan_in)` that draws weights with `random.Random(seed)`, pushes "
                "random inputs through tanh, and returns the output standard deviation. Compare fan-in scaling with "
                "an unscaled version for two fan-in sizes, print all results, and comment which line applies the "
                "scale."
            ),
            patterns=["def ", "random.Random", "print("],
            mapping=(
                "Xavier and He initialisation are fan-in and fan-out versions of this variance argument, and they "
                "are default settings in every framework's layer constructors."
            ),
        ),
        103: dict(
            topic="Testing a gradient",
            idea=(
                "Testing a gradient means writing a check that fails when the derivative is wrong, not merely "
                "printing two numbers and hoping they look close. The check has three parts: a function whose "
                "derivative you know, an implementation of that derivative, and a numerical estimate from central "
                "differences. You compare them at several parameter values, including one where the derivative is "
                "large and one where it is small, and you assert on the relative error rather than the absolute "
                "error, because gradients scale with the function. A deliberately buggy derivative is the best test "
                "of the test: remove a factor or a square and confirm that the check catches it. If the check passes "
                "on the buggy version too, the tolerance is too loose or the evaluation point is degenerate. Today "
                "you write a correct gradient and a subtly wrong one for the same cubic, print both against the "
                "numerical estimate at two points, and assert only on the correct one. This is exactly how you should "
                "treat a hand-written backward pass in a real model: keep the test, run it after every edit, and "
                "treat a silent mismatch as a stop signal rather than a curiosity. A test that is never allowed to "
                "fail on purpose is easy to fool."
            ),
            code=(
                'def f(w):\n'
                '    return (w - 2.0) ** 3\n'
                '\n'
                'def good(w):\n'
                '    return 3 * (w - 2.0) ** 2\n'
                '\n'
                'def buggy(w):\n'
                '    return 3 * (w - 2.0)\n'
                '\n'
                'def numeric(w, eps=1e-6):\n'
                '    return (f(w + eps) - f(w - eps)) / (2 * eps)\n'
                '\n'
                'for w in [0.5, 2.5]:\n'
                '    exact = numeric(w)\n'
                '    print(f"w={w} numeric={round(exact, 4)} good={round(good(w), 4)} buggy={round(buggy(w), 4)}")\n'
                '\n'
                'assert abs(good(2.5) - numeric(2.5)) < 1e-4\n'
                'assert abs(buggy(2.5) - numeric(2.5)) > 0.1\n'
                'print("a gradient test must fail on a wrong derivative, not just print numbers")'
            ),
            variant_b="add a third implementation that is off by a factor of two and check that the test rejects it",
            variant_c="test near w=2 where the true gradient is zero and explain why relative error is a poor metric there",
            mistakes=[
                "Using an absolute tolerance that passes obvious errors on large gradients.",
                "Testing only at a point where the derivative happens to be zero.",
                "Writing the check against the same buggy expression, so both sides are wrong together.",
            ],
            q1=(
                "Why is a deliberately buggy gradient a useful part of a gradient test?",
                "It proves the test can fail; a test that passes both correct and incorrect derivatives is not checking anything.",
            ),
            homework=(
                "Write `grad_test(f, analytic, points, tol=1e-4)` that compares central differences with the analytic "
                "gradient and raises on mismatch. Run it on a correct and a buggy derivative of the same cubic, print "
                "the outcomes, and comment which line computes the numerical reference."
            ),
            patterns=["def ", "grad_test", "raise"],
            mapping=(
                "Frameworks ship gradient-check utilities, but the habit of asserting on a hand-written backward "
                "pass is what catches implementation bugs in custom layers."
            ),
        ),
        104: dict(
            topic="Review: backpropagation checklist",
            idea=(
                "A backpropagation checklist is a short sequence of checks that turns a vague debugging session into "
                "a process, and today you run the whole sequence on one small example. First, confirm the forward "
                "pass produces the shape and scale you expect. Second, confirm the loss is a single finite number "
                "and that a perfect prediction gives zero. Third, verify each analytic gradient against a central "
                "finite difference at the current parameter values. Fourth, confirm the update uses the pre-update "
                "gradient and subtracts rather than adds. Fifth, check that the loss decreases after a small step; if "
                "it does not, reduce the learning rate before changing anything else. Finally, re-run the whole "
                "script from a fixed seed and confirm the printed numbers are identical, because nondeterminism "
                "hides real bugs. These checks are cheap and catch the great majority of silent training failures. "
                "Today you assemble them into one script that prints a labelled line for each check and a final "
                "weight and loss. Keep the checklist somewhere visible: when a real model fails to learn, the cause "
                "is far more often a violated item here than a missing architectural innovation. A written order also "
                "stops you changing three things at once when one check can locate the fault."
            ),
            code=(
                'def loss(w):\n'
                '    return (w - 1.0) ** 2\n'
                '\n'
                'def grad(w):\n'
                '    return 2 * (w - 1.0)\n'
                '\n'
                'def numeric(w, eps=1e-6):\n'
                '    return (loss(w + eps) - loss(w - eps)) / (2 * eps)\n'
                '\n'
                'w = 0.0\n'
                'before = loss(w)\n'
                'g = grad(w)\n'
                'check = numeric(w)\n'
                'print("1 forward finite:", round(before, 4))\n'
                'print("2 gradient check:", round(g, 4), "vs", round(check, 4))\n'
                'w = w - 0.2 * g\n'
                'print("3 update subtracted:", round(w, 4))\n'
                'print("4 loss fell:", loss(w) < before)\n'
                '\n'
                'assert abs(g - check) < 1e-4\n'
                'assert loss(w) < before\n'
                'print("5 final w:", round(w, 4), "loss:", round(loss(w), 4))\n'
                'print("checklist complete: forward, loss, gradient, update, decrease")'
            ),
            variant_b="run five steps instead of one and confirm the loss keeps falling toward zero",
            variant_c="start at w=5 and walk the checklist again, checking the gradient at the new point",
            mistakes=[
                "Skipping the gradient check because the loss happened to fall.",
                "Changing the learning rate and the gradient formula at the same time.",
                "Trusting a run that cannot be reproduced because its seed was never fixed.",
            ],
            q1=(
                "What should you check first if a single update makes the loss increase?",
                "The gradient check and the learning rate, since a wrong sign or an oversized step are the two likely causes.",
            ),
            homework=(
                "Write `train_check(w, rate, steps)` that runs the forward, gradient check, update and loss-decrease "
                "checks, printing one labelled line per check and returning the final weight. Run it from two starts, "
                "comment which line performs the finite-difference check, and keep the assertions."
            ),
            patterns=["def ", "check", "print("],
            mapping=(
                "This checklist maps directly onto debugging a real training loop: verify the loss, the backward "
                "pass, the update, and determinism in that order before touching the architecture."
            ),
        ),
    },
)
