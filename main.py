# -*- encoding: utf-8 -*-
# main.py
"""
**A maze game**\n
* start pos: the left upper corner of the maze\n
* end pos: the right down corner of the maze\n
* rule: use WASD to move, Escape to exit when you win\n
====\n\n====\n
By *Cozy_wa*\n
Email: ``Cozy_wa_9149U4@outlook.com``\n
"""

import ctypes
import os
import platform
import random
import threading
import time
import typing
from dataclasses import dataclass

import json5  # A JSON parser library with comments
import pygame

type Pos = tuple[int, int]
type Maze = list[list[int]]
type Color = tuple[int, int, int]

# Initialize pygame
pygame.init()


@dataclass
class GameConfig:
    width: int
    height: int
    title: str
    cell_size: int
    seed: int  # seed, Control random map generation
    tick: int
    move_delay: int
    wall_color: Color
    road_color: Color
    exit_color: Color
    player_color: Color
    start_color: Color

    @property
    def window_width(self) -> int:
        return self.width * self.cell_size

    @property
    def window_height(self) -> int:  # noqa: N802
        return self.height * self.cell_size


@dataclass
class MoveData:
    """Mobile-related data"""
    # Move keys
    up_key: int
    down_key: int
    left_key: int
    right_key: int
    # Move directions
    move_dir: dict[int, Pos]


DEFAULT_CONFIG: dict[str, typing.Any] = {
    "WINDOW": {"WIDTH": 41, "HEIGHT": 35, "TITLE": "Maze"},
    "CELL_SIZE": 15,
    "SEED": None,
    "Tick": 60,
    "MoveDelay": 70,
    "COLOR": {
        "WALL": [0, 0, 0],
        "ROAD": [255, 255, 255],
        "RED": [255, 0, 0],
        "GREEN": [0, 255, 0],
        "BLUE": [0, 0, 255]
    }
}
_CONFIG = DEFAULT_CONFIG


def initial_setup(config: dict[str, typing.Any]) -> GameConfig:
    """Do the initial setup and return"""
    colors: dict[str, Color] = config["COLOR"]
    window: dict[str, typing.Any] = config["WINDOW"]

    return GameConfig(
        width=window["WIDTH"],
        height=window["HEIGHT"],
        title=window["TITLE"],
        cell_size=config["CELL_SIZE"],
        seed=config["SEED"],
        tick=config["Tick"],
        move_delay=config["MoveDelay"],
        wall_color=tuple(colors["WALL"]),
        road_color=tuple(colors["ROAD"]),
        exit_color=tuple(colors["RED"]),
        player_color=tuple(colors["GREEN"]),
        start_color=tuple(colors["BLUE"])
    )


# Load configuration
config_path = os.path.abspath("config.jsonc")
if os.path.exists(config_path):
    with open(config_path, encoding='utf-8') as config_file:
        _CONFIG = json5.load(config_file)  # If got the configuration, replace it with the one in the file
else:
    print("No config file.\nUse default config")

try:
    setting: GameConfig = initial_setup(_CONFIG)
except KeyError:
    print("\033[31m-Invalid config file.\n\033[33m-Use default config.\033[0m")
    setting = initial_setup(DEFAULT_CONFIG)

move_data: MoveData = MoveData(
    up_key=pygame.K_w,
    down_key=pygame.K_s,
    left_key=pygame.K_a,
    right_key=pygame.K_d,
    move_dir={
        pygame.K_w: (0, -1),
        pygame.K_s: (0, 1),
        pygame.K_a: (-1, 0),
        pygame.K_d: (1, 0)
    }
)


class Player:
    def __init__(
            self,
            start_pos: Pos,
            exit_pos: Pos,
            maze: Maze,
            screen
    ) -> None:
        """
        :param start_pos: Player's starting coordinates
        :param exit_pos: The location of exit
        :param maze: The data of maze
        :param screen: screen (pygame)
        """
        self.x, self.y = start_pos
        self.exit_x, self.exit_y = exit_pos
        self.maze: Maze = maze

        self.screen = screen
        self.current_direction: int | None = None  # Record the direction of the last successful move (key value)
        self.last_key: int | None = None  # Records the last arrow key pressed (updated by external events)

    @property
    def is_win(self) -> bool:
        return (self.x == self.exit_x) and (self.y == self.exit_y)

    def move(self, move_keys: dict) -> None:
        """Move: Prioritize Turns - The last key pressed while turning takes priority"""
        # Get all the pressed arrow keys
        pressed: list[int] = [got_key for got_key, is_put in move_keys.items() if is_put]
        if not pressed:
            return  # No key pressed, returning directly

        current_dir: int | None = self.current_direction

        # Divided into non-current direction (turning) and current direction
        # A key (turn) different from last time
        turns: list[int] = [
            put_key for put_key in pressed if put_key != current_dir
        ] if current_dir is not None else pressed
        # The same key as last time
        same: list[int] = [
            put_key for put_key in pressed if put_key == current_dir
        ] if current_dir is not None else []

        # Build order: In the turn group, the key pressed last comes first, the rest stay in their original order
        if self.last_key is not None and self.last_key in turns:
            # Move last_key to the very front of turns
            turns.remove(self.last_key)
            order: list[int] = [self.last_key] + turns + same  # Handling: last key pressed -> turn key -> straight key
        else:
            order = turns + same

        # Try moving one by one, and exit immediately once successful
        for key in order:
            dx, dy = move_data.move_dir[key]
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < setting.width and 0 <= ny < setting.height and self.maze[ny][nx] > -1:
                self.x = nx
                self.y = ny
                self.current_direction = key  # Update current direction
                return  # Move just one step

    def draw(self) -> None:
        pygame.draw.rect(
            self.screen,
            setting.player_color,
            (self.x * setting.cell_size, self.y * setting.cell_size, setting.cell_size, setting.cell_size)
        )


