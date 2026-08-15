# -*- encoding: utf-8 -*-
# generator.py
"""
The maze generator
"""

import random
from classes import Pos, MazeMap, GameConfig


def generate_maze(setting: GameConfig) -> tuple[MazeMap, int, int]:
    """
    Generate a maze, with the end at the longest path
    :return: The data of maze and the position of the end
    """
    random.seed(setting.seed)

    # Initialize a binary list for the maze (all walls)
    maze_map: MazeMap = [[-1] * setting.width for _ in range(setting.height)]
    maze_map[0][0]: int = 0  # Mark the entrance as an empty lot (distance is 0)

    # Store branch nodes to return to the previous branch after a branch ends
    stack: list[tuple[Pos, int]] = [((0, 0), 0)]
    directions: tuple[Pos, ...] = (
        (-2, 0),
        (2, 0),
        (0, -2),
        (0, 2)
    )
    while stack:  # If there are generated units in the pile
        x, y = stack[-1][0]  # Get the last generated unit from the stack
        distance: int = stack[-1][1] + 1  # Get the distance of this generated cell
        neighbors: list[Pos] = []

        # If the direction of the straight line with one space in between is a wall, mark it
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < setting.width and 0 <= ny < setting.height and maze_map[ny][nx] == -1:
                neighbors.append((nx, ny))

        if neighbors:
            next_x, next_y = random.choice(neighbors)
            maze_map[(next_y + y) // 2][(next_x + x) // 2] = distance
            maze_map[next_y][next_x] = distance  # Open up this road
            stack.append(((next_x, next_y), distance))
        else:
            # Delete the points that are no longer valid, go back to the previous point, and continue branching
            stack.pop()

    exit_x, exit_y = 0, 0

    # Find the point with the greatest distance (if there are multiple, take the first one)
    max_distance = -float('inf')
    for y in range(setting.height):
        for x in range(setting.width):
            if maze_map[y][x] > max_distance:
                max_distance = maze_map[y][x]
                exit_x, exit_y = x, y

    return maze_map, exit_x, exit_y
