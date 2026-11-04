"""
Experiment 1: Water Jug Problem using BFS and DFS
AIM: For the Water Jug Problem you have 2 unmarked jugs (4L, 3L, Target = 2L)
Each node is represented as (Jug1, Jug2).
Show search tree how BFS and DFS explore the state space.
"""

from collections import deque


def get_next_states(curr, cap1, cap2):
    j1, j2 = curr
    return [
        (cap1, j2),                                              # Fill jug1
        (j1, cap2),                                              # Fill jug2
        (0, j2),                                                 # Empty jug1
        (j1, 0),                                                 # Empty jug2
        (j1 - min(j1, cap2 - j2), j2 + min(j1, cap2 - j2)),     # Pour jug1 -> jug2
        (j1 + min(j2, cap1 - j1), j2 - min(j2, cap1 - j1)),     # Pour jug2 -> jug1
    ]


def water_jug_bfs(cap1, cap2, target):
    if target > max(cap1, cap2) or target < 0:
        print("Error!! Enter valid target value")
        return
    if cap1 <= 0 or cap2 <= 0:
        print("Error!! Enter valid jug capacities")
        return

    visited = set()
    parent = {}
    queue = deque()

    start = (0, 0)
    queue.append(start)
    visited.add(start)
    parent[start] = None

    found = False
    target_state = None
    level = 0

    print("\n--- Level-wise Graph Explorer (BFS) ---")

    while queue:
        level_size = len(queue)
        level_nodes = list(queue)
        print(f"Level {level} -> {' '.join(str(s) for s in level_nodes)}")

        for _ in range(level_size):
            curr = queue.popleft()

            if curr[0] == target or curr[1] == target:
                target_state = curr
                found = True
                break

            for next_state in get_next_states(curr, cap1, cap2):
                if next_state not in visited:
                    visited.add(next_state)
                    parent[next_state] = curr
                    queue.append(next_state)

        if found:
            break
        level += 1

    if not found:
        print("\nThere is no solution for this target value")
        return

    # Reconstruct path
    path = []
    curr = target_state
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()

    print(f"\nShortest Path to Target ({target}) using BFS:")
    print(" -> ".join(str(s) for s in path))


def water_jug_dfs(cap1, cap2, target):
    if target > max(cap1, cap2) or target < 0:
        print("Error!! Enter valid target value")
        return
    if cap1 <= 0 or cap2 <= 0:
        print("Error!! Enter valid jug capacities")
        return

    visited = set()
    parent = {}
    stack = []

    start = (0, 0)
    stack.append(start)
    visited.add(start)
    parent[start] = None

    found = False
    target_state = None

    print("\n--- Exploring graph using DFS ---")

    while stack:
        curr = stack.pop()

        if curr[0] == target or curr[1] == target:
            target_state = curr
            found = True
            break

        for next_state in reversed(get_next_states(curr, cap1, cap2)):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = curr
                stack.append(next_state)
                print(f"{curr} -> {next_state}")

    if not found:
        print("\nThere is no solution for this target value")
        return

    # Reconstruct path
    path = []
    curr = target_state
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()

    print(f"\nPath to Target ({target}) using DFS:")
    print(" -> ".join(str(s) for s in path))


if __name__ == "__main__":
    cap1 = int(input("Enter capacity of Jug 1: "))
    cap2 = int(input("Enter capacity of Jug 2: "))
    target = int(input("Enter target volume: "))

    repeat = 'y'
    while repeat.lower() == 'y':
        print("\nChoose the method to solve:")
        print("1. BFS (Level-wise Graph)")
        print("2. DFS")
        choice = int(input("Enter your choice (1 or 2): "))

        if choice == 1:
            water_jug_bfs(cap1, cap2, target)
        elif choice == 2:
            water_jug_dfs(cap1, cap2, target)
        else:
            print("Invalid choice!")

        repeat = input("\nWould you like to try the other method? (y/n): ")
