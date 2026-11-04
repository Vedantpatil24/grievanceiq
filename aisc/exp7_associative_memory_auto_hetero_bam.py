"""
Experiment 7: Associative Memory Networks
AIM: Implement Auto Associative, Heteroassociative, and Bidirectional Associative Memory (BAM).
"""


def activate(net_input):
    """Bipolar activation function."""
    if net_input > 0:
        return 1
    elif net_input < 0:
        return -1
    return 0


def autoassociative():
    """Autoassociative Memory Network - train for input [-1, 1, 1, 1]."""
    print("=" * 50)
    print("  Autoassociative Memory Network")
    print("=" * 50)

    original_x = [-1, 1, 1, 1]
    n = len(original_x)

    # Train: W = x^T * x (outer product)
    W = [[original_x[i] * original_x[j] for j in range(n)] for i in range(n)]

    choice = 1
    while choice == 1:
        print(f"\n{'-' * 50}")
        x = list(map(int, input("Enter 4 elements of test vector (space-separated): ").split()))

        # Show weight matrix
        print("\nWeight Matrix W:")
        for row in W:
            print("\t".join(str(v) for v in row))

        # Compute net input y_in = x * W
        y_in = [sum(x[i] * W[i][j] for i in range(n)) for j in range(n)]
        print(f"\nNet input y_inj = {y_in}")

        # Apply activation
        y = [activate(v) for v in y_in]
        print(f"Output after activation y = {y}")

        # Check correctness
        if y == original_x:
            print("\nResult: Correct response is obtained.")
        else:
            print("\nResult: Incorrect response. The network did not recognize the input.")

        choice = int(input("\nTest another input? (1 for Yes, 0 for No): "))


def heteroassociative():
    """Heteroassociative Memory Network."""
    print("\n" + "=" * 50)
    print("  Heteroassociative Memory Network")
    print("=" * 50)

    # Training data
    S = [[1, 0, 0, 0], [1, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 1]]
    T = [[0, 1], [0, 1], [1, 0], [1, 0]]

    input_size = 4
    output_size = 2

    # Train: W = sum(S^T * T)
    W = [[0] * output_size for _ in range(input_size)]
    for p in range(4):
        for i in range(input_size):
            for j in range(output_size):
                W[i][j] += S[p][i] * T[p][j]

    choice = 1
    while choice == 1:
        print(f"\n{'-' * 50}")
        x = list(map(int, input("Enter 4 elements of test vector (e.g., 1 1 0 0): ").split()))

        print("\nTarget Matrix T (Training Targets):")
        for row in T:
            print("\t".join(str(v) for v in row))

        print("\nTrained Weight Matrix W:")
        for row in W:
            print("\t".join(str(v) for v in row))

        # Compute net input
        y_in = [sum(x[i] * W[i][j] for i in range(input_size)) for j in range(output_size)]
        print(f"\nNet input y_inj = {y_in}")

        # Apply activation
        y = [1 if v > 0 else 0 for v in y_in]
        print(f"Output after activation y = {y}")

        choice = int(input("\nTest another input? (1 for Yes, 0 for No): "))


def bam():
    """Bidirectional Associative Memory (BAM) Network."""
    print("\n" + "=" * 50)
    print("  Bidirectional Associative Memory (BAM)")
    print("=" * 50)

    # Patterns: E and F (15 elements each, bipolar)
    X = [
        [1, 1, 1, 1, -1, -1, 1, 1, 1, 1, -1, -1, 1, 1, 1],       # E
        [1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1, -1, -1]      # F
    ]
    Y = [[-1, 1], [1, 1]]  # Targets

    input_size = 15
    output_size = 2

    # Train: W = sum(X^T * Y)
    W = [[0] * output_size for _ in range(input_size)]
    for p in range(2):
        for i in range(input_size):
            for j in range(output_size):
                W[i][j] += X[p][i] * Y[p][j]

    while True:
        print(f"\n{'=' * 60}")
        print("1. Input (15 elements) -> Output (Forward Recall)")
        print("2. Output (2 elements) -> Input (Backward Recall)")
        print("3. Exit")
        choice = int(input("Select an option: "))

        if choice == 1:
            x_test = list(map(int, input("\nEnter 15 bipolar elements (-1 or 1):\n> ").split()))

            y_in = [sum(x_test[i] * W[i][j] for i in range(input_size)) for j in range(output_size)]
            print(f"Net Output y_inj = {y_in}")

            y_out = [activate(v) for v in y_in]
            print(f"Final Activated Output = {y_out}")

        elif choice == 2:
            y_test = list(map(int, input("\nEnter 2 bipolar elements (-1 or 1):\n> ").split()))

            x_in = [sum(y_test[j] * W[i][j] for j in range(output_size)) for i in range(input_size)]
            print(f"Net Input x_inj = {x_in}")

            x_out = [activate(v) for v in x_in]
            print(f"Final Activated Input = {x_out}")

        elif choice == 3:
            print("Exiting...")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    print("Select which network to run:")
    print("1. Autoassociative Memory")
    print("2. Heteroassociative Memory")
    print("3. Bidirectional Associative Memory (BAM)")
    print("4. Run All")

    ch = int(input("Enter choice: "))
    if ch == 1:
        autoassociative()
    elif ch == 2:
        heteroassociative()
    elif ch == 3:
        bam()
    elif ch == 4:
        autoassociative()
        heteroassociative()
        bam()
