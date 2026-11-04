"""
Experiment 2: 8 Puzzle Problem using A* Search Algorithm
AIM: Start from given state and try to achieve the goal state in 8 puzzle problem.
Uses A* with misplaced tiles heuristic.
"""

import random


def print_matrix(mat):
    for row in mat:
        print(" ".join(f"{x:2d}" for x in row))


def calc_heuristic(mat, goal):
    """Count misplaced tiles (excluding blank/0)."""
    count = 0
    for i in range(3):
        for j in range(3):
            if mat[i][j] != 0 and mat[i][j] != goal[i][j]:
                count += 1
    return count


def is_goal(mat, goal):
    return mat == goal


def copy_matrix(mat):
    return [row[:] for row in mat]


def is_reverse(prev, curr):
    opposites = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}
    return opposites.get(prev) == curr


def solve(start, goal, blank_x, blank_y):
    current = {
        'mat': copy_matrix(start),
        'x': blank_x,
        'y': blank_y,
        'g': 0,
        'h': calc_heuristic(start, goal),
        'move': 'S'
    }
    current['f'] = current['g'] + current['h']

    step = 0
    dx = [0, 0, -1, 1]
    dy = [-1, 1, 0, 0]
    moves = ['L', 'R', 'U', 'D']

    while True:
        print(f"\n===================== STEP {step} ======================")
        print("\nCurrent Matrix:")
        print_matrix(current['mat'])
        print(f"g = {current['g']}, h = {current['h']}, f = {current['f']}")

        if is_goal(current['mat'], goal):
            print("\nGoal Reached!")
            return

        children = []
        print("\nPossible Moves:")

        for i in range(4):
            nx = current['x'] + dx[i]
            ny = current['y'] + dy[i]

            if 0 <= nx < 3 and 0 <= ny < 3:
                if is_reverse(current['move'], moves[i]):
                    continue

                new_mat = copy_matrix(current['mat'])
                new_mat[nx][ny], new_mat[current['x']][current['y']] = \
                    new_mat[current['x']][current['y']], new_mat[nx][ny]

                h = calc_heuristic(new_mat, goal)
                g = current['g'] + 1
                child = {
                    'mat': new_mat,
                    'x': nx,
                    'y': ny,
                    'g': g,
                    'h': h,
                    'f': g + h,
                    'move': moves[i]
                }
                children.append(child)

                print(f"\n Move to {moves[i]}:")
                print_matrix(new_mat)
                print(f" g = {g}, h = {h}, f = {g + h}")

        if not children:
            print("\nNo valid moves available.")
            return

        min_f = min(c['f'] for c in children)
        candidates = [c for c in children if c['f'] == min_f]
        current = random.choice(candidates)

        print(f"\n Chosen Move (min f):")
        print_matrix(current['mat'])
        print(f"g = {current['g']}, h = {current['h']}, f = {current['f']}")

        step += 1
        if step > 1000:
            print("\nMaximum steps exceeded. The algorithm is stuck in a local loop.")
            return


if __name__ == "__main__":
    print("Enter the Initial Matrix (9 numbers, use 0 for empty space):")
    start = []
    blank_x, blank_y = -1, -1
    for i in range(3):
        row = list(map(int, input().split()))
        for j in range(3):
            if row[j] == 0:
                blank_x, blank_y = i, j
        start.append(row)

    print("Enter the Goal Matrix (9 numbers):")
    goal = []
    for i in range(3):
        row = list(map(int, input().split()))
        goal.append(row)

    if blank_x == -1 or blank_y == -1:
        print("Error: No empty space (0) found in the initial matrix.")
    else:
        solve(start, goal, blank_x, blank_y)
