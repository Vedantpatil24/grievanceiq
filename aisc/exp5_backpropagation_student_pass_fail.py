"""
Experiment 5: Back Propagation Neural Network - Student Pass/Fail Classifier
AIM: Implement backpropagation for a simple student pass/fail binary classifier.
Uses a 2-input, 2-hidden, 1-output network with sigmoid activation.
"""

import math
import random


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def print_weight_update(name, old_w, delta, new_w):
    print(f"  {name:<8} | {old_w:>8.4f} | {delta:>8.4f} | {new_w:>8.4f}")


def main():
    limit = int(input("Enter the limit (number of epochs) for training: "))

    # Generate 10 random patterns
    random.seed(42)
    patterns = []
    for _ in range(10):
        x1 = random.random()
        x2 = random.random()
        t = 1.0 if (x1 + x2 > 1.0) else 0.0
        patterns.append((x1, x2, t))

    # Print training data
    print("\nGenerated Training Data (10 Random Patterns)")
    print("=" * 56)
    print(f"{'Sample':>6} | {'x1 (Study)':>10} | {'x2 (Attendance)':>15} | {'Target':>6}")
    print("-" * 56)
    for i, (x1, x2, t) in enumerate(patterns):
        print(f"  {i+1:<4} | {x1:>10.4f} | {x2:>15.4f} | {int(t):>6}")
    print("=" * 56 + "\n")

    # Learning rate
    alpha = 0.25

    # Initial weights (Input to Hidden)
    v11, v21, v01 = 0.6, -0.1, 0.3
    v12, v22, v02 = -0.3, 0.4, 0.5

    # Initial weights (Hidden to Output)
    w1, w2, w0 = 0.4, 0.1, -0.2

    print(f"Starting Backprop Walkthrough for {limit} Epoch(s)")

    for epoch in range(1, limit + 1):
        print(f"\n{'=' * 55}")
        print(f"{'EPOCH ' + str(epoch):^55}")
        print(f"{'=' * 55}\n")

        for i, (x1, x2, t) in enumerate(patterns):
            print(f"PATTERN {i+1} - [{x1:.4f}, {x2:.4f}], target = {int(t)}")
            print("Feedforward:")

            z1_in = v01 + (x1 * v11) + (x2 * v21)
            z1 = sigmoid(z1_in)
            print(f"  z1_in = {z1_in:.4f} => z1 = f(z1_in) = {z1:.4f}")

            z2_in = v02 + (x1 * v12) + (x2 * v22)
            z2 = sigmoid(z2_in)
            print(f"  z2_in = {z2_in:.4f} => z2 = f(z2_in) = {z2:.4f}")

            y_in = w0 + (z1 * w1) + (z2 * w2)
            y = sigmoid(y_in)
            print(f"  y_in = {y_in:.4f} => y = f(y_in) = {y:.4f}\n")

            # Output error
            delta_y = (t - y) * y * (1.0 - y)
            print(f"Output error: delta_y = {delta_y:.4f}\n")

            # Output weight updates
            print("Output weight updates:")
            print(f"  {'Weight':<8} | {'Old':>8} | {'Delta':>8} | {'New':>8}")
            print("  " + "-" * 42)

            dw1 = alpha * delta_y * z1
            dw2 = alpha * delta_y * z2
            dw0 = alpha * delta_y * 1.0

            print_weight_update("W1", w1, dw1, w1 + dw1)
            print_weight_update("W2", w2, dw2, w2 + dw2)
            print_weight_update("W0", w0, dw0, w0 + dw0)

            w1 += dw1
            w2 += dw2
            w0 += dw0

            # Backpropagate to hidden layer
            print("\nBackpropagate to hidden layer:")
            delta_in_z1 = delta_y * (w1 - dw1)
            delta_z1 = delta_in_z1 * z1 * (1.0 - z1)
            delta_in_z2 = delta_y * (w2 - dw2)
            delta_z2 = delta_in_z2 * z2 * (1.0 - z2)
            print(f"  delta_z1 = {delta_z1:.4f}, delta_z2 = {delta_z2:.4f}\n")

            print("Hidden weight updates:")
            print(f"  {'Weight':<8} | {'Old':>8} | {'Delta':>8} | {'New':>8}")
            print("  " + "-" * 42)

            dv11 = alpha * delta_z1 * x1
            dv21 = alpha * delta_z1 * x2
            dv01 = alpha * delta_z1 * 1.0
            dv12 = alpha * delta_z2 * x1
            dv22 = alpha * delta_z2 * x2
            dv02 = alpha * delta_z2 * 1.0

            print_weight_update("V11", v11, dv11, v11 + dv11)
            print_weight_update("V21", v21, dv21, v21 + dv21)
            print_weight_update("V01", v01, dv01, v01 + dv01)
            print_weight_update("V12", v12, dv12, v12 + dv12)
            print_weight_update("V22", v22, dv22, v22 + dv22)
            print_weight_update("V02", v02, dv02, v02 + dv02)

            v11 += dv11; v21 += dv21; v01 += dv01
            v12 += dv12; v22 += dv22; v02 += dv02
            print("-" * 55 + "\n")

    # Summary
    print(f"Summary After {limit} Epoch(s) ({limit * 10} total patterns processed)")
    print("=" * 40)
    print(f"V11: {v11:.4f} | V21: {v21:.4f} | V01: {v01:.4f}")
    print(f"V12: {v12:.4f} | V22: {v22:.4f} | V02: {v02:.4f}")
    print(f"W1:  {w1:.4f}  | W2:  {w2:.4f}  | W0:  {w0:.4f}\n")

    # Prediction phase
    print("=" * 40)
    print("       TRAINING COMPLETE")
    print("=" * 40)
    print("Now let's test the trained network!")

    while True:
        test_x1 = float(input("\nEnter x1 (Study hours, 0.0 to 1.0): "))
        test_x2 = float(input("Enter x2 (Attendance/Sleep, 0.0 to 1.0): "))

        z1_in = v01 + (test_x1 * v11) + (test_x2 * v21)
        z1 = sigmoid(z1_in)
        z2_in = v02 + (test_x1 * v12) + (test_x2 * v22)
        z2 = sigmoid(z2_in)
        y_in = w0 + (z1 * w1) + (z2 * w2)
        y = sigmoid(y_in)

        print(f"\n--- Prediction Results ---")
        print(f"Network raw output (Probability): {y:.4f}")
        print(f"Result: {'PASS (1)' if y >= 0.5 else 'FAIL (0)'}")

        cont = input("\nTest another student? (y/n): ")
        if cont.lower() != 'y':
            break

    print("Exiting program. Goodbye!")


if __name__ == "__main__":
    main()
