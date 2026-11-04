"""
Experiment 6: Kohonen Self Organizing Feature Maps (SOM) & LVQ Network
AIM: Implement Unsupervised Learning Algorithm - Kohonen SOM & LVQ Network.
"""


def kohonen_som():
    """Kohonen Self Organizing Feature Map implementation."""
    print("=" * 50)
    print("  Kohonen Self Organizing Feature Map (SOM)")
    print("=" * 50)

    original_W = [
        [0.3, 0.2, 0.1, 0.8, 0.4],
        [0.5, 0.6, 0.7, 0.9, 0.2]
    ]

    num_iterations = int(input("How many input vectors would you like to test? "))

    for k in range(num_iterations):
        # Reset weights for each test case
        W = [row[:] for row in original_W]

        print(f"\n{'-' * 50}")
        print(f"Test Case {k + 1}")
        print(f"{'-' * 50}")

        x1 = float(input("Enter value for x1: "))
        x2 = float(input("Enter value for x2: "))
        alpha = float(input("Enter learning rate (alpha): "))

        print(f"\nOriginal Weights Matrix (W):")
        for row in W:
            print("  ".join(f"{v:.2f}" for v in row))

        print(f"\nInput Vector: x1 = {x1}, x2 = {x2}")
        print(f"Learning Rate (alpha) = {alpha}\n")

        # Find winning unit
        min_dist = float('inf')
        winner = -1

        print("Calculated Distances (D(j) = (w1j - x1)^2 + (w2j - x2)^2):")
        for j in range(5):
            dist = (W[0][j] - x1) ** 2 + (W[1][j] - x2) ** 2
            print(f"  D({j+1}) = ({W[0][j]:.2f} - {x1})^2 + ({W[1][j]:.2f} - {x2})^2 = {dist:.4f}")

            if dist < min_dist:
                min_dist = dist
                winner = j

        print(f"\nWinning cluster unit (J) = {winner + 1} with D = {min_dist:.4f}")

        # Update weights
        old_w1 = W[0][winner]
        old_w2 = W[1][winner]
        W[0][winner] = old_w1 + alpha * (x1 - old_w1)
        W[1][winner] = old_w2 + alpha * (x2 - old_w2)

        print(f"\nUpdating weights for Unit {winner + 1}:")
        print(f"  w1{winner+1}(new) = {old_w1:.2f} + {alpha} * ({x1} - {old_w1:.2f}) = {W[0][winner]:.4f}")
        print(f"  w2{winner+1}(new) = {old_w2:.2f} + {alpha} * ({x2} - {old_w2:.2f}) = {W[1][winner]:.4f}")

        print(f"\n{'=' * 50}")
        print(f"FINAL UPDATED WEIGHT MATRIX FOR TEST CASE {k + 1}:")
        for row in W:
            print("  ".join(f"{v:.4f}" for v in row))
        print()


def lvq_network():
    """Learning Vector Quantization (LVQ) Network implementation."""
    print("\n" + "=" * 50)
    print("  LVQ (Learning Vector Quantization)")
    print("=" * 50)

    W = [
        [0.0, 0.0, 1.0, 1.0],   # w1 - Class 1
        [1.0, 0.0, 0.0, 0.0]    # w2 - Class 2
    ]
    weight_classes = [1, 2]

    train_vectors = [
        [0.0, 0.0, 0.0, 1.0],   # T = 2
        [1.0, 1.0, 0.0, 0.0],   # T = 1
        [0.0, 1.0, 1.0, 0.0]    # T = 1
    ]
    train_targets = [2, 1, 1]
    alpha = 0.1

    print("Initial Reference Weights:")
    print(f"  w1 (Class 1): {W[0]}")
    print(f"  w2 (Class 2): {W[1]}\n")

    perfectly_trained = False
    max_epochs = 100

    for epoch in range(1, max_epochs + 1):
        print(f"{'=' * 50}")
        print(f"{'EPOCH ' + str(epoch):^50}")
        print(f"{'=' * 50}")

        matches = 0

        for i, (vec, target) in enumerate(zip(train_vectors, train_targets)):
            print(f"\n{'-' * 50}")
            print(f"Training Vector {i+1}: {vec} | Target Class: {target}")

            # Find winner
            min_dist = float('inf')
            winner = -1
            for j in range(2):
                dist = sum((W[j][d] - vec[d]) ** 2 for d in range(4))
                print(f"  D({j+1}) to w{j+1} = {dist:.4f}")
                if dist < min_dist:
                    min_dist = dist
                    winner = j

            predicted = weight_classes[winner]
            print(f"\n  Winner: w{winner+1} (Class {predicted}), distance = {min_dist:.4f}")

            if predicted == target:
                print(f"  Match! Updating w{winner+1} using addition (+)...")
                for d in range(4):
                    W[winner][d] += alpha * (vec[d] - W[winner][d])
                matches += 1
            else:
                print(f"  Mismatch! Updating w{winner+1} using subtraction (-)...")
                for d in range(4):
                    W[winner][d] -= alpha * (vec[d] - W[winner][d])

            print(f"  Updated w{winner+1}: [{', '.join(f'{v:.2f}' for v in W[winner])}]")

        if matches == len(train_vectors):
            perfectly_trained = True
            print("\n>>> All training vectors correctly classified! Stopping. <<<\n")
            break

    if not perfectly_trained:
        print("\n>>> Max epochs reached. Training stopped. <<<\n")

    print("=" * 50)
    print("TRAINING COMPLETED! Final Weights:")
    print(f"  w1 (Class 1): [{', '.join(f'{v:.4f}' for v in W[0])}]")
    print(f"  w2 (Class 2): [{', '.join(f'{v:.4f}' for v in W[1])}]")
    print("=" * 50)

    # Prediction phase
    choice = input("\nPredict output for a custom test vector? (y/n): ")
    while choice.lower() == 'y':
        test = list(map(float, input("Enter 4 elements (x1 x2 x3 x4): ").split()))

        min_dist = float('inf')
        winner = -1
        for j in range(2):
            dist = sum((W[j][d] - test[d]) ** 2 for d in range(4))
            print(f"  D({j+1}) to w{j+1} = {dist:.4f}")
            if dist < min_dist:
                min_dist = dist
                winner = j

        print(f"\n  PREDICTED OUTPUT CLASS: CLASS {weight_classes[winner]}\n")
        choice = input("Predict another vector? (y/n): ")


if __name__ == "__main__":
    kohonen_som()
    lvq_network()
