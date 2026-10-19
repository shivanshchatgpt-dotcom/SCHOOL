"""Deep Learning optimisation and regularisation, days 135-149.

Every example is stdlib-only, offline and deterministic: a parameter is a
float, a gradient is a number, and an optimiser is a short update rule you can
read line by line. The printed values are rounded so the arithmetic stays
visible, and seeded randomness is used wherever a batch order matters.
"""

PHASE = (
    "Optimization and Regularisation",
    "Understand and implement the update rules, schedules and normalisation tricks that make training converge, then judge them with validation evidence rather than folklore.",
    {
        135: dict(
            topic="Orientation: making training work",
            idea=(
                "Training a network is a loop, not a single clever formula: predict, measure loss, compute "
                "gradients, update parameters, repeat. What makes the loop work is not one exotic algorithm but "
                "a set of choices that interact. The learning rate decides how far each step moves. The batch "
                "size decides how noisy the gradient estimate is. The optimiser decides how past gradients "
                "influence the current step. Regularisation decides how much the model is allowed to memorise. "
                "At the start of this phase it helps to see the loop stripped to a single scalar parameter, "
                "because every later method is a variation on those few lines. You can watch a small learning "
                "rate crawl toward the minimum and a large one overshoot or oscillate, and you can watch the "
                "loss fail to fall when the update direction is wrong. The practical habit to build is checking "
                "the loss curve before touching anything else: a flat curve, a curve that explodes, and a curve "
                "that falls then rises each point at a different cause. Today you run the same quadratic problem "
                "at two rates and print the loss at every step. The numbers are small, but the pattern is the "
                "one you will debug for the rest of the course."
            ),
            code="""def loss(w):
    return (w - 3.0) ** 2

def train(lr, steps):
    w = 0.0
    history = []
    for _ in range(steps):
        g = 2.0 * (w - 3.0)
        w -= lr * g
        history.append(round(loss(w), 4))
    return w, history

final_a, hist_a = train(0.05, 8)
final_b, hist_b = train(0.4, 8)
print("lr=0.05 final w:", round(final_a, 4))
print("lr=0.05 losses:", hist_a[:4])
print("lr=0.40 final w:", round(final_b, 4))
print("lr=0.40 losses:", hist_b[:4])
print("training is a loop over predict, loss, gradient and update")
""",
            variant_b="try a learning rate of 1.2 so the parameter visibly bounces across the minimum",
            variant_c="flip the gradient sign and show that the loss grows instead of falling",
            mistakes=[
                "Changing several hyperparameters at once, so no single cause can be attributed to the result.",
                "Trusting a falling training loss without checking that the parameters remain finite and sensible.",
                "Using a learning rate so large that the reported loss looks like noise or an overflow.",
            ],
            q1=(
                "What four operations repeat inside a training loop?",
                "Predict the output, compute the loss, compute gradients, and update the parameters with an optimiser.",
            ),
            homework=(
                "Write `train(lr, steps)` that runs gradient descent on the loss `(w - 3.0) ** 2`, prints the "
                "loss at each step, and returns the final weight. Run it at 0.05 and 0.4, then comment which "
                "rate overshoots and where the loss stops falling."
            ),
            patterns=["def train", "print(", "return"],
            mapping=(
                "This is the same loop that `torch.optim` runs, with `loss.backward()` supplying the gradient "
                "and `optimizer.step()` applying the update."
            ),
        ),
        136: dict(
            topic="Batch gradient descent",
            idea=(
                "Batch gradient descent computes the gradient of the loss over the entire training set before "
                "taking a single step. For a linear model the derivative of mean squared error with respect to "
                "each parameter is just the average of per-example derivatives, so the update uses one honest "
                "estimate of the true gradient. The advantage is a smooth, deterministic path: with a suitable "
                "learning rate the loss decreases monotonically, and two runs from the same starting point "
                "produce identical numbers. The disadvantage is cost. Every step touches every example, so a "
                "large dataset makes each update slow, and the model cannot react quickly to new data. Batch "
                "gradient descent also has no noise to help it escape saddle regions, which matters more once "
                "models become non-convex. In practice you use it as the reference against which mini-batch and "
                "stochastic variants are judged: if a noisy method cannot beat the batch curve on a small "
                "problem, something else is wrong. Today you average gradients over four points, update a slope "
                "and intercept, and print both parameters plus the mean squared error for five steps. Notice "
                "that the loss never jumps upward, because every step uses the same complete information. That contrast is the baseline for every later optimiser."
            ),
            code="""def predict(w, b, x):
    return w * x + b

xs = [0.0, 1.0, 2.0, 3.0]
ys = [1.0, 3.0, 5.0, 7.0]

def batch_grad(w, b):
    gw = 0.0
    gb = 0.0
    for x, y in zip(xs, ys):
        err = predict(w, b, x) - y
        gw += 2.0 * err * x / len(xs)
        gb += 2.0 * err / len(xs)
    return gw, gb

w = 0.0
b = 0.0
for step in range(1, 6):
    gw, gb = batch_grad(w, b)
    w -= 0.05 * gw
    b -= 0.05 * gb
    mse = sum((predict(w, b, x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)
    print(step, round(w, 4), round(b, 4), round(mse, 4))
print("the batch gradient averages every example before one update")
""",
            variant_b="double the learning rate and print the same five steps to find where the batch path overshoots",
            variant_c="shuffle the examples with a fixed seed and show that the batch gradient is unchanged",
            mistakes=[
                "Dividing by the number of examples twice, which silently scales the learning rate down.",
                "Forgetting that batch descent is deterministic, then blaming randomness for a reproducible failure.",
                "Assuming a smooth batch curve proves the model generalises, when it only proves the optimiser works.",
            ],
            q1=(
                "Why is batch gradient descent deterministic from a fixed starting point?",
                "Each step uses the same full dataset and the same arithmetic, so the gradient and update are identical every run.",
            ),
            homework=(
                "Write `batch_grad(w, b, xs, ys)` that returns the mean squared error gradients for a linear "
                "model, then a loop that prints slope, intercept and loss for five updates. Verify that shuffling "
                "the data does not change the printed sequence."
            ),
            patterns=["def batch_grad", "zip", "print("],
            mapping=(
                "Setting the DataLoader batch size equal to the dataset gives this behaviour in PyTorch; the "
                "same averaging happens inside the loss reduction."
            ),
        ),
        137: dict(
            topic="Momentum in numbers",
            idea=(
                "Plain gradient descent reacts only to the current gradient, so it slows down in flat directions "
                "and zig-zags across steep ones. Momentum fixes both problems by keeping a velocity that "
                "accumulates past gradients. The rule is simple: multiply the old velocity by a factor beta, add "
                "the new gradient, and move the parameter by the learning rate times that velocity. With beta "
                "around 0.9 the velocity behaves like an exponential moving average of recent gradients, so "
                "consistent directions build speed while alternating directions cancel. The result is fewer "
                "oscillations and faster travel along shallow valleys. Momentum also carries the parameter "
                "through small plateaus where the instantaneous gradient is nearly zero. The cost is one extra "
                "number per parameter and one extra multiplication, which is trivial next to the model itself. "
                "The factor beta controls memory: zero recovers plain descent, values near one remember a long "
                "history and can overshoot at the end of a run. Today you run the same scalar quadratic with and "
                "without momentum and print the parameter after each step. Watch how the momentum path covers "
                "more distance early and how it can cross the minimum before settling. Compare the distances travelled, not just the final value."
            ),
            code="""def run(lr, beta, steps):
    w = -2.0
    v = 0.0
    out = []
    for _ in range(steps):
        g = 2.0 * (w - 3.0)
        v = beta * v + g
        w -= lr * v
        out.append(round(w, 4))
    return out

plain = run(0.05, 0.0, 5)
momentum = run(0.05, 0.9, 5)
print("plain:", plain)
print("momentum:", momentum)
print("velocity carries past gradients, so the same step size travels further")
""",
            variant_b="raise beta to 0.99 and print ten steps to show the overshoot growing",
            variant_c="negate the gradient every step and show how momentum smooths the alternating directions",
            mistakes=[
                "Applying momentum to the parameters instead of to the gradients, which changes the update entirely.",
                "Treating beta as a learning rate, so both controls are tuned together and neither is understood.",
                "Forgetting to reset the velocity buffer when starting a new independent training run.",
            ],
            q1=(
                "What does the momentum velocity accumulate?",
                "An exponentially weighted sum of past gradients, so consistent directions grow and alternating ones cancel.",
            ),
            homework=(
                "Write `momentum_run(lr, beta, steps)` that performs the velocity update `v = beta * v + g` and "
                "prints the parameter each step. Compare beta 0.0 and 0.9, then explain in a comment why the "
                "second path moves faster."
            ),
            patterns=["def momentum_run", "v = beta", "print("],
            mapping=(
                "`torch.optim.SGD(momentum=0.9)` keeps exactly this velocity buffer, and the state is saved in "
                "`optimizer.state_dict()` so training can resume."
            ),
        ),
        138: dict(
            topic="RMSProp",
            idea=(
                "Different parameters can need very different step sizes. A weight with consistently large "
                "gradients should move cautiously, while one with tiny gradients needs a larger relative step. "
                "RMSProp adapts per parameter using a running average of squared gradients. At each step it "
                "updates a scale `s = rho * s + (1 - rho) * g * g`, then divides the gradient by the square root "
                "of that scale plus a small epsilon. Dividing by a root mean square makes the effective step "
                "roughly independent of gradient magnitude: large gradients shrink, small ones grow. The decay "
                "rate rho controls how quickly the scale forgets old history, typically around 0.9 or 0.99. The "
                "epsilon prevents division by zero and also caps how large the step can become when the scale is "
                "tiny. RMSProp was proposed as a fix for the shrinking learning rate of AdaGrad, which "
                "accumulates squared gradients forever. Because the scale is local to each parameter, RMSProp "
                "handles poorly conditioned problems without hand-tuning a separate rate per layer. Today you "
                "run it on one scalar parameter and print the parameter together with its root mean square, so "
                "you can see the scale settle as the gradient shrinks near the minimum. The scale is not the loss; it only controls step size."
            ),
            code="""import math

def rmsprop(lr=0.05, rho=0.9, eps=1e-8, steps=6):
    w = -2.0
    s = 0.0
    out = []
    for _ in range(steps):
        g = 2.0 * (w - 3.0)
        s = rho * s + (1.0 - rho) * g * g
        w -= lr * g / (math.sqrt(s) + eps)
        out.append((round(w, 4), round(math.sqrt(s), 4)))
    return out

for i, (w, rms) in enumerate(rmsprop(), 1):
    print(i, "w", w, "rms", rms)
print("each weight gets its own scale from a running mean of squared gradients")
""",
            variant_b="set rho to 0.5 so the scale reacts faster and describe what happens to the steps",
            variant_c="remove epsilon and explain why the first update would divide by zero",
            mistakes=[
                "Using the raw squared gradient instead of a running average, which turns the method into AdaGrad.",
                "Confusing rho with the learning rate and scaling the update in the wrong place.",
                "Omitting epsilon and hitting a division by zero or an enormous first step.",
            ],
            q1=(
                "Why does RMSProp divide by a running root mean square instead of the current gradient?",
                "The running average stabilises the scale across steps, so one unusual gradient does not permanently change the parameter's step size.",
            ),
            homework=(
                "Write `rmsprop_run(lr, rho, steps)` implementing `s = rho * s + (1 - rho) * g * g` and the scaled "
                "update, printing both the weight and root mean square per step. Run it with rho 0.9 and 0.5 and "
                "compare the first three steps."
            ),
            patterns=["def rmsprop_run", "math.sqrt", "print("],
            mapping=(
                "PyTorch exposes `torch.optim.RMSprop` with `alpha` as rho and `eps` as epsilon; the per-parameter "
                "square average lives in the optimiser state."
            ),
        ),
        139: dict(
            topic="Adam as formulas",
            idea=(
                "Adam combines the two ideas you have just built: momentum for the direction and a running square "
                "average for the scale. For each parameter it maintains `m`, an exponential average of gradients, "
                "and `v`, an exponential average of squared gradients. The raw averages start at zero, so early "
                "estimates are biased toward zero; Adam corrects this by dividing `m` by `1 - beta1 ** t` and `v` "
                "by `1 - beta2 ** t`, where t is the step number. The update is then `w -= lr * mhat / (sqrt(vhat) "
                "+ eps)`. Bias correction matters most in the first handful of steps, which is exactly when a "
                "biased small update would waste progress. The two decay rates usually sit near 0.9 and 0.999, "
                "and epsilon near 1e-8. Adam is popular because it needs little tuning and behaves well across "
                "sparse and noisy gradients, but it is not automatically better than well-tuned momentum. It can "
                "generalise slightly worse on some vision tasks, and its adaptive scale interacts with weight "
                "decay. Today you implement the formulas directly on one scalar, printing `mhat`, `vhat` and the "
                "weight for five steps. Doing the arithmetic by hand makes the bias-correction terms feel like "
                "bookkeeping rather than magic. Read each line and match it to the name of the component."
            ),
            code="""import math

w, m, v = -2.0, 0.0, 0.0
b1, b2, lr, eps = 0.9, 0.999, 0.1, 1e-8
for t in range(1, 6):
    g = 2.0 * (w - 3.0)
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * g * g
    mhat = m / (1 - b1 ** t)
    vhat = v / (1 - b2 ** t)
    w -= lr * mhat / (math.sqrt(vhat) + eps)
    print(t, "mhat", round(mhat, 4), "vhat", round(vhat, 4), "w", round(w, 4))
print("bias correction makes the first steps trustworthy")
""",
            variant_b="disable bias correction and print the first three steps to show how small they become",
            variant_c="set beta1 to 0.0 and describe which part of the method has been removed",
            mistakes=[
                "Forgetting bias correction, so the first updates are much smaller than intended.",
                "Using beta values outside zero to one, which makes the averages diverge or oscillate.",
                "Sharing one `v` across all parameters instead of keeping per-parameter state.",
            ],
            q1=(
                "What problem does bias correction solve in Adam?",
                "The moving averages initialise at zero, so without correction the early estimates are biased downward.",
            ),
            homework=(
                "Write `adam_step(w, m, v, g, t, lr)` that applies the Adam formulas and returns the new weight, "
                "`m` and `v`. Run five steps on `g = 2 * (w - 3)`, print `mhat`, `vhat` and the weight, then "
                "repeat with bias correction disabled."
            ),
            patterns=["def adam_step", "mhat", "print("],
            mapping=(
                "`torch.optim.Adam` implements these exact formulas, including `bias_correction`; inspecting "
                "`optimizer.state` shows the per-parameter `m` and `v` buffers."
            ),
        ),
        140: dict(
            topic="Learning rate warmup",
            idea=(
                "A large learning rate at step zero can damage a freshly initialised model before any useful "
                "signal has been learned. Warmup avoids this by starting small and increasing the rate over the "
                "first few hundred or thousand steps. The simplest schedule is linear: at step k of a warmup of "
                "length N, use `peak * (k + 1) / N`, then hold the peak or hand over to a decay schedule. Warmup "
                "matters most for transformers and large batch training, where early gradients can be noisy and "
                "adaptive optimiser states are still unreliable. It also protects against the sharp curvature "
                "that appears when many parameters update simultaneously from random initialisation. The cost is "
                "extra time spent at a rate too small to make much progress, so warmup length is a real "
                "hyperparameter rather than a free win. Too short and training can spike; too long and the run "
                "wastes its early budget. A useful diagnostic is to log the learning rate alongside the loss: if "
                "the loss jumps while the rate is still rising, the peak is probably too high. Today you print a "
                "linear warmup followed by a constant rate, and check that the first step is not the largest one. Then compare the same schedule with and without warmup."
            ),
            code="""def lr_at(step, warmup=5, peak=0.1):
    if step < warmup:
        return peak * (step + 1) / warmup
    return peak

for step in range(8):
    print("step", step, "lr", round(lr_at(step), 4))
print("warmup raises the rate gradually before the peak takes over")
""",
            variant_b="use a warmup of two steps and show how quickly the peak is reached",
            variant_c="replace the constant phase with a linear decay and print the same eight steps",
            mistakes=[
                "Starting at the peak rate and calling the later decay a warmup.",
                "Making warmup longer than the useful part of training, so the model barely moves.",
                "Changing warmup and peak together, then being unable to tell which fixed the loss spike.",
            ],
            q1=(
                "Why can a large learning rate at step zero be harmful?",
                "Freshly initialised parameters and optimiser states give unreliable early updates, so a large step can push the model into a bad region before useful gradients dominate.",
            ),
            homework=(
                "Write `lr_at(step, warmup, peak)` returning a linear warmup followed by a constant rate, and a "
                "loop printing the rate for eight steps. Then add a `decay_at` variant and compare the two curves "
                "in a short comment."
            ),
            patterns=["def lr_at", "warmup", "print("],
            mapping=(
                "PyTorch implements this with `LambdaLR` or `LinearLR`; frameworks such as Hugging Face wrap "
                "warmup plus decay into a single scheduler."
            ),
        ),
        141: dict(
            topic="Batch normalisation maths",
            idea=(
                "Batch normalisation stabilises training by re-centring and re-scaling activations using "
                "statistics from the current mini-batch. For each feature it computes the batch mean, the batch "
                "variance, and then maps every value to `(x - mean) / sqrt(var + eps)`. That alone would force "
                "every layer to have zero mean and unit variance, which can remove useful representational "
                "freedom, so the result is multiplied by a learned gamma and shifted by a learned beta. Gamma "
                "and beta are trained like any other parameters, which lets the network undo the normalisation "
                "if that is better. The epsilon keeps the division stable when a feature is almost constant. At "
                "training time the batch statistics are used and a running average is stored; at evaluation time "
                "the stored average replaces the batch estimate so predictions do not depend on which examples "
                "happen to share a batch. This train-eval difference is a common source of silent bugs. Batch "
                "normalisation also changes the loss landscape, allowing higher learning rates and reducing "
                "sensitivity to initialisation. Today you compute the mean and variance of four activations, "
                "normalise them, and apply gamma and beta to see the output scale and shift change. The variance uses the biased denominator, which is standard here."
            ),
            code="""xs = [1.0, 2.0, 3.0, 4.0]
mean = sum(xs) / len(xs)
var = sum((x - mean) ** 2 for x in xs) / len(xs)
gamma, beta, eps = 2.0, 0.5, 1e-5
out = [((x - mean) / (var + eps) ** 0.5) * gamma + beta for x in xs]
print("mean", round(mean, 4), "var", round(var, 4))
print("normalised", [round(v, 4) for v in out])
print("gamma and beta restore scale and shift after normalising")
""",
            variant_b="set gamma to 0.5 and confirm that the output spread shrinks without changing the mean",
            variant_c="use a batch where one value repeats and explain why epsilon matters for the variance",
            mistakes=[
                "Normalising at evaluation with the current batch instead of the stored running statistics.",
                "Ignoring epsilon, which makes near-constant features produce enormous normalised values.",
                "Forgetting that gamma and beta are learned parameters, then wondering why the scale never adapts.",
            ],
            q1=(
                "Why does batch normalisation include learned gamma and beta?",
                "They let the network rescale and shift the normalised activations, restoring representational flexibility that pure normalisation would remove.",
            ),
            homework=(
                "Write `batch_norm(xs, gamma, beta, eps)` returning the normalised list, and print the batch mean "
                "and variance before and after. Run it on a constant batch to show why epsilon is needed, and "
                "comment on the train versus eval statistics."
            ),
            patterns=["def batch_norm", "gamma", "print("],
            mapping=(
                "`nn.BatchNorm1d` or `nn.BatchNorm2d` follows this exact computation and switches behaviour "
                "between `model.train()` and `model.eval()`."
            ),
        ),
        142: dict(
            topic="Layer normalisation",
            idea=(
                "Layer normalisation normalises each sample across its own features instead of across the batch. "
                "For a single row of activations it computes that row's mean and variance, subtracts the mean, "
                "divides by the standard deviation, then applies learned gamma and beta per feature. Because the "
                "statistics come from one example, the result does not depend on batch size and is identical at "
                "training and evaluation time. That property makes layer normalisation attractive for recurrent "
                "networks, small batches and transformers, where batch statistics are either noisy or "
                "unavailable. It also means two samples with the same shape are normalised independently: a "
                "sample with values around ten becomes centred near zero, and so does one with values around one "
                "hundred. The learned affine parameters restore whatever scale the next layer needs. Layer "
                "normalisation does not mix information between examples, so it cannot accidentally leak "
                "statistics from one sample to another, which is a subtle risk in batch normalisation. The "
                "tradeoff is that it removes per-sample magnitude information, which may matter for some tasks. "
                "Today you normalise two rows with very different scales, apply shared gamma and beta, and print "
                "the results. The outputs should look almost identical, showing that only relative feature "
                "patterns survive."
            ),
            code="""def layer_norm(row, gamma, beta, eps=1e-5):
    mean = sum(row) / len(row)
    var = sum((x - mean) ** 2 for x in row) / len(row)
    return [round(((x - mean) / (var + eps) ** 0.5) * g + b, 4)
            for x, g, b in zip(row, gamma, beta)]

gamma = [1.0, 1.0, 1.0]
beta = [0.0, 0.0, 0.0]
for row in ([1.0, 2.0, 3.0], [10.0, 20.0, 30.0]):
    print(row, "->", layer_norm(row, gamma, beta))
print("normalising each sample across features removes per-sample scale")
""",
            variant_b="use gamma 2.0 and beta 1.0 to show the affine transform after normalisation",
            variant_c="pass rows with different feature patterns and explain which similarity survives normalisation",
            mistakes=[
                "Confusing the feature axis with the batch axis and normalising across the wrong dimension.",
                "Using batch statistics at evaluation when layer normalisation should not depend on the batch.",
                "Dropping gamma and beta and losing the ability to restore useful activation scale.",
            ],
            q1=(
                "How does layer normalisation differ from batch normalisation?",
                "Layer normalisation uses each sample's own feature statistics, while batch normalisation uses statistics across the batch for each feature.",
            ),
            homework=(
                "Write `layer_norm(row, gamma, beta)` that computes per-row mean and variance and returns the "
                "affine-normalised values. Print two rows with very different magnitudes, then run the same "
                "function with gamma 2.0 and explain the change."
            ),
            patterns=["def layer_norm", "zip", "print("],
            mapping=(
                "`nn.LayerNorm` normalises over the trailing dimensions you specify and keeps learned weight and "
                "bias, matching the affine step here."
            ),
        ),
        143: dict(
            topic="Weight decay",
            idea=(
                "Weight decay discourages large parameters by adding a cost proportional to their size. In the "
                "classic view it is an L2 penalty, so the gradient gains a term `wd * w` and every update pulls "
                "the weight slightly toward zero. For plain stochastic gradient descent this is mathematically "
                "the same as multiplying the weight by a factor slightly below one each step. With adaptive "
                "optimisers the two views stop agreeing: adding `wd * w` to the gradient lets the adaptive scale "
                "divide the decay too, so heavily updated parameters decay less than intended. Decoupled weight "
                "decay, popularised by AdamW, applies the shrinkage directly to the parameter after the gradient "
                "step, keeping the regularisation strength independent of the adaptive denominator. That is why "
                "AdamW often generalises better than Adam with an L2 penalty. Weight decay is not free: too much "
                "keeps the model small and underfit, too little lets it memorise noise. Values around 0.01 to 0.1 "
                "are common for AdamW, but the right value depends on the model, dataset and learning rate. Today "
                "you run both update styles side by side on one weight with a constant gradient and print the "
                "divergence. The difference is small per step but compounds over a training run."
            ),
            code="""def l2_step(w, g, lr, wd):
    return w - lr * (g + wd * w)

def decoupled_step(w, g, lr, wd):
    return (w - lr * g) * (1.0 - lr * wd)

w1 = 1.0
w2 = 1.0
for step in range(1, 5):
    w1 = l2_step(w1, 0.1, 0.5, 0.1)
    w2 = decoupled_step(w2, 0.1, 0.5, 0.1)
    print(step, "l2", round(w1, 4), "decoupled", round(w2, 4))
print("decoupled decay shrinks the weight after the gradient step")
""",
            variant_b="raise the learning rate to 0.9 and show the two styles separating faster",
            variant_c="set the gradient to zero and confirm that only weight decay moves the parameter",
            mistakes=[
                "Assuming L2 and decoupled decay are identical for Adam, when the adaptive scale changes both.",
                "Applying weight decay to biases and normalisation parameters without evidence that it helps.",
                "Increasing weight decay to fix overfitting while ignoring the possibility that the model is underfit.",
            ],
            q1=(
                "Why is decoupled weight decay used with Adam?",
                "It shrinks weights independently of the adaptive gradient scale, so the regularisation strength is not distorted by the optimiser.",
            ),
            homework=(
                "Write `l2_step` and `decoupled_step` for a single weight, then print four updates with a fixed "
                "gradient. Run the comparison with a zero gradient and explain in a comment which term still "
                "changes the weight."
            ),
            patterns=["def l2_step", "def decoupled_step", "print("],
            mapping=(
                "`torch.optim.AdamW` implements decoupled decay, while `Adam(weight_decay=...)` adds the penalty "
                "to the gradient in the classic way."
            ),
        ),
        144: dict(
            topic="Gradient clipping",
            idea=(
                "Some training runs fail not because the learning rate is wrong but because a single batch "
                "produces an enormous gradient. Recurrent networks and deep transformers are especially prone to "
                "this, and one such step can undo hours of progress. Gradient clipping caps the update by "
                "rescaling the gradient before the optimiser sees it. Global norm clipping computes the norm of "
                "the whole gradient vector, and if that norm exceeds a threshold it multiplies every component "
                "by `max_norm / norm`. Because the same factor is applied to all components, the direction of "
                "the update is preserved and only its length changes. Element-wise clipping instead clamps each "
                "component independently, which can rotate the update and is usually less desirable. Clipping by "
                "value is simple but scale-dependent; norm clipping adapts to the overall magnitude. A threshold "
                "that is too small slows learning by constantly shrinking healthy gradients, while one that is "
                "too large never activates. Monitoring the pre-clip norm tells you whether clipping is doing "
                "anything. Today you clip a three-component gradient with norm five down to a maximum of 2.5, "
                "print both norms, and verify that the direction is unchanged. The arithmetic is small, but the "
                "protection is real. Log the pre-clip norm as well."
            ),
            code="""import math

grads = [3.0, 4.0, 0.0]
norm = math.sqrt(sum(g * g for g in grads))
max_norm = 2.5
scale = min(1.0, max_norm / norm)
clipped = [round(g * scale, 4) for g in grads]
print("global norm", round(norm, 4), "scale", round(scale, 4))
print("clipped", clipped)
print("clipped norm", round(math.sqrt(sum(g * g for g in clipped)), 4))
print("clipping rescales the whole vector, keeping its direction")
""",
            variant_b="set max_norm above the original norm and confirm that the clipping factor stays at one",
            variant_c="clip each component separately to 3.0 and compare the resulting direction",
            mistakes=[
                "Clipping after the optimiser step, which does nothing to the update that was actually applied.",
                "Applying independent per-component clamps and assuming the gradient direction is preserved.",
                "Setting the threshold so low that every step is clipped, which quietly behaves like a tiny learning rate.",
            ],
            q1=(
                "What stays the same when a gradient vector is clipped by global norm?",
                "Its direction stays the same; only its length is reduced to the maximum norm.",
            ),
            homework=(
                "Write `clip_global(grads, max_norm)` returning the rescaled list and the original norm. Call it "
                "on a vector whose norm exceeds the threshold, print both norms, and assert that the direction "
                "ratios are unchanged."
            ),
            patterns=["def clip_global", "math.sqrt", "print("],
            mapping=(
                "`torch.nn.utils.clip_grad_norm_` performs this global rescaling in place before "
                "`optimizer.step()`, and returns the pre-clip norm for logging."
            ),
        ),
        145: dict(
            topic="A learning rate finder",
            idea=(
                "Choosing a learning rate by guessing wastes runs. A learning rate finder sweeps upward on a "
                "logarithmic scale, trains briefly at each rate, and records the loss. At very small rates the "
                "loss barely moves; as the rate grows it falls quickly; beyond a point it bounces or explodes. "
                "The useful zone is usually the steepest part of the downward curve, just before the minimum, "
                "divided by a safety factor. The original method increases the rate exponentially within one "
                "pass over the data, but even a crude independent sweep on a small problem reveals the shape. "
                "Two details matter. First, reset the model between rates or the later runs start from a "
                "different place; resetting is the cleaner comparison. Second, a short run is enough to rank "
                "rates, but final training should still use a schedule rather than the single best value. The "
                "finder is a diagnostic, not an oracle: noisy batches, a tiny sample, or a loss that has not "
                "started falling can all mislead it. Today you evaluate six rates on a quadratic, print the loss "
                "for each, and select the rate with the lowest loss that did not diverge. The pattern is the same "
                "one you would plot on a real model, only the numbers are smaller."
            ),
            code="""def loss_at(lr):
    w = 0.0
    for _ in range(8):
        g = 2.0 * (w - 3.0)
        w -= lr * g
        if abs(w) > 50:
            return float("inf")
    return (w - 3.0) ** 2

best = None
for k in range(-4, 2):
    lr = 10.0 ** k
    loss = loss_at(lr)
    label = "inf" if loss == float("inf") else round(loss, 4)
    print("lr", lr, "loss", label)
    if loss != float("inf") and (best is None or loss < best[1]):
        best = (lr, loss)
print("suggested lr", best[0], "loss", round(best[1], 4))
""",
            variant_b="extend the sweep to 100.0 and show that divergence appears beyond the useful range",
            variant_c="start from a different initial weight and explain why the best rate can shift",
            mistakes=[
                "Reusing partially trained weights for every rate, so the loss comparison mixes two variables.",
                "Picking the rate at the very bottom of the curve rather than a safer value just before it.",
                "Treating a finder result from one batch as a permanent setting for every dataset and model.",
            ],
            q1=(
                "Where on a learning rate sweep is the useful range usually found?",
                "On the steeply falling part of the loss curve, just before the rate becomes unstable and the loss rises or diverges.",
            ),
            homework=(
                "Write `find_lr(rates)` that trains a fresh scalar model for eight steps at each rate and prints "
                "rate plus final loss. Skip divergent runs, return the best rate and loss, and comment on why "
                "the model is reset for each trial."
            ),
            patterns=["def find_lr", "for", "print("],
            mapping=(
                "The `lr_finder` callback in fastai or a short manual sweep in PyTorch follows this pattern, and "
                "the resulting curve is read the same way."
            ),
        ),
        146: dict(
            topic="Schedulers compared",
            idea=(
                "A learning rate schedule changes the step size during training, and the shape of that change "
                "often matters as much as the starting value. A constant rate is the simplest baseline but "
                "spends late training taking steps that are too large to settle. Step decay drops the rate at "
                "fixed milestones and is easy to reason about, though the drops can cause small loss jumps. "
                "Cosine decay reduces the rate smoothly to near zero, which suits long runs and is standard for "
                "transformers when combined with warmup. Exponential decay is another smooth option but can "
                "leave the rate too high at the end unless the final value is controlled. The common thread is "
                "exploration early and refinement late: a larger rate covers ground and escapes poor regions, "
                "while a smaller rate lets the model settle into a minimum. Schedules should be compared with "
                "the same total budget and the same seed, otherwise the comparison measures luck. It is also "
                "worth logging the rate itself, because a bug in the schedule is easy to miss when only the loss "
                "is plotted. Today you print constant, step and cosine values at five checkpoints, and see how "
                "the cosine curve spends most of its time at a moderate rate before a quiet finish."
            ),
            code="""import math

def constant(step):
    return 0.1

def step_decay(step):
    return 0.1 if step < 10 else 0.01

def cosine(step, total=20):
    return 0.1 * 0.5 * (1.0 + math.cos(math.pi * step / total))

for step in (0, 5, 10, 15, 20):
    print(step, "constant", round(constant(step), 4),
          "step", round(step_decay(step), 4),
          "cosine", round(cosine(step), 4))
print("schedules trade early progress against a quiet finish")
""",
            variant_b="make the cosine end at 0.01 instead of zero and compare the last two checkpoints",
            variant_c="add a warmup phase before the cosine and explain which training steps change",
            mistakes=[
                "Comparing schedules with different total step budgets, which confounds the schedule with training time.",
                "Letting a cosine schedule reach exactly zero while the model is still improving.",
                "Changing the schedule and the peak rate together, then attributing the result to the schedule alone.",
            ],
            q1=(
                "What is the usual purpose of decaying the learning rate late in training?",
                "Smaller late steps let the model settle into a minimum instead of bouncing around it.",
            ),
            homework=(
                "Write `constant`, `step_decay` and `cosine` functions, then a loop that prints their values at "
                "several checkpoints. Add a `warmup_cosine` variant and comment on where each schedule spends "
                "the largest steps."
            ),
            patterns=["def cosine", "def step_decay", "print("],
            mapping=(
                "PyTorch provides `StepLR`, `CosineAnnealingLR` and `LambdaLR`; the loss and learning rate should "
                "both be logged to catch schedule mistakes."
            ),
        ),
        147: dict(
            topic="Regularisation tradeoffs",
            idea=(
                "Regularisation is a tradeoff, not a switch. A model with no regularisation can drive training "
                "loss very low while validation loss turns upward, which is the signature of overfitting. Adding "
                "regularisation shrinks that gap, but too much prevents the model from fitting real structure and "
                "both losses rise. The useful value sits somewhere in the middle, and it must be chosen on "
                "validation data rather than training data. Weight decay, dropout, early stopping and data "
                "augmentation all pull in the same broad direction but through different mechanisms, so their "
                "effects are not interchangeable. It also helps to separate the sources of the gap: a small "
                "dataset, a model with too many parameters, noisy labels, and a long training run can each "
                "produce overfitting, and regularisation only masks some of them. When comparing strengths, keep "
                "the architecture, seed, schedule and evaluation set fixed, and change one thing at a time. "
                "Report both losses, not just the better-looking one, because a low validation loss with a "
                "collapsed training loss often means the model has stopped learning. Today you sweep a few decay "
                "strengths against a simple synthetic train-validation curve, print both errors, and select the "
                "strength with the best validation result. That is the whole method."
            ),
            code="""def errors(wd):
    train = 0.05 + 0.5 * wd + (wd - 0.2) ** 2
    val = 0.12 + 0.6 * (wd - 0.15) ** 2 + 0.08 * wd
    return train, val

best = None
for wd in (0.0, 0.05, 0.1, 0.2, 0.4):
    tr, va = errors(wd)
    print("wd", wd, "train", round(tr, 4), "val", round(va, 4))
    if best is None or va < best[1]:
        best = (wd, va)
print("best validation wd", best[0])
""",
            variant_b="change the validation curve so the best strength shifts and explain what real evidence would cause that",
            variant_c="add a very large strength and show both losses rising as the model underfits",
            mistakes=[
                "Selecting the regularisation strength on the training loss, which always prefers less regularisation.",
                "Changing the model size and the weight decay together, so the cause of the improvement is ambiguous.",
                "Assuming more regularisation is always safer, then ending up with an underfit model.",
            ],
            q1=(
                "What pattern in train and validation loss suggests overfitting?",
                "Training loss keeps falling while validation loss stops improving and then rises, widening the gap between them.",
            ),
            homework=(
                "Write `sweep(wd_values)` that prints training and validation error for each strength and returns "
                "the best validation setting. Keep the curves in one small function, and comment on why the "
                "choice must not use the training error."
            ),
            patterns=["def sweep", "val", "print("],
            mapping=(
                "In PyTorch this is a validation loop over `model.eval()` plus early stopping or a weight decay "
                "grid, with the best checkpoint chosen by validation loss."
            ),
        ),
        148: dict(
            topic="Reproducing an optimisation run",
            idea=(
                "An optimisation result is only useful if someone can reproduce it. Reproducibility starts with "
                "explicit seeds for every source of randomness: initial weights, batch shuffling, dropout masks "
                "and data augmentation. A seeded `random.Random` object is better than the global random module "
                "because it keeps separate streams from interfering. The order of operations matters too. "
                "Shuffling before splitting, or splitting before shuffling, changes which examples land in which "
                "batch, so the same seed can still produce different curves if the pipeline order changes. Log "
                "the seed, the data order, the learning rate, the batch size and the final loss together, "
                "because a number without its configuration cannot be checked. Hardware and library versions can "
                "also change results, especially with parallel floating point reductions, so exact reproduction "
                "sometimes requires the same environment. The practical test is simple: run the whole training "
                "function twice in the same process and confirm that the printed parameters and losses match. "
                "If they do not, randomness is leaking in from somewhere. Today you train a tiny linear model "
                "with seeded shuffling and mini-batches, run it twice, and compare the outputs. The run is small "
                "enough to audit by eye, which is the point. Write the seed into the output line."
            ),
            code="""import random

def train(seed=7, epochs=4):
    rng = random.Random(seed)
    w = 0.0
    data = [(rng.uniform(0, 1), rng.uniform(0, 1)) for _ in range(12)]
    for _ in range(epochs):
        order = list(range(len(data)))
        rng.shuffle(order)
        for start in range(0, len(order), 4):
            batch = [data[i] for i in order[start:start + 4]]
            g = sum(2.0 * (w * x - y) * x for x, y in batch) / len(batch)
            w -= 0.1 * g
    mse = sum((w * x - y) ** 2 for x, y in data) / len(data)
    return round(w, 4), round(mse, 4)

first = train()
second = train()
print("first run", first)
print("second run", second)
print("same seed reproduces the shuffle, batches and final loss")
""",
            variant_b="change the seed and show that the final weight and loss move",
            variant_c="shuffle once before splitting into batches and explain why the run no longer matches",
            mistakes=[
                "Seeding only the global random module while a library uses its own generator.",
                "Changing the order of shuffling and splitting, then expecting the same seed to reproduce the run.",
                "Recording the final loss without the seed, batch size and learning rate needed to interpret it.",
            ],
            q1=(
                "What is the simplest check that a training run is reproducible?",
                "Call the full training function twice with the same seed and verify that parameters and losses match exactly.",
            ),
            homework=(
                "Write `train(seed, epochs)` using `random.Random(seed)` for data creation and batch shuffling. "
                "Call it twice with the same seed, assert the results are equal, then call it with a different "
                "seed and print both outcomes for comparison."
            ),
            patterns=["def train", "random.Random", "assert"],
            mapping=(
                "PyTorch users set `torch.manual_seed` and DataLoader worker seeds; deterministic algorithms can "
                "be requested, though some operations remain hardware dependent."
            ),
        ),
        149: dict(
            topic="Review: optimization checklist",
            idea=(
                "This phase gave you a toolbox, and the final skill is knowing which tool to reach for when a run "
                "misbehaves. Start with the gradient: a finite-difference check catches sign errors and missing "
                "terms before any long training run. Then check scale: are the parameters and gradients finite, "
                "and does the loss fall at all in the first few steps? Next check the learning rate and schedule: "
                "a rate that is too high explodes or oscillates, while one that is too low looks flat. Inspect "
                "the update rule itself: momentum and adaptive methods carry state, and stale or shared state can "
                "produce plausible but wrong curves. Compare against a plain baseline, because a complicated "
                "optimiser that does not beat simple descent on a small problem is usually hiding a bug. Check "
                "regularisation on validation data, not training data, and keep the seed and configuration with "
                "the result. Finally, verify reproducibility by running twice. A checklist is not bureaucracy; it "
                "is a fixed order that prevents you from tuning hyperparameters to compensate for a broken "
                "gradient. Today you run a compact check: compare an analytic gradient with a finite difference, "
                "take a few descent steps, and print boolean results for the gradient, the loss decrease and "
                "parameter finiteness."
            ),
            code="""def grad_check(f, x, eps=1e-6):
    numeric = (f(x + eps) - f(x - eps)) / (2 * eps)
    analytic = 2.0 * (x - 3.0)
    return abs(numeric - analytic) < 1e-4

w = 0.0
checks = []
checks.append(("gradient", grad_check(lambda t: (t - 3.0) ** 2, w)))
for _ in range(3):
    w -= 0.1 * 2.0 * (w - 3.0)
checks.append(("loss fell", (w - 3.0) ** 2 < (0.0 - 3.0) ** 2))
checks.append(("weights finite", abs(w) < 1e6))
for name, ok in checks:
    print(name, ok)
print("checked gradient, update and stability before trusting a run")
""",
            variant_b="break the analytic gradient on purpose and show the check turning false",
            variant_c="use a learning rate of 2.0 and add a check that flags the resulting divergence",
            mistakes=[
                "Tuning the learning rate before confirming that the gradient is correct.",
                "Treating finite parameters as proof of learning, when the loss may still be flat or rising.",
                "Skipping the baseline, so a complex optimiser is credited for gains that plain descent would also get.",
            ],
            q1=(
                "Why check the gradient before tuning the learning rate?",
                "A wrong gradient makes every learning rate misleading, so hyperparameter tuning would optimise around a bug.",
            ),
            homework=(
                "Write `check_run()` that performs a finite-difference gradient check, takes three descent steps, "
                "and returns booleans for a correct gradient, a lower loss and finite parameters. Print each "
                "result and assert the gradient check passes."
            ),
            patterns=["def check_run", "assert", "print("],
            mapping=(
                "This mirrors a PyTorch debugging pass: `torch.autograd.gradcheck`, a short overfit-one-batch "
                "run, and a finite-loss check before any scheduler tuning."
            ),
        ),
    },
)
