# -*- encoding: utf-8 -*-
# generator.py
"""
The maze generator
"""

import random
from data.aliases import Pos, MazeMap
from data.config_analysis import setting


def generate_maze() -> tuple[MazeMap, int, int]:
    """
    Generate a maze, with the end at a random position
    :return: The data of maze and the position of the end
    """
    directions: tuple[Pos, ...] = (
        (-2, 0),
        (2, 0),
        (0, -2),
        (0, 2)
    )
    random.seed(setting.seed)

    # Initialize a binary list for the maze (all walls)
    maze_map: MazeMap = [[False] * setting.width for _ in range(setting.height)]
    maze_map[0][0]: int = True  # Mark the entrance as an empty lot

    stack: list[Pos] = [(0, 0)]  # Store branch nodes to return to the previous branch after a branch ends
    ends: list[Pos] = []  # Store the ends

    backed: bool = False
    while stack:  # If there are generated units in the pile
        x, y = stack[-1]  # Get the last generated unit from the stack
        neighbors: list[Pos] = []

        # If the direction of the straight line with one space in between is a wall, mark it
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if all((0 <= nx < setting.width, 0 <= ny < setting.height)) and not maze_map[ny][nx]:
                neighbors.append((nx, ny))

        if neighbors:
            backed: bool = False
            next_x, next_y = random.choice(neighbors)
            maze_map[(next_y + y) // 2][(next_x + x) // 2] = True
            maze_map[next_y][next_x] = True  # Open up this road
            stack.append((next_x, next_y))
        else:
            if not backed:
                ends.append((x, y))
            backed = True
            # Delete the points that are no longer valid, go back to the previous point, and continue branching
            stack.pop()

    # Choose a random cell as the exit from ends
    exit_x, exit_y = random.choice(ends)

    return maze_map, exit_x, exit_y
