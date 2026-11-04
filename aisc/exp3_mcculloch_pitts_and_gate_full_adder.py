"""
Experiment 3: McCulloch Pitts Neuron - AND Gate & Full Adder
AIM: Implement AND Gate using McCulloch Pitts Neuron and design Half and Full Adder.
"""


def and_gate():
    """Find weights and threshold for AND gate using McCulloch Pitts model."""
    print("=" * 50)
    print("McCulloch Pitts Neuron - AND Gate")
    print("=" * 50)

    x1 = [0, 0, 1, 1]
    x2 = [0, 1, 0, 1]
    expected = [0, 0, 0, 1]
    p = 0
    found = False

    for w1 in range(2):
        if found:
            break
        for w2 in range(2):
            if found:
                break
            for theta in range(5):
                if found:
                    break

                print(f"\n----------------------------------")
                print(f"Trying: w1 = {w1}, w2 = {w2}, theta = {theta}, p = {p}")

                correct = True
                for i in range(4):
                    n = (x1[i] * w1) + (x2[i] * w2)
                    calculated = n - p
                    output = 1 if calculated >= theta else 0

                    status = "<--- Correct" if output == expected[i] else "<--- WRONG"
                    if output != expected[i]:
                        correct = False

                    print(f"Input ({x1[i]},{x2[i]}) -> n = {n}, theta = {theta}, "
                          f"calculated = {calculated}, output = {output}, "
                          f"expected = {expected[i]} {status}")

                if correct:
                    print(f"\n{'=' * 34}")
                    print("FINAL SOLUTION")
                    print(f"w1 = {w1}")
                    print(f"w2 = {w2}")
                    print(f"theta = {theta}")
                    print(f"p = {p}")
                    print("=" * 34)
                    found = True
                else:
                    print("This combination does not give AND output.")

    if not found:
        print("\nNo solution found.")


def full_adder():
    """Implement Full Adder using McCulloch Pitts Neuron."""
    print("\n" + "=" * 50)
    print("McCulloch Pitts Neuron - Full Adder")
    print("=" * 50)

    x1 = [0, 0, 0, 0, 1, 1, 1, 1]
    x2 = [0, 0, 1, 1, 0, 0, 1, 1]
    cin = [0, 1, 0, 1, 0, 1, 0, 1]
    p = 0

    # STEP 1: Intermediate SUM S1 = x1 XOR x2
    s1 = []
    for i in range(8):
        z1 = 1 if (x1[i] * 1 + x2[i] * -1) >= 1 else 0
        z2 = 1 if (x1[i] * -1 + x2[i] * 1) >= 1 else 0
        s1.append(1 if (z1 + z2) >= 1 else 0)

    # STEP 2: Final SUM = S1 XOR Cin
    print("STEP 1: FINDING FINAL SUM (s1 XOR cin)")

    # Find weights for z_sum1 = s1 AND NOT cin
    w_s1_1, w_cin_1, theta_sum1 = 0, 0, 0
    for w1 in range(-1, 2):
        for w2 in range(-1, 2):
            for theta in range(3):
                correct = all(
                    (1 if (s1[i] * w1 + cin[i] * w2 - p) >= theta else 0) ==
                    (1 if s1[i] == 1 and cin[i] == 0 else 0)
                    for i in range(8)
                )
                if correct:
                    w_s1_1, w_cin_1, theta_sum1 = w1, w2, theta
                    break
            if correct:
                break
        if correct:
            break

    # Find weights for z_sum2 = NOT s1 AND cin
    w_s1_2, w_cin_2, theta_sum2 = 0, 0, 0
    for w1 in range(-1, 2):
        for w2 in range(-1, 2):
            for theta in range(3):
                correct = all(
                    (1 if (s1[i] * w1 + cin[i] * w2 - p) >= theta else 0) ==
                    (1 if s1[i] == 0 and cin[i] == 1 else 0)
                    for i in range(8)
                )
                if correct:
                    w_s1_2, w_cin_2, theta_sum2 = w1, w2, theta
                    break
            if correct:
                break
        if correct:
            break

    # Combine to get final SUM
    final_sum = []
    for i in range(8):
        z_a = 1 if (s1[i] * w_s1_1 + cin[i] * w_cin_1) >= theta_sum1 else 0
        z_b = 1 if (s1[i] * w_s1_2 + cin[i] * w_cin_2) >= theta_sum2 else 0
        final_sum.append(1 if (z_a + z_b) >= 1 else 0)

    print("SUM weights found successfully.")

    # STEP 3: Finding Carry Out
    print("\nSTEP 2: FINDING CARRY OUT (Cout)")
    c_w1, c_w2, c_w3, cout_theta = 0, 0, 0, 0
    cout_found = False

    for w1 in range(2):
        if cout_found:
            break
        for w2 in range(2):
            if cout_found:
                break
            for w3 in range(2):
                if cout_found:
                    break
                for theta in range(4):
                    correct = all(
                        (1 if (x1[i] * w1 + x2[i] * w2 + cin[i] * w3 - p) >= theta else 0) ==
                        (1 if x1[i] + x2[i] + cin[i] >= 2 else 0)
                        for i in range(8)
                    )
                    if correct:
                        c_w1, c_w2, c_w3, cout_theta = w1, w2, w3, theta
                        cout_found = True
                        print(f"*** Cout SOLUTION FOUND ***")
                        print(f"w1 = {c_w1}, w2 = {c_w2}, w3 = {c_w3}, theta = {cout_theta}")
                        break

    cout_val = [1 if (x1[i] * c_w1 + x2[i] * c_w2 + cin[i] * c_w3) >= cout_theta else 0
                for i in range(8)]

    # Final Truth Table
    print(f"\n{'─' * 40}")
    print("FINAL FULL ADDER TRUTH TABLE")
    print(f"{'─' * 40}")
    print("x1   x2   Cin   |   Sum   Cout")
    print("─" * 30)
    for i in range(8):
        print(f"{x1[i]}    {x2[i]}    {cin[i]}     |    {final_sum[i]}     {cout_val[i]}")
    print("=" * 40)


if __name__ == "__main__":
    and_gate()
    full_adder()
