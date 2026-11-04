"""
Experiment 8: Fuzzy Logic - Fuzzy Sets and Fuzzy Relations
AIM: Implement Fuzzy Sets and Fuzzy Relations for a given problem statement.
Covers: Union, Intersection, Complement, Algebraic/Bounded operations,
        Cartesian Product, and Max-Min / Max-Product Composition.
"""


def format_num(value):
    """Format number: remove trailing zeros."""
    if abs(value) < 1e-9:
        value = 0.0
    s = f"{value:.2f}".rstrip('0').rstrip('.')
    return s


def print_fuzzy_set(A, elements):
    """Display fuzzy set in notation like { 0.1/0 + 0.2/1 + ... }."""
    items = [f"{format_num(A[i])}/{elements[i]}" for i in range(len(A))]
    print("{ " + " + ".join(items) + " }")


def fuzzy_union(A, B):
    return [max(a, b) for a, b in zip(A, B)]


def fuzzy_intersection(A, B):
    return [min(a, b) for a, b in zip(A, B)]


def fuzzy_complement(A):
    return [1.0 - a for a in A]


def print_result(name, result, elements):
    print(f"{name} = ", end="")
    print_fuzzy_set(result, elements)


def question7():
    """Fuzzy Set Operations (Q7)."""
    print(f"\n{'=' * 60}")
    print("QUESTION 7 - FUZZY SET OPERATIONS")
    print(f"{'=' * 60}")

    elements = [0, 1, 2, 3, 4]
    A = [0.1, 0.2, 0.4, 0.6, 1.0]
    B = [1.0, 0.5, 0.7, 0.3, 0.0]

    print("\nGiven:")
    print("A = ", end=""); print_fuzzy_set(A, elements)
    print("B = ", end=""); print_fuzzy_set(B, elements)
    print()

    A_bar = fuzzy_complement(A)
    B_bar = fuzzy_complement(B)
    A_union_B = fuzzy_union(A, B)

    print_result("(a) A U B", A_union_B, elements)
    print_result("(b) A ∩ B", fuzzy_intersection(A, B), elements)
    print_result("(c) A-bar", A_bar, elements)
    print_result("(d) B-bar", B_bar, elements)
    print_result("(e) A U A-bar", fuzzy_union(A, A_bar), elements)
    print_result("(f) A ∩ A-bar", fuzzy_intersection(A, A_bar), elements)
    print_result("(g) B U B-bar", fuzzy_union(B, B_bar), elements)
    print_result("(h) B ∩ B-bar", fuzzy_intersection(B, B_bar), elements)
    print_result("(i) A ∩ B-bar", fuzzy_intersection(A, B_bar), elements)
    print_result("(j) A U B-bar", fuzzy_union(A, B_bar), elements)
    print_result("(k) B ∩ A-bar", fuzzy_intersection(B, A_bar), elements)
    print_result("(l) B U A-bar", fuzzy_union(B, A_bar), elements)
    print_result("(m) (A U B)-bar", fuzzy_complement(A_union_B), elements)
    print_result("(n) A-bar ∩ B-bar", fuzzy_intersection(A_bar, B_bar), elements)


def question9():
    """Algebraic and Bounded Operations (Q9)."""
    print(f"\n{'=' * 60}")
    print("QUESTION 9 - ALGEBRAIC AND BOUNDED OPERATIONS")
    print(f"{'=' * 60}")

    elements = [1, 2, 3, 4]
    A = [0.2, 0.3, 0.4, 0.5]
    B = [0.1, 0.2, 0.2, 1.0]

    print("\nGiven:")
    print("A = ", end=""); print_fuzzy_set(A, elements)
    print("B = ", end=""); print_fuzzy_set(B, elements)
    print()

    alg_sum = [a + b - a * b for a, b in zip(A, B)]
    alg_prod = [a * b for a, b in zip(A, B)]
    bnd_sum = [min(1.0, a + b) for a, b in zip(A, B)]
    bnd_diff = [max(0.0, a - b) for a, b in zip(A, B)]

    print("(a) Algebraic Sum (A + B - A*B)")
    print_result("    Result", alg_sum, elements)
    print("\n(b) Algebraic Product (A*B)")
    print_result("    Result", alg_prod, elements)
    print("\n(c) Bounded Sum min(1, A+B)")
    print_result("    Result", bnd_sum, elements)
    print("\n(d) Bounded Difference max(0, A-B)")
    print_result("    Result", bnd_diff, elements)


def question2():
    """Fuzzy Cartesian Product (Q2)."""
    print(f"\n{'=' * 60}")
    print("QUESTION 2 - FUZZY CARTESIAN PRODUCT")
    print(f"{'=' * 60}")

    X = ["x1", "x2", "x3"]
    Y = ["y1", "y2"]
    A = [0.3, 0.7, 1.0]
    B = [0.4, 0.9]

    print("\nGiven:")
    print("A = { " + " + ".join(f"{format_num(A[i])}/{X[i]}" for i in range(3)) + " }")
    print("B = { " + " + ".join(f"{format_num(B[i])}/{Y[i]}" for i in range(2)) + " }")
    print("\nFormula: mu_R(x,y) = min(mu_A(x), mu_B(y))\n")

    R = [[0.0] * 2 for _ in range(3)]
    for i in range(3):
        for j in range(2):
            R[i][j] = min(A[i], B[j])
            print(f"mu_R({X[i]}, {Y[j]}) = min({format_num(A[i])}, {format_num(B[j])}) = {format_num(R[i][j])}")

    print("\nCartesian Product R = A x B:\n")
    print(f"{'':>8}" + "".join(f"{y:>8}" for y in Y))
    for i in range(3):
        print(f"{X[i]:>8}" + "".join(f"{format_num(R[i][j]):>8}" for j in range(2)))


