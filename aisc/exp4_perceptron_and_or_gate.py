"""
Experiment 4: Single Layer Perceptron - AND & OR Gate
AIM: Implement AND and OR gate using perceptron learning rule.
Display X1, X2, t, Y, W1, W2, B at end of each epoch.
"""


def activation(yin):
    """Binary activation function."""
    return 1 if yin > 0 else 0


def perceptron_train(gate_name, targets):
    """Train a single layer perceptron for the given gate."""
    print(f"\n{'=' * 70}")
    print(f"  Single Layer Perceptron - {gate_name} Gate")
    print(f"{'=' * 70}")

    X1 = [0, 0, 1, 1]
    X2 = [0, 1, 0, 1]
    t = targets

    W1 = 0.0
    W2 = 0.0
    B = 0.0

    alpha = float(input("Enter learning rate (alpha): "))
    max_epochs = int(input("Enter maximum number of epochs: "))

    converged = False

    for epoch in range(1, max_epochs + 1):
        print(f"\n{'=' * 70}")
        print(f"{'EPOCH ' + str(epoch):^70}")
        print(f"{'=' * 70}")
        print(f"{'Sample':<8}{'X1':<6}{'X2':<6}{'W1':<7}{'W2':<7}{'B':<6}"
              f"{'Target':<8}{'Yin':<8}{'Y':<5}{'dW1':<8}{'dW2':<8}{'dB':<6}"
              f"{'NewW1':<8}{'NewW2':<8}{'NewB':<6}")
        print("-" * 90)

        weight_updated = False

        for i in range(4):
            current_w1 = W1
            current_w2 = W2
            current_b = B

            yin = current_b + (current_w1 * X1[i]) + (current_w2 * X2[i])
            y = activation(yin)

            delta_w1 = 0.0
            delta_w2 = 0.0
            delta_b = 0.0

            if t[i] != y:
                error = t[i] - y
                delta_w1 = alpha * error * X1[i]
                delta_w2 = alpha * error * X2[i]
                delta_b = alpha * error

                W1 = current_w1 + delta_w1
                W2 = current_w2 + delta_w2
                B = current_b + delta_b
                weight_updated = True

            print(f"{i+1:<8}{X1[i]:<6}{X2[i]:<6}{current_w1:<7.1f}{current_w2:<7.1f}"
                  f"{current_b:<6.1f}{t[i]:<8}{yin:<8.1f}{y:<5}"
                  f"{delta_w1:<8.1f}{delta_w2:<8.1f}{delta_b:<6.1f}"
                  f"{W1:<8.1f}{W2:<8.1f}{B:<6.1f}")

        print("-" * 90)

        if not weight_updated:
            converged = True
            print(f"\nSUCCESS: Solution found and converged at Epoch {epoch}!")
            break

    if not converged:
        print("\nFAILURE: Did not find a solution. Epoch limit reached.")

    return W1, W2, B


if __name__ == "__main__":
    print("=" * 70)
    print("  PART A: AND Gate")
    print("=" * 70)
    perceptron_train("AND", [0, 0, 0, 1])

    print("\n\n")

    print("=" * 70)
    print("  PART B: OR Gate")
    print("=" * 70)
    perceptron_train("OR", [0, 1, 1, 1])
