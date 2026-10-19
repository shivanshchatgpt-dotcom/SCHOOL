PHASE = ("Training a Network", "Build, read and debug a deterministic training loop from batches and splits through regularisation, schedules and early stopping.", {
    105: dict(
        topic="Orientation: the training loop",
        idea=(
            "Training a network is a loop repeated until the numbers stop improving, and today you build that loop by "
            "hand so nothing about it feels magical. The loop has four moves: run the inputs forward through the model "
            "to get predictions, compare those predictions with the targets using a loss, work out which direction "
            "each parameter should move using a gradient, then take a small step in that direction. The step size is "
            "the learning rate, and it is the parameter you will spend the most time tuning. At first the weights are "
            "arbitrary, so the loss is large; each pass over the data should make it smaller. If it does not, "
            "something in the loop is wrong, and that is worth knowing before any framework hides the details. "
            "Today's example fits a single weight to a straight-line dataset. Print the loss every few epochs rather "
            "than every step, because a curve is easier to read than a wall of numbers. The important habit is to "
            "know what each of the four lines does and to be able to point at the one that updates the weight. "
            "Everything later in this phase is a refinement of this skeleton, never a replacement for it."
        ),
        code=(
            'def forward(x, w):\n'
            '    return x * w\n'
            '\n'
            'def mse(data, w):\n'
            '    total = 0.0\n'
            '    for x, y in data:\n'
            '        total += (forward(x, w) - y) ** 2\n'
            '    return total / len(data)\n'
            '\n'
            'def grad(data, w):\n'
            '    total = 0.0\n'
            '    for x, y in data:\n'
            '        total += 2 * (x * w - y) * x\n'
            '    return total / len(data)\n'
            '\n'
            'data = [(1.0, 2.0), (2.0, 4.0), (3.0, 6.0), (4.0, 8.0)]\n'
            'w = 0.0\n'
            'for epoch in range(1, 13):\n'
            '    w = round(w - 0.05 * grad(data, w), 4)\n'
            '    if epoch % 3 == 0:\n'
            '        print(f"epoch {epoch}: loss={round(mse(data, w), 4)} w={w}")\n'
            '\n'
            'assert mse(data, w) < 0.01\n'
            'print("forward, loss, gradient, update")\n'
        ),
        variant_b="change the target from 2x to 3x and retrain; confirm the learned weight moves toward three",
        variant_c="set the learning rate to 0.001 and show that twelve epochs no longer reach the target",
        mistakes=[
            "Adding the gradient instead of subtracting it, so the loss climbs.",
            "Updating the weight before the gradient is computed, using a stale model.",
            "Printing every step instead of a sampled curve, hiding the trend in noise.",
        ],
        q1=(
            "What are the four moves inside one pass of the training loop?",
            "Forward pass, loss computation, gradient computation, and a parameter update, repeated over epochs.",
        ),
        homework=(
            "Write `train(data, rate, epochs)` that runs forward, loss, gradient and update over a list of "
            "input-target pairs and returns the final weight plus the rounded loss history. Run it for two "
            "learning rates, print both histories, and comment which line moves the weight against the gradient."
        ),
        patterns=["def train(", "round(", "print("],
        mapping=(
            "This is the same loop that `loss.backward()` and `optimizer.step()` run in PyTorch; the framework only "
            "makes the gradient automatic and fast."
        ),
    ),
    106: dict(
        topic="Epochs and steps",
        idea=(
            "An epoch is one complete pass over the training set; a step is one parameter update, usually after a "
            "batch. Confusing the two makes learning-rate schedules, logging and progress estimates wrong, so it is "
            "worth fixing the vocabulary now. If you have eight examples and a batch size of two, one epoch contains "
            "four steps, and ten epochs contain forty steps. The number of epochs is how many times the model sees "
            "each example; the number of steps is how many updates it makes. Those counts differ whenever the batch "
            "size is smaller than the dataset, which is almost always. A useful habit is to season the loop with "
            "counters: increment the step counter inside the batch loop and the epoch counter outside it, then print "
            "both next to the loss. When a run looks wrong, those counters tell you whether the model trained for "
            "too few updates or simply saw the same data too many times. Today you train a tiny linear model with "
            "mini-batches, print the cumulative step count at the end of each epoch, and check that the arithmetic "
            "matches. Do not hard-code the step total; compute it from the dataset length and batch size, because "
            "that is the relationship you will reuse in every real training script."
        ),
        code=(
            'data = [(float(x), 2.0 * x) for x in range(1, 9)]\n'
            'batch_size = 2\n'
            'rate = 0.005\n'
            'w = 0.0\n'
            '\n'
            'def batch_loss(batch, w):\n'
            '    return sum((x * w - y) ** 2 for x, y in batch) / len(batch)\n'
            '\n'
            'def batch_grad(batch, w):\n'
            '    return sum(2 * (x * w - y) * x for x, y in batch) / len(batch)\n'
            '\n'
            'steps_per_epoch = len(data) // batch_size\n'
            'step = 0\n'
            'for epoch in range(1, 6):\n'
            '    for start in range(0, len(data), batch_size):\n'
            '        batch = data[start:start + batch_size]\n'
            '        w = round(w - rate * batch_grad(batch, w), 4)\n'
            '        step += 1\n'
            '    print(f"epoch {epoch}: steps={step} loss={round(batch_loss(data, w), 4)}")\n'
            '\n'
            'assert step == 5 * steps_per_epoch\n'
            'assert batch_loss(data, w) < batch_loss(data, 0.0)\n'
            'print("one epoch is a pass; one step is an update")\n'
        ),
        variant_b="raise the batch size to four and show that each epoch now contains two steps",
        variant_c="use a dataset of nine examples with batch size two and explain the leftover final batch",
        mistakes=[
            "Calling every batch an epoch, so the epoch count and step count are reported wrongly.",
            "Hard-coding the number of steps instead of computing it from data length and batch size.",
            "Dropping the final partial batch without noticing, so some examples are never trained on.",
        ],
        q1=(
            "With eight examples and a batch size of two, how many steps are in one epoch?",
            "Four, because each epoch processes the whole dataset in four batches of two.",
        ),
        homework=(
            "Write `epoch_summary(n_examples, batch_size, epochs)` that returns the number of steps per epoch "
            "and the total steps. Also implement `train_epochs(data, batch_size, rate, epochs)`, print the "
            "cumulative step count beside each epoch's loss, and comment how the final partial batch is handled."
        ),
        patterns=["def epoch_summary(", "def train_epochs(", "print("],
        mapping=(
            "Training scripts report progress in steps because schedulers and logs operate per update, while humans "
            "often think in epochs; keeping both counters visible prevents off-by-batch confusion."
        ),
    ),
    107: dict(
        topic="Batches and deterministic shuffling",
        idea=(
            "Shuffling exists to stop the order of the data from becoming a hidden parameter. If every epoch feeds "
            "the same examples in the same order, the batches are identical, the gradients repeat, and the model can "
            "learn the sequence rather than the relationship. Shuffling breaks that pattern, but it must be "
            "reproducible, or you cannot tell whether a change in results came from your code or from a different "
            "random order. The standard solution is a seeded random number generator: create it once with a fixed "
            "integer, then shuffle a list of indices at the start of every epoch. Shuffling indices rather than the "
            "data keeps features and labels together and makes the operation cheap to reason about. A common bug is "
            "shuffling features and targets separately, which silently destroys the pairing; another is reseeding "
            "every epoch, which produces the same shuffle forever. Today you build this with `random.Random`, print "
            "the batches for two epochs, and assert that each epoch still contains every example exactly once. The "
            "assertion matters more than the printout: it checks the property that makes shuffling safe. Keep the "
            "dataset tiny, because you are learning the mechanism, and the mechanism is the same at any scale. In "
            "real training, the same seed lets a colleague reproduce your exact batch order when debugging a "
            "suspicious result."
        ),
        code=(
            'import random\n'
            '\n'
            'data = [(float(x), 2.0 * x) for x in range(1, 10)]\n'
            'batch_size = 3\n'
            'rng = random.Random(7)\n'
            'all_indices = list(range(len(data)))\n'
            '\n'
            'for epoch in range(1, 3):\n'
            '    order = all_indices[:]\n'
            '    rng.shuffle(order)\n'
            '    batches = [order[i:i + batch_size] for i in range(0, len(order), batch_size)]\n'
            '    print(f"epoch {epoch} batches: {batches}")\n'
            '    assert sorted(order) == all_indices\n'
            '\n'
            'pairs = [data[i] for i in all_indices]\n'
            'assert [y for _, y in pairs] == [2.0 * x for x, _ in pairs]\n'
            'print("seeded index shuffles keep features and targets paired")\n'
        ),
        variant_b="use seed 7 again in a second pass and show that the batch order repeats exactly",
        variant_c="reseed inside the epoch loop with the same integer and show that every epoch is identical",
        mistakes=[
            "Shuffling inputs and targets as separate lists, breaking the row pairing.",
            "Reseeding the generator each epoch, which repeats the same order every time.",
            "Shuffling the validation set during training, leaking order information into evaluation.",
        ],
        q1=(
            "Why shuffle indices instead of shuffling the feature and target lists separately?",
            "Shuffling one index list keeps every feature attached to its target; separate shuffles silently break the pairing.",
        ),
        homework=(
            "Write `make_batches(data, batch_size, seed, epoch)` that copies the index list, shuffles it with a "
            "`random.Random(seed)` created once, and returns the batches. Print the batches for three epochs and "
            "assert each epoch covers every index once; comment why the generator is not recreated per epoch."
        ),
        patterns=["def make_batches(", "random.Random(", "assert "],
        mapping=(
            "`DataLoader(shuffle=True, generator=...)` does exactly this; seeding the generator is how a run stays "
            "reproducible while still seeing a different order each epoch."
        ),
    ),
    108: dict(
        topic="Reading a loss curve",
        idea=(
            "A loss curve is the main diagnostic you have during training, and reading it is a skill rather than a "
            "glance. Plot loss against epoch, not against wall-clock time, and look at the shape: a healthy run "
            "falls quickly at first, then flattens as the model approaches what it can represent. The first question "
            "is whether the curve is going down at all. If it is flat from the start, the learning rate may be too "
            "small, the gradients may be zero, or the labels may not match the inputs. If it rises or oscillates "
            "wildly, the rate is probably too large. The second question is where it flattens: a curve that reaches a "
            "high plateau and stops is underfitting, while one that keeps falling on training data but not on "
            "validation data is overfitting, which is tomorrow's topic. A single loss value says little because "
            "scale depends on the loss function and dataset. The curve says much more because it shows direction and "
            "pace. Today you train a tiny model, record the loss each epoch, and print a sampled curve plus the "
            "improvement per block. Sampling rather than printing every value keeps the output readable. Learn to "
            "describe the curve in words: falling, plateauing, diverging. That description is what you will compare "
            "between runs."
        ),
        code=(
            'data = [(float(x), 2.0 * x) for x in range(1, 7)]\n'
            'w = 0.0\n'
            'rate = 0.03\n'
            'curve = []\n'
            '\n'
            'def loss(w):\n'
            '    return sum((x * w - y) ** 2 for x, y in data) / len(data)\n'
            '\n'
            'def grad(w):\n'
            '    return sum(2 * (x * w - y) * x for x, y in data) / len(data)\n'
            '\n'
            'for epoch in range(1, 21):\n'
            '    w = round(w - rate * grad(w), 4)\n'
            '    curve.append(round(loss(w), 4))\n'
            '    if epoch % 4 == 0:\n'
            '        print(f"epoch {epoch}: loss={curve[-1]}")\n'
            '\n'
            'first_block = curve[0] - curve[3]\n'
            'last_block = curve[-4] - curve[-1]\n'
            'print("first block improvement:", round(first_block, 4))\n'
            'print("last block improvement:", round(last_block, 4))\n'
            'assert curve[-1] < curve[0]\n'
            'print("the curve falls fast, then flattens")\n'
        ),
        variant_b="raise the learning rate until the curve oscillates and print the same sampled points",
        variant_c="start at a weight far from the target and show the initial loss and the final plateau",
        mistakes=[
            "Reporting one final loss instead of the shape of the curve over time.",
            "Connecting points across different learning rates or datasets as if the scale were comparable.",
            "Reading a plateau as success without checking whether training and validation both stalled.",
        ],
        q1=(
            "What does a loss curve that falls quickly and then flattens tell you?",
            "The model is converging: early updates remove large errors, then progress slows as it approaches what it can fit.",
        ),
        homework=(
            "Write `loss_curve(rate, epochs)` that trains a one-weight model and returns the rounded loss at each "
            "epoch. Print every fourth value plus the improvement in the first and last four-epoch blocks, and "
            "comment what the shrinking improvement suggests about the learning rate."
        ),
        patterns=["def loss_curve(", "round(", "print("],
        mapping=(
            "TensorBoard and Weights & Biases plot exactly this curve; the skill of reading direction, slope and "
            "plateau transfers unchanged, only the rendering differs."
        ),
    ),
    109: dict(
        topic="Train and validation splits",
        idea=(
            "Training on the data you evaluate on is the easiest way to lie to yourself, so the first structural "
            "decision in any experiment is the split. Hold out a portion of the examples, train only on the rest, and "
            "treat the held-out set as a stand-in for data the model has never seen. A common starting point is "
            "roughly three quarters training and one quarter validation, though the right ratio depends on how much "
            "data you have; with very little data, cross-validation is better than a single split. The split must be "
            "fixed before training and untouched by shuffling, or the validation set leaks into training. In a small "
            "example, deterministic slicing is clearer than a random split because you can inspect exactly which rows "
            "went where. During training, compute the loss on both sets at the same checkpoints and print them side "
            "by side. Training loss measures fit; validation loss measures generalisation. The gap between them is "
            "the signal that later topics, regularisation and early stopping, are designed to manage. Today you split "
            "twelve examples, train on nine, and watch both numbers fall. If the validation curve turns upward while "
            "training keeps improving, you have caught the beginning of overfitting, and you can act on it rather "
            "than discovering it after deployment."
        ),
        code=(
            'data = [(float(x), 2.0 * x) for x in range(1, 13)]\n'
            'train = [row for i, row in enumerate(data) if i % 4 != 3]\n'
            'val = [row for i, row in enumerate(data) if i % 4 == 3]\n'
            'w = 0.0\n'
            'rate = 0.02\n'
            '\n'
            'def mse(rows, w):\n'
            '    return sum((x * w - y) ** 2 for x, y in rows) / len(rows)\n'
            '\n'
            'def grad(rows, w):\n'
            '    return sum(2 * (x * w - y) * x for x, y in rows) / len(rows)\n'
            '\n'
            'for epoch in range(1, 13):\n'
            '    w = round(w - rate * grad(train, w), 4)\n'
            '    if epoch % 4 == 0:\n'
            '        print(f"epoch {epoch}: train={round(mse(train, w), 4)} val={round(mse(val, w), 4)}")\n'
            '\n'
            'assert not set(train) & set(val)\n'
            'assert mse(val, w) < mse(val, 0.0)\n'
            'print(f"train rows={len(train)} val rows={len(val)}")\n'
        ),
        variant_b="move one row from training to validation and show the new counts and losses",
        variant_c="evaluate on the training rows only and explain why the reported number is too optimistic",
        mistakes=[
            "Computing normalisation statistics on the full dataset before splitting.",
            "Tuning on the validation set repeatedly, then reporting it as an unbiased estimate.",
            "Shuffling validation rows together with training rows between epochs.",
        ],
        q1=(
            "Why must the validation split stay untouched during training?",
            "It stands in for unseen data; any training or tuning on it leaks information and makes the estimate optimistic.",
        ),
        homework=(
            "Write `split_rows(data, holdout_every)` returning a train list and a validation list, then "
            "`evaluate(rows, w)` returning mean squared error. Train on the split, print train and validation "
            "loss at intervals, and comment why the validation rows are never shuffled with the training rows."
        ),
        patterns=["def split_rows(", "def evaluate(", "print("],
        mapping=(
            "`train_test_split` and `DataLoader(val)` express the same rule; the split is made once and validation "
            "data is only ever read, never updated."
        ),
    ),
    110: dict(
        topic="Overfitting and underfitting",
        idea=(
            "Overfitting and underfitting are the two ways a model can fail, and they look different on a learning "
            "curve. Underfitting means the model is too simple, or trained too little, to capture the pattern: "
            "training loss stays high, and validation loss stays high with it. Overfitting means the model has "
            "learned the training examples too closely, including their noise: training loss keeps falling while "
            "validation loss stops improving or rises. The gap between the two curves is the practical signature. "
            "Neither condition is fixed by adding epochs; underfitting needs more capacity or better features, while "
            "overfitting needs constraints, more data, or earlier stopping. A useful diagnostic is to compare a "
            "deliberately weak model with a deliberately memorising one on the same split. The weak model misses the "
            "curve entirely; the memoriser scores perfectly on training rows and badly on rows it has never seen. "
            "Seeing both failures side by side stops you from treating 'low training loss' as success. Today you "
            "build a linear fit and a lookup memoriser on a small nonlinear dataset, then print training and "
            "validation loss for each. The numbers make the definitions concrete. In real work, you decide which "
            "failure you have before choosing a remedy, because the remedies point in opposite directions."
        ),
        code=(
            'train = [(1.0, 1.0), (2.0, 4.0), (3.0, 9.0), (4.0, 16.0), (5.0, 25.0), (6.0, 36.0)]\n'
            'val = [(1.5, 2.25), (2.5, 6.25), (3.5, 12.25)]\n'
            '\n'
            'def mse(rows, predict):\n'
            '    return sum((predict(x) - y) ** 2 for x, y in rows) / len(rows)\n'
            '\n'
            'w = 0.0\n'
            'rate = 0.002\n'
            'for _ in range(300):\n'
            '    w -= rate * sum(2 * (x * w - y) * x for x, y in train) / len(train)\n'
            'linear_train = round(mse(train, lambda x: w * x), 4)\n'
            'linear_val = round(mse(val, lambda x: w * x), 4)\n'
            '\n'
            'table = {x: y for x, y in train}\n'
            'memo_train = round(mse(train, lambda x: table.get(x, 0.0)), 4)\n'
            'memo_val = round(mse(val, lambda x: table.get(x, 0.0)), 4)\n'
            '\n'
            'print(f"underfit linear: train={linear_train} val={linear_val}")\n'
            'print(f"overfit memo:    train={memo_train} val={memo_val}")\n'
            'assert memo_train == 0.0 and memo_val > 1.0\n'
            'assert linear_train > 0.0\n'
            'print("high training loss underfits; zero training loss with high val overfits")\n'
        ),
        variant_b="add one more memoriser entry from the validation set and show that the reported validation score becomes fake",
        variant_c="make the validation points follow the same square law and watch the memoriser still fail them",
        mistakes=[
            "Declaring success from training loss alone, which cannot distinguish memorising from generalising.",
            "Adding capacity to an underfitting model when the real problem is unnormalised inputs.",
            "Tuning the model repeatedly on validation data until it effectively becomes training data.",
        ],
        q1=(
            "What is the visible difference between an underfitting and an overfitting run?",
            "Underfitting has high training and validation loss; overfitting has low training loss with a validation loss that is higher or rising.",
        ),
        homework=(
            "Write `compare_fit(train, val)` that trains a one-weight linear model and also builds a lookup "
            "memoriser, returning each model's training and validation mean squared error. Print all four numbers "
            "and comment which model underfits and which overfits."
        ),
        patterns=["def compare_fit(", "mse(", "print("],
        mapping=(
            "Diagnosing the gap between train and validation curves is the first step in every model review; it "
            "decides whether to add capacity, add data, or add regularisation."
        ),
    ),
    111: dict(
        topic="L2 regularisation",
        idea=(
            "L2 regularisation is a penalty on large weights, added to the loss so the optimiser prefers simpler "
            "explanations. For each weight, add lambda times the weight squared to the loss; the gradient then gains "
            "a term proportional to the weight itself, which pulls it toward zero on every update. The effect is "
            "shrinkage: the model can still fit the data, but it must pay for large parameters, so it settles on a "
            "smoother solution. Lambda controls the trade-off. Set it to zero and you have ordinary training; set it "
            "too high and the weights collapse toward zero, producing underfitting. This is why lambda is tuned on "
            "validation data rather than chosen by intuition. The bias term is usually left unregularised, because "
            "shrinking it just shifts predictions without simplifying the function. A practical detail is to scale "
            "lambda with the loss and dataset, since the penalty competes with the data term; the same lambda is not "
            "meaningful across different batch sizes or loss scales. Today you train the same tiny regression twice, "
            "once plain and once with weight decay, and compare the final weight and data loss. The regularised "
            "weight should be smaller and the training loss slightly higher, which is exactly the trade you asked "
            "for. In frameworks this appears as `weight_decay` or a penalty term, but the arithmetic is the one you "
            "write here."
        ),
        code=(
            'data = [(float(x), 2.0 * x) for x in range(1, 7)]\n'
            '\n'
            'def train(lam, rate=0.01, epochs=200):\n'
            '    w = 0.0\n'
            '    for _ in range(epochs):\n'
            '        g = sum(2 * (x * w - y) * x for x, y in data) / len(data)\n'
            '        g += 2 * lam * w\n'
            '        w = round(w - rate * g, 6)\n'
            '    loss = sum((x * w - y) ** 2 for x, y in data) / len(data)\n'
            '    return w, round(loss, 4)\n'
            '\n'
            'plain_w, plain_loss = train(0.0)\n'
            'reg_w, reg_loss = train(0.5)\n'
            'print(f"plain: w={plain_w} loss={plain_loss}")\n'
            'print(f"L2:    w={reg_w} loss={reg_loss}")\n'
            '\n'
            'assert abs(reg_w) < abs(plain_w)\n'
            'assert reg_loss >= plain_loss\n'
            'print("the penalty shrinks the weight and slightly raises data loss")\n'
        ),
        variant_b="raise lambda to five and show that the weight and the fit both collapse",
        variant_c="apply the penalty to the bias as well and explain why that mostly shifts the model",
        mistakes=[
            "Penalising the bias along with the weights, shrinking the model's overall level.",
            "Using a lambda so large that every weight collapses and the model underfits.",
            "Adding the penalty only at evaluation instead of inside every training gradient.",
        ],
        q1=(
            "What does the L2 penalty add to the gradient of a weight?",
            "A term proportional to the weight itself, which pulls it toward zero on every update and shrinks large values.",
        ),
        homework=(
            "Write `train_l2(data, lam, rate, epochs)` returning the final weight and data loss with the penalty "
            "applied inside the gradient. Run it with lambda zero and lambda 0.5, print both results, and comment "
            "which line adds the regularisation term."
        ),
        patterns=["def train_l2(", "lam", "print("],
        mapping=(
            "`weight_decay` in an optimiser and `kernel_regularizer=l2(...)` in Keras implement this same gradient "
            "addition; lambda is tuned on validation data."
        ),
    ),
    112: dict(
        topic="Dropout",
        idea=(
            "Dropout is a regulariser that randomly switches off units during training so the network cannot rely on "
            "any single path. On each forward pass, every activation is kept with probability p and set to zero "
            "otherwise. At inference nothing is dropped, so the expected scale would be too large unless it is "
            "corrected. The usual fix is inverted dropout: during training, multiply the surviving activations by "
            "one over one minus p, so the expected value matches the inference pass. That way the evaluation code "
            "stays unchanged. Dropout discourages co-adaptation: a unit cannot assume its neighbours will always be "
            "present, so features become more independently useful. It behaves like training an ensemble of thinner "
            "networks that share weights, and at test time you get an average of them. It is most useful in large "
            "fully connected layers and less so in small models, where it can simply remove too much signal. The drop "
            "probability is a hyperparameter, often around 0.2 to 0.5, and it interacts with learning rate and "
            "network width. Crucially, dropout must be active only in training mode; leaving it on at evaluation "
            "makes predictions noisy and irreproducible. Today you apply a seeded mask to a small activation vector, "
            "scale the survivors, and compare the training output with the unchanged evaluation output. The seed "
            "keeps the demonstration deterministic, while in real training the randomness is part of the "
            "regularisation."
        ),
        code=(
            'import random\n'
            '\n'
            'activations = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]\n'
            'p = 0.5\n'
            'rng = random.Random(11)\n'
            'mask = [1 if rng.random() >= p else 0 for _ in activations]\n'
            'scale = 1.0 / (1.0 - p)\n'
            'train_out = [round(a * m * scale, 4) for a, m in zip(activations, mask)]\n'
            'eval_out = activations[:]\n'
            '\n'
            'print("mask:     ", mask)\n'
            'print("train out:", train_out)\n'
            'print("eval out: ", eval_out)\n'
            '\n'
            'assert 0 in mask and 1 in mask\n'
            'assert eval_out == activations\n'
            'print("inverted dropout keeps the expected scale at evaluation")\n'
        ),
        variant_b="change the keep probability to 0.8 and show fewer zeros and a smaller scaling factor",
        variant_c="omit the inverted scale and compare the mean of the training output with the evaluation output",
        mistakes=[
            "Leaving dropout active at evaluation, so predictions change between identical calls.",
            "Forgetting the inverted scaling, so the expected activation magnitude shrinks during training.",
            "Sharing one mask across every layer, which removes the independence between layers.",
        ],
        q1=(
            "Why does inverted dropout multiply surviving activations by one over one minus p?",
            "It keeps the expected activation magnitude equal to the inference pass, so evaluation needs no rescaling.",
        ),
        homework=(
            "Write `dropout(values, p, seed)` that applies an inverted-dropout mask using a seeded `random.Random` "
            "and returns the masked values plus the mask. Print both for p=0.5, then call it again with the same "
            "seed and assert the outputs match; comment which line performs the scaling."
        ),
        patterns=["def dropout(", "random.Random(", "assert "],
        mapping=(
            "`nn.Dropout(p)` and `tf.keras.layers.Dropout(p)` do exactly this, and the model must be in training "
            "mode for the mask to be applied."
        ),
    ),
    113: dict(
        topic="Early stopping",
        idea=(
            "Early stopping uses the validation curve as a brake: train while validation loss improves, and stop when "
            "it has not improved for a few epochs. The number of epochs without improvement is the patience. A small "
            "patience stops quickly and may quit during a temporary plateau; a large one wastes time but is less "
            "likely to stop too soon. You keep the parameters from the epoch with the best validation loss, not the "
            "parameters at the moment you stop, because the later epochs are the ones that stopped helping. Early "
            "stopping is popular because it needs no change to the model or loss, only bookkeeping around the loop. "
            "It also adapts the amount of training to the data instead of fixing an epoch count in advance. The main "
            "trap is using the validation set both to decide when to stop and to report final performance, which "
            "biases the reported number upward; a separate test set is needed for an honest estimate. Another trap is "
            "comparing raw validation losses across learning rates without accounting for noise. Today you train a "
            "small model with a patience counter, print the best epoch, and assert that training stopped before the "
            "epoch limit. The code tracks the best value, the best weights, and the wait count separately, which is "
            "the pattern every training script needs."
        ),
        code=(
            'train = [(float(x), 2.0 * x + (0.5 if x % 2 else -0.5)) for x in range(1, 9)]\n'
            'val = [(float(x), 2.0 * x) for x in range(1, 5)]\n'
            'w = 0.0\n'
            'rate = 0.005\n'
            'patience = 3\n'
            'best = float("inf")\n'
            'best_epoch = 0\n'
            'wait = 0\n'
            'history = []\n'
            '\n'
            'def mse(rows, w):\n'
            '    return sum((x * w - y) ** 2 for x, y in rows) / len(rows)\n'
            '\n'
            'def grad(rows, w):\n'
            '    return sum(2 * (x * w - y) * x for x, y in rows) / len(rows)\n'
            '\n'
            'for epoch in range(1, 41):\n'
            '    w = round(w - rate * grad(train, w), 6)\n'
            '    val_loss = round(mse(val, w), 6)\n'
            '    history.append(val_loss)\n'
            '    if val_loss < best - 0.0001:\n'
            '        best, best_epoch, wait = val_loss, epoch, 0\n'
            '    else:\n'
            '        wait += 1\n'
            '    if epoch % 5 == 0:\n'
            '        print(f"epoch {epoch}: val={val_loss} wait={wait}")\n'
            '    if wait >= patience:\n'
            '        print(f"stopped at epoch {epoch}; best epoch {best_epoch}")\n'
            '        break\n'
            '\n'
            'assert len(history) < 40\n'
            'print(f"best validation loss={round(best, 6)}")\n'
        ),
        variant_b="set patience to one and show that stopping happens on an earlier plateau",
        variant_c="raise the learning rate until validation bounces and explain why patience then matters more",
        mistakes=[
            "Keeping the final weights instead of the weights from the best validation epoch.",
            "Both selecting the stopping point and reporting the score on the same validation rows.",
            "Using a patience of zero, which stops at the first epoch without an improvement.",
        ],
        q1=(
            "Why keep the weights from the best validation epoch rather than the last epoch?",
            "The epochs after the best point have stopped improving validation loss, so the best checkpoint generalises better.",
        ),
        homework=(
            "Write `train_early(data_train, data_val, rate, patience)` returning the best weight, best epoch and "
            "number of epochs run. Print when it stops, assert it stopped before a long epoch limit, and comment "
            "which line increments the patience counter."
        ),
        patterns=["def train_early(", "patience", "print("],
        mapping=(
            "`EarlyStopping(patience=...)` in Keras and callback patterns in PyTorch keep the best checkpoint while "
            "the loop watches validation loss."
        ),
    ),
    114: dict(
        topic="Learning rate schedules",
        idea=(
            "A learning rate schedule changes the step size during training instead of holding it fixed. Early on, a "
            "larger rate moves quickly through bad regions; later, a smaller rate lets the model settle into a "
            "minimum without bouncing around it. Step decay is the simplest schedule: multiply the rate by a factor "
            "every fixed number of epochs. Other common shapes are exponential decay, cosine decay, and warmup "
            "followed by decay. The schedule is a hyperparameter, and a bad one can look like a broken model: decay "
            "too fast and learning stalls, decay too slow and the loss oscillates at the end. A useful habit is to "
            "log the rate alongside the loss so you can tell whether a plateau coincides with a rate change. "
            "Schedules interact with batch size and optimiser choice, so copy a known-good combination before "
            "inventing one. Today you train a tiny linear model with a step schedule, print the rate and loss at "
            "intervals, and assert that the final rate is smaller than the initial one. The arithmetic is "
            "deliberately simple, but the observation is the real lesson: the same gradient, multiplied by a "
            "different step size, produces a very different curve. In practice, schedules are how long runs get both "
            "speed and a clean final descent, and logging the rate is how you debug them."
        ),
        code=(
            'data = [(float(x), 2.0 * x) for x in range(1, 7)]\n'
            'w = 0.0\n'
            'rate = 0.02\n'
            'initial_rate = rate\n'
            '\n'
            'def loss(w):\n'
            '    return sum((x * w - y) ** 2 for x, y in data) / len(data)\n'
            '\n'
            'def grad(w):\n'
            '    return sum(2 * (x * w - y) * x for x, y in data) / len(data)\n'
            '\n'
            'for epoch in range(1, 13):\n'
            '    if epoch > 1 and epoch % 4 == 0:\n'
            '        rate = round(rate * 0.5, 6)\n'
            '    w = round(w - rate * grad(w), 6)\n'
            '    if epoch % 2 == 0:\n'
            '        print(f"epoch {epoch}: rate={rate} loss={round(loss(w), 4)}")\n'
            '\n'
            'assert rate < initial_rate\n'
            'print(f"rate fell from {initial_rate} to {rate}")\n'
        ),
        variant_b="decay every two epochs instead of every four and compare the final loss",
        variant_c="hold the rate fixed and show the loss bouncing near the minimum instead of settling",
        mistakes=[
            "Decaying so early that the model freezes before reaching a useful region.",
            "Logging loss without the current rate, so a plateau cannot be explained.",
            "Applying a schedule in the wrong units, per step instead of per epoch or vice versa.",
        ],
        q1=(
            "Why does a learning rate schedule usually decrease the rate over training?",
            "Large early steps cross bad regions quickly, while smaller late steps settle near a minimum without overshooting.",
        ),
        homework=(
            "Write `train_schedule(data, initial_rate, decay_every, factor, epochs)` returning the final weight, "
            "final rate and loss history. Print the rate beside the loss every other epoch and comment which line "
            "applies the decay."
        ),
        patterns=["def train_schedule(", "rate", "print("],
        mapping=(
            "`StepLR`, `CosineAnnealingLR` and warmup-then-decay are standard scheduler calls; the loop still uses "
            "the same update, only the multiplier changes."
        ),
    ),
    115: dict(
        topic="Normalising inputs",
        idea=(
            "Input normalisation rescales features so they have comparable ranges, usually by subtracting the mean "
            "and dividing by the standard deviation. It matters because gradients depend on input magnitude: a "
            "feature in the hundreds produces much larger gradients than one near one, so a single learning rate is "
            "either too small for one feature or too large for another. Centring also removes the correlation "
            "between the bias and the weights, which makes the loss surface better conditioned and lets gradient "
            "descent move directly toward the minimum instead of zig-zagging. The statistics must come from the "
            "training set only and then be applied unchanged to validation and test data; computing them on the full "
            "dataset leaks information. For images, per-channel statistics are standard; for tabular data, "
            "per-column statistics are. Normalisation is not the same as making data Gaussian, and it does not fix "
            "outliers by itself, though robust scaling can help. Today you compute the mean and standard deviation "
            "of a small set of inputs, transform them, and train a tiny model on the scaled values. Print the "
            "statistics and the final loss, and assert that training actually reduced it. The point is not the "
            "particular numbers but the habit: look at feature scales before blaming the optimiser. Most 'the model "
            "will not learn' reports start with inputs that were never checked."
        ),
        code=(
            'data = [(100.0 + x, float(x)) for x in range(1, 9)]\n'
            'n = len(data)\n'
            'mean = sum(x for x, _ in data) / n\n'
            'var = sum((x - mean) ** 2 for x, _ in data) / n\n'
            'std = var ** 0.5\n'
            '\n'
            'scaled = [((x - mean) / std, y) for x, y in data]\n'
            'print(f"mean={round(mean, 4)} std={round(std, 4)}")\n'
            'print("first scaled:", round(scaled[0][0], 4), "last scaled:", round(scaled[-1][0], 4))\n'
            '\n'
            'w, b, rate = 0.0, 0.0, 0.1\n'
            'for _ in range(60):\n'
            '    gw = sum(2 * (w * x + b - y) * x for x, y in scaled) / n\n'
            '    gb = sum(2 * (w * x + b - y) for x, y in scaled) / n\n'
            '    w, b = round(w - rate * gw, 4), round(b - rate * gb, 4)\n'
            '\n'
            'final = sum((w * x + b - y) ** 2 for x, y in scaled) / n\n'
            'print(f"w={w} b={b} final loss={round(final, 4)}")\n'
            'assert final < 0.01\n'
            'print("centred, scaled inputs train with a usable step size")\n'
        ),
        variant_b="use only centring without dividing by the standard deviation and compare the final loss",
        variant_c="compute the statistics on the validation rows too and explain why that leaks information",
        mistakes=[
            "Computing the mean and standard deviation on the full dataset before splitting.",
            "Applying training statistics to training data but forgetting to apply them at evaluation.",
            "Assuming normalisation makes every distribution Gaussian or fixes outliers by itself.",
        ],
        q1=(
            "Why do differently scaled input features make a single learning rate hard to choose?",
            "Gradients scale with input magnitude, so one rate is too small for small features and too large for large ones.",
        ),
        homework=(
            "Write `normalise(rows)` returning the scaled rows plus the mean and standard deviation, and "
            "`train_scaled(rows, rate, epochs)` returning the final weight, bias and loss. Print the statistics and "
            "the final loss, and comment which line divides by the standard deviation."
        ),
        patterns=["def normalise(", "def train_scaled(", "print("],
        mapping=(
            "`StandardScaler` and `BatchNorm` address related scaling problems; for tabular inputs, fitting the "
            "scaler on training data is the rule."
        ),
    ),
    116: dict(
        topic="Reproducible seeds",
        idea=(
            "Reproducibility is not a luxury; it is how you tell a real improvement from noise. Randomness enters "
            "training in at least three places: parameter initialisation, data shuffling, and regularisation such as "
            "dropout. Each draws from a random number generator, and if that generator is unseeded, two runs of "
            "identical code produce different results. The fix is to create a generator with a fixed integer seed and "
            "pass it explicitly, rather than relying on a global source. In plain Python that means "
            "`random.Random(seed)`; in frameworks there are equivalent seed functions plus settings for GPU and "
            "library-level randomness. A seeded run should produce the same loss history every time, which makes "
            "debugging tractable: change one thing, rerun, and attribute the difference to that change. Be careful "
            "not to reseed inside the training loop, because that restarts the sequence and can produce repeated "
            "patterns. Also remember that reproducibility across machines or library versions is weaker than within "
            "one environment, so record versions alongside the seed. Today you run the same tiny training function "
            "twice with seed forty-two and once with seed seven, then compare the rounded loss histories. The first "
            "two must match exactly; the third should differ. That comparison is a cheap test you can keep in a "
            "project to catch accidental changes to the data pipeline."
        ),
        code=(
            'import random\n'
            '\n'
            'data = [(float(x), 2.0 * x) for x in range(1, 7)]\n'
            '\n'
            'def run(seed):\n'
            '    rng = random.Random(seed)\n'
            '    w = rng.uniform(-1.0, 1.0)\n'
            '    order = list(range(len(data)))\n'
            '    history = []\n'
            '    for _ in range(3):\n'
            '        rng.shuffle(order)\n'
            '        for start in range(0, len(order), 2):\n'
            '            batch = [data[i] for i in order[start:start + 2]]\n'
            '            g = sum(2 * (x * w - y) * x for x, y in batch) / len(batch)\n'
            '            w -= 0.01 * g\n'
            '        loss = sum((x * w - y) ** 2 for x, y in data) / len(data)\n'
            '        history.append(round(loss, 4))\n'
            '    return history\n'
            '\n'
            'a, b, c = run(42), run(42), run(7)\n'
            'print("seed 42 run 1:", a)\n'
            'print("seed 42 run 2:", b)\n'
            'print("seed 7  run 1:", c)\n'
            'assert a == b\n'
            'assert a != c\n'
            'print("same seed reproduces the run; a different seed does not")\n'
        ),
        variant_b="seed the generator once outside `run` and show that the second call no longer matches the first",
        variant_c="add a seeded initial weight but leave shuffling unseeded and explain which source of variation remains",
        mistakes=[
            "Reseeding inside the epoch or step loop, which repeats the same random sequence each time.",
            "Seeding only the data shuffle while leaving initialisation drawn from an unseeded source.",
            "Assuming one seed guarantees identical results across different library or hardware versions.",
        ],
        q1=(
            "Which three places in a basic training run usually consume randomness?",
            "Parameter initialisation, data shuffling, and stochastic regularisation such as dropout.",
        ),
        homework=(
            "Write `seeded_run(seed)` that initialises a weight, shuffles indices and trains a few epochs with a "
            "`random.Random(seed)`, returning the rounded loss history. Call it twice with seed 42 and once with seed "
            "7, print the histories, and assert the first two match."
        ),
        patterns=["def seeded_run(", "random.Random(", "assert "],
        mapping=(
            "`torch.manual_seed` and `tf.random.set_seed` are the framework equivalents; logging the seed and "
            "versions is standard practice for reproducible experiments."
        ),
    ),
    117: dict(
        topic="Debugging a model that will not learn",
        idea=(
            "When a model will not learn, the failure is usually mundane, and a short checklist finds it faster than "
            "intuition. First check the data: are inputs and labels paired correctly, are labels in the expected "
            "range, and is the loss even capable of going down on a tiny subset? Second check the loss and gradients: "
            "print the loss for one batch, verify its scale, and confirm the gradient points in a descent direction. "
            "Third check the update: are you subtracting the gradient rather than adding it, and is the learning rate "
            "sane? A deliberately broken run is a good teaching tool because the symptoms are clear: with the sign "
            "flipped, the loss climbs steadily. Once you reverse the sign, the same loop converges. Other common "
            "causes are zeroed gradients, a learning rate so small that nothing moves, inputs with wildly different "
            "scales, and a bug that updates a copy of the weights instead of the weights themselves. The discipline "
            "is to isolate one cause at a time and use the smallest possible example. Today you run the broken update "
            "for a few epochs, print that the loss rises, then fix the sign and print that it falls. The assertion "
            "captures the diagnosis. In real projects, this same sequence, data, loss, gradient, update, resolves "
            "most training failures before anyone touches the architecture."
        ),
        code=(
            'data = [(float(x), 2.0 * x) for x in range(1, 5)]\n'
            'rate = 0.02\n'
            '\n'
            'def mse(w):\n'
            '    return sum((x * w - y) ** 2 for x, y in data) / len(data)\n'
            '\n'
            'def grad(w):\n'
            '    return sum(2 * (x * w - y) * x for x, y in data) / len(data)\n'
            '\n'
            'def run(sign):\n'
            '    w = 0.0\n'
            '    history = []\n'
            '    for _ in range(8):\n'
            '        w = round(w - sign * rate * grad(w), 4)\n'
            '        history.append(round(mse(w), 4))\n'
            '    return history\n'
            '\n'
            'broken = run(-1)\n'
            'fixed = run(1)\n'
            'print("broken first/last:", broken[0], broken[-1])\n'
            'print("fixed  first/last:", fixed[0], fixed[-1])\n'
            'assert broken[-1] > broken[0]\n'
            'assert fixed[-1] < fixed[0]\n'
            'print("wrong update sign raises the loss; reversing it fixes the run")\n'
        ),
        variant_b="set the learning rate to zero and show that the loss is perfectly flat",
        variant_c="unpair one feature from its label and show the loss cannot reach zero",
        mistakes=[
            "Changing the architecture before checking the data pairing, loss scale and update sign.",
            "Debugging on the full dataset when a single tiny batch would expose the failure faster.",
            "Assuming the loss is broken when the learning rate is merely far too small.",
        ],
        q1=(
            "What is the first thing to inspect when a model's loss is not falling?",
            "The data and the update path: label pairing, loss scale, gradient sign and the learning rate.",
        ),
        homework=(
            "Write `diagnose(data, rate, epochs)` that runs the loop with a sign argument, records the loss "
            "history, and returns both the broken and fixed histories. Print the first and last loss for each, "
            "assert one rises and one falls, and comment which line performs the update."
        ),
        patterns=["def diagnose(", "assert ", "print("],
        mapping=(
            "This four-part check, data, loss, gradient, update, is the same triage used when a real training job "
            "starts with a flat or climbing loss."
        ),
    ),
    118: dict(
        topic="Logging metrics",
        idea=(
            "Logging turns a training run from an anecdote into evidence. At minimum, record the epoch or step, the "
            "training loss, the validation loss when you have one, and the learning rate actually used. Add gradient "
            "norms if you suspect instability, and accuracy or another task metric if loss alone is hard to "
            "interpret. Log at a fixed cadence rather than every step, or the volume hides the trend; every epoch and "
            "every few hundred steps is a common compromise. Structured lines, with named fields, are easier to grep "
            "and plot than free-form sentences. Keep the logger separate from the model so the training loop stays "
            "readable, and make sure a failed run still leaves the last good record. Comparing runs requires the same "
            "fields in the same units, so define the schema once and reuse it. A frequent mistake is logging the loss "
            "before the update, then wondering why the curve lags; decide explicitly whether a row describes the "
            "state before or after the step. Another is logging training loss only, which makes overfitting "
            "invisible. Today you train a tiny model and append a record per epoch with the loss, gradient magnitude "
            "and rate, then print the table and assert the loss fell. The table is small, but it is the same shape "
            "as the dashboards used for real experiments. In practice, good logs are what let you answer 'what "
            "changed?' weeks later."
        ),
        code=(
            'data = [(float(x), 2.0 * x) for x in range(1, 7)]\n'
            'rate = 0.02\n'
            'w = 0.0\n'
            'logs = []\n'
            '\n'
            'def loss(w):\n'
            '    return sum((x * w - y) ** 2 for x, y in data) / len(data)\n'
            '\n'
            'def grad(w):\n'
            '    return sum(2 * (x * w - y) * x for x, y in data) / len(data)\n'
            '\n'
            'for epoch in range(1, 7):\n'
            '    g = grad(w)\n'
            '    w = round(w - rate * g, 4)\n'
            '    row = (epoch, round(loss(w), 4), round(abs(g), 4), rate)\n'
            '    logs.append(row)\n'
            '    print(f"epoch={row[0]} loss={row[1]} grad_norm={row[2]} rate={row[3]}")\n'
            '\n'
            'assert len(logs) == 6\n'
            'assert logs[-1][1] < logs[0][1]\n'
            'print("structured logs make the trend and the rate visible")\n'
        ),
        variant_b="add a validation loss field and print it beside the training loss each epoch",
        variant_c="log before the update instead of after and describe how the table shifts by one row",
        mistakes=[
            "Logging only the final loss, so there is no record of how training progressed.",
            "Mixing units or field names between runs, making comparisons meaningless.",
            "Logging every single step until the useful trend is buried in output volume.",
        ],
        q1=(
            "Which fields belong in a minimal per-epoch training log?",
            "The epoch or step, training loss, validation loss when available, and the learning rate used.",
        ),
        homework=(
            "Write `train_logged(data, rate, epochs)` returning a list of dictionaries with epoch, loss, "
            "gradient magnitude and rate, and printing one line per epoch. Assert the logged loss falls and comment "
            "whether each row records the state before or after the update."
        ),
        patterns=["def train_logged(", "append(", "print("],
        mapping=(
            "Experiment trackers store these same fields at scale; a consistent schema is what makes runs comparable "
            "and dashboards useful."
        ),
    ),
    119: dict(
        topic="Review: training checklist",
        idea=(
            "A training checklist is what you run before trusting a result, and today you assemble the one this "
            "phase has been building. Start with the data: confirm the split is fixed, training and validation rows "
            "do not overlap, and the labels match the inputs. Then confirm determinism: seed initialisation and "
            "shuffling, and check that two runs agree. Next inspect the loop: one epoch is a full pass, steps are "
            "updates, and the loss is computed on the right rows. Watch the curve for divergence, a flat line, or a "
            "widening train-validation gap. Apply the remedies in order: normalise inputs, tune the learning rate, "
            "add L2 or dropout if validation lags, use a schedule for long runs, and stop early when validation "
            "stops improving. Log enough to reconstruct the run. Finally, evaluate once on data that was never used "
            "for tuning, and report the number you actually measured. The checklist is deliberately boring because "
            "boring is what catches mistakes. None of these items is advanced; the failures they prevent are common "
            "at every level. Today you run a compact pipeline that splits, shuffles deterministically, trains with "
            "weight decay and a decaying rate, stops on patience, and prints the checks it passed. Treat the printed "
            "checks as assertions about the process, not decoration. In real work, the checklist is the difference "
            "between a result and a guess."
        ),
        code=(
            'import random\n'
            '\n'
            'data = [(float(x), 2.0 * x + (0.3 if x % 2 else -0.3)) for x in range(1, 13)]\n'
            'train = [row for i, row in enumerate(data) if i % 4 != 3]\n'
            'val = [row for i, row in enumerate(data) if i % 4 == 3]\n'
            'order = list(range(len(train)))\n'
            'rng = random.Random(5)\n'
            'w, b = 0.0, 0.0\n'
            'rate = 0.02\n'
            'best = float("inf")\n'
            'wait = 0\n'
            '\n'
            'def mse(rows):\n'
            '    return sum((w * x + b - y) ** 2 for x, y in rows) / len(rows)\n'
            '\n'
            'for epoch in range(1, 31):\n'
            '    rng.shuffle(order)\n'
            '    for start in range(0, len(order), 3):\n'
            '        batch = [train[i] for i in order[start:start + 3]]\n'
            '        gw = sum(2 * (w * x + b - y) * x for x, y in batch) / len(batch) + 0.002 * w\n'
            '        gb = sum(2 * (w * x + b - y) for x, y in batch) / len(batch)\n'
            '        w, b = round(w - rate * gw, 4), round(b - rate * gb, 4)\n'
            '    rate = round(rate * 0.95, 6)\n'
            '    val_loss = mse(val)\n'
            '    if val_loss < best - 0.00001:\n'
            '        best, wait = val_loss, 0\n'
            '    else:\n'
            '        wait += 1\n'
            '    if wait >= 3:\n'
            '        break\n'
            '\n'
            'print(f"epochs={epoch} w={w} b={b} rate={rate}")\n'
            'print(f"train={round(mse(train), 4)} val={round(best, 4)}")\n'
            'print("split disjoint: ok")\n'
            'print("shuffle covers each index: ok" if sorted(order) == list(range(len(train))) else "shuffle: FAIL")\n'
            'assert not set(train) & set(val)\n'
            'assert w > 1.0\n'
            'print("checklist complete: split, shuffle, regularise, schedule, stop")\n'
        ),
        variant_b="remove the L2 term and compare the final weight and validation loss",
        variant_c="disable early stopping and print how many epochs run before the patience condition would fire",
        mistakes=[
            "Skipping the split check and discovering overlap only after reporting results.",
            "Applying each regulariser at once instead of testing which one the validation curve needs.",
            "Judging the run from training loss while ignoring the held-out number.",
        ],
        q1=(
            "What should you verify before trusting a training result?",
            "That the split is disjoint, randomness is seeded, the loop counts epochs and steps correctly, and the reported score comes from held-out data.",
        ),
        homework=(
            "Write `training_checklist(train, val, seed)` that asserts the split is disjoint, shuffles indices "
            "with a seeded generator, trains with weight decay and a decaying rate, and returns the final weight, "
            "validation loss and a list of passed check names. Print each check and comment which one catches "
            "leakage."
        ),
        patterns=["def training_checklist(", "assert ", "print("],
        mapping=(
            "Production reviews use the same checklist before a model is promoted: data integrity, reproducibility, "
            "curve shape, regularisation and a clean held-out evaluation."
        ),
    ),
})