def question3():
    """Fuzzy Relation Composition (Q3)."""
    print(f"\n{'=' * 60}")
    print("QUESTION 3 - FUZZY RELATION COMPOSITION")
    print(f"{'=' * 60}")

    R = [[0.6, 0.3], [0.2, 0.9]]
    S = [[1.0, 0.5, 0.3], [0.8, 0.4, 0.7]]

    print("\nRelation R:")
    print("         y1      y2")
    for i, label in enumerate(["x1", "x2"]):
        print(f"{label}      {'     '.join(str(v) for v in R[i])}")

    print("\nRelation S:")
    print("         z1      z2      z3")
    for i, label in enumerate(["y1", "y2"]):
        print(f"{label}      {'     '.join(str(v) for v in S[i])}")

    # Max-Min Composition
    print(f"\n{'-' * 60}")
    print("(a) MAX-MIN COMPOSITION")
    print(f"T(x,z) = max_y [ min(R(x,y), S(y,z)) ]\n")

    T_mm = [[0.0] * 3 for _ in range(2)]
    for i in range(2):
        for k in range(3):
            v1 = min(R[i][0], S[0][k])
            v2 = min(R[i][1], S[1][k])
            T_mm[i][k] = max(v1, v2)
            print(f"T({i+1},{k+1}) = max(min({R[i][0]}, {S[0][k]}), min({R[i][1]}, {S[1][k]})) = {format_num(T_mm[i][k])}")

    print("\nResult T (Max-Min):")
    print("         z1      z2      z3")
    for i, label in enumerate(["x1", "x2"]):
        print(f"{label}    " + "    ".join(f"{format_num(T_mm[i][k]):>5}" for k in range(3)))

    # Max-Product Composition
    print(f"\n{'-' * 60}")
    print("(b) MAX-PRODUCT COMPOSITION")
    print(f"T(x,z) = max_y [ R(x,y) * S(y,z) ]\n")

    T_mp = [[0.0] * 3 for _ in range(2)]
    for i in range(2):
        for k in range(3):
            v1 = R[i][0] * S[0][k]
            v2 = R[i][1] * S[1][k]
            T_mp[i][k] = max(v1, v2)
            print(f"T({i+1},{k+1}) = max({format_num(v1)}, {format_num(v2)}) = {format_num(T_mp[i][k])}")

    print("\nResult T (Max-Product):")
    print("         z1      z2      z3")
    for i, label in enumerate(["x1", "x2"]):
        print(f"{label}    " + "    ".join(f"{format_num(T_mp[i][k]):>5}" for k in range(3)))


def interactive_fuzzy():
    """Interactive fuzzy set operations with user input."""
    print(f"\n{'=' * 60}")
    print("INTERACTIVE FUZZY SET OPERATIONS")
    print(f"{'=' * 60}")

    elements = [0, 1, 2, 3, 4]

    while True:
        print("\nElements: 0, 1, 2, 3, 4")
        print("\nEnter membership values for A:")
        A = []
        for e in elements:
            while True:
                val = float(input(f"  A[{e}] = "))
                if 0 <= val <= 1:
                    A.append(val)
                    break
                print("  Enter a value between 0 and 1.")

        print("\nEnter membership values for B:")
        B = []
        for e in elements:
            while True:
                val = float(input(f"  B[{e}] = "))
                if 0 <= val <= 1:
                    B.append(val)
                    break
                print("  Enter a value between 0 and 1.")

        A_bar = fuzzy_complement(A)
        B_bar = fuzzy_complement(B)
        A_union_B = fuzzy_union(A, B)

        print(f"\n{'-' * 50}")
        print("A = ", end=""); print_fuzzy_set(A, elements)
        print("B = ", end=""); print_fuzzy_set(B, elements)
        print(f"\nALL FUZZY SET OPERATIONS:")
        print(f"{'-' * 50}")

        print_result("(a) A U B", A_union_B, elements)
        print_result("(b) A ∩ B", fuzzy_intersection(A, B), elements)
        print_result("(c) A-bar", A_bar, elements)
        print_result("(d) B-bar", B_bar, elements)
        print_result("(e) A U A-bar", fuzzy_union(A, A_bar), elements)
        print_result("(f) A ∩ A-bar", fuzzy_intersection(A, A_bar), elements)
        print_result("(g) B U B-bar", fuzzy_union(B, B_bar), elements)
        print_result("(h) B ∩ B-bar", fuzzy_intersection(B, B_bar), elements)
        print_result("(i) A ∩ B-bar", fuzzy_intersection(A, B_bar), elements)
        print_result("(j) A U B-bar", fuzzy_union(A, B_bar), elements)
        print_result("(k) B ∩ A-bar", fuzzy_intersection(B, A_bar), elements)
        print_result("(l) B U A-bar", fuzzy_union(B, A_bar), elements)
        print_result("(m) (A U B)-bar", fuzzy_complement(A_union_B), elements)
        print_result("(n) A-bar ∩ B-bar", fuzzy_intersection(A_bar, B_bar), elements)

        cont = input(f"\n{'-' * 50}\nEnter another pair of fuzzy sets? (Y/N): ")
        if cont.upper() != 'Y':
            break

    print("\nProgram finished.")


if __name__ == "__main__":
    print("*" * 60)
    print("          FUZZY LOGIC OPERATIONS")
    print("*" * 60)

    question7()
    question9()
    question2()
    question3()
    interactive_fuzzy()