def generate_maze() -> tuple[Maze, int, int]:
    """
    Generate a maze, with the end at the longest path
    :return: The data of maze and the position of the end
    """
    # Initialize a binary list for the maze (all walls)
    maze: Maze = [[-1] * setting.width for _ in range(setting.height)]
    maze[0][0]: int = 0  # Mark the entrance as an empty lot (distance is 0)

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
            if 0 <= nx < setting.width and 0 <= ny < setting.height and maze[ny][nx] == -1:
                neighbors.append((nx, ny))

        if neighbors:
            next_x, next_y = random.choice(neighbors)
            maze[(next_y + y) // 2][(next_x + x) // 2] = distance
            maze[next_y][next_x] = distance  # Open up this road
            stack.append(((next_x, next_y), distance))
        else:
            # Delete the points that are no longer valid, go back to the previous point, and continue branching
            stack.pop()

    exit_x, exit_y = 0, 0

    # Find the point with the greatest distance (if there are multiple, take the first one)
    max_dist = -float('inf')
    for y in range(setting.height):
        for x in range(setting.width):
            if maze[y][x] > max_dist:
                max_dist = maze[y][x]
                exit_x, exit_y = x, y

    return maze, exit_x, exit_y


def main() -> None | typing.NoReturn:
    def windows_show_message_box(tip: str, title: str) -> None:
        """Show popup"""
        ctypes.windll.user32.MessageBoxW(0, tip, title, 0)  # noqa: F821

    is_windows = platform.system() == "Windows"
    # Handle the original script document
    document: str = __doc__.replace('\n\n', '\n') if __doc__ is not None else ""
    if document:
        if is_windows:
            windows_show_message_box(document, "Notes")
        else:
            print("Notes:\n", document)

    def graphic() -> None:
        screen.blit(visible_surface, (0, 0))
        player.draw()
        pygame.display.update()

    def update_cell(draw_x: int, draw_y: int) -> None:
        rect: tuple[int, int, int, int] = (
            draw_x * setting.cell_size,
            draw_y * setting.cell_size,
            setting.cell_size,
            setting.cell_size
        )
        if maze[draw_y][draw_x] > 0:
            pygame.draw.rect(visible_surface, setting.road_color, rect)
        elif maze[draw_y][draw_x] == 0:  # Draw start
            pygame.draw.rect(visible_surface, setting.start_color, rect)
        if draw_x == exit_x and draw_y == exit_y:  # Update end
            pygame.draw.rect(visible_surface, setting.exit_color, rect)

    def reveal_area(cx: int = 0, cy: int = 0) -> None:
        """
        Light the cell which passed
        :param cx: X-coordinate of the lit center
        :param cy: Y-coordinate of the lit center
        """
        for dx, dy in move_data.move_dir.values():
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < setting.width and 0 <= ny < setting.height and not explored[ny][nx]:
                explored[ny][nx] = True  # Edit explored list
                update_cell(nx, ny)

    random.seed(setting.seed)
    screen = pygame.display.set_mode((setting.window_width, setting.window_height))
    pygame.display.set_caption(setting.title)

    # Clock that controls movement speed
    clock = pygame.time.Clock()
    maze, exit_x, exit_y = generate_maze()

    explored = [[False] * setting.width for _ in range(setting.height)]  # Explored list, True means lit up
    visible_surface = pygame.Surface((setting.window_width, setting.window_height))
    visible_surface.fill(setting.wall_color)
    reveal_area()

    player = Player((0, 0), (exit_x, exit_y), maze, screen)
    # Last move time: if the interval current_time - last_move_time is less than move_delay, moving is not allowed
    last_move_time = 0
    win = False
    running = True

    def event_handle() -> None:
        nonlocal running
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in move_data.move_dir:  # 移动
                    player.last_key = event.key

    start_time = time.time()

    while running:
        # Draw game elements
        graphic()
        clock.tick(setting.tick)

        current_time = pygame.time.get_ticks()
        event_handle()

        # Move if the time gap isn’t enough or victory doesn’t allow moving
        keys = pygame.key.get_pressed()  # Check if the button is being held down
        # The pressed state of the movement key
        move_keys = {key: keys[key] for key in move_data.move_dir}
        if current_time - last_move_time > setting.move_delay and not win:
            if any(move_keys):
                old_x, old_y = player.x, player.y
                player.move(move_keys)
                if (player.x, player.y) != (old_x, old_y):
                    reveal_area(player.x, player.y)  # Reveal around the new location
                    last_move_time = current_time  # Set the last move time to the current time

        # Check if reach end
        if not win and player.is_win:
            win = True
            finish_time = time.time()

            used_time = finish_time - start_time
            # Reveal the full map after victory
            for y in range(setting.height):
                for x in range(setting.width):
                    if not explored[y][x]:
                        explored[y][x] = True
                        update_cell(x, y)
            graphic()
            if is_windows:
                threading.Thread(
                    target=windows_show_message_box,
                    args=(
                        f"Used {used_time}s",
                        "Pass successfully"
                    ),
                    daemon=True
                ).start()  # Show popup, daemon control window ends when the main process ends
            else:
                print("Pass successfully\n", f"Used {used_time}s")
            while running:  # Wait for exit
                event_handle()
                clock.tick(setting.tick)

    pygame.quit()


if __name__ == '__main__':
    main()
