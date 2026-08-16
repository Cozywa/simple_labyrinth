# -*- encoding: utf-8 -*-
# classes.py
"""
The classes (or type names) in this project
"""

from dataclasses import dataclass
import pygame
import typing

type Pos = tuple[int, int]
type MazeMap = list[list[bool]]
type Color = tuple[int, int, int]


@dataclass
class GameConfig:
    width: int
    height: int
    title: str
    cell_size: int
    seed: int  # seed, Control random map generation
    tick: int
    wait_tick: int
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
            maze_map: MazeMap,
            screen
    ) -> None:
        """
        :param start_pos: Player's starting coordinates
        :param exit_pos: The location of exit
        :param maze_map: The data of maze
        :param screen: The screen (pygame)
        """
        self.x, self.y = start_pos
        self.exit_x, self.exit_y = exit_pos
        self.maze_map: MazeMap = maze_map

        self.screen = screen
        self.current_direction: int | None = None  # Record the direction of the last successful move (key value)
        self.last_key: int | None = None  # Records the last arrow key pressed (updated by external events)

    @property
    def is_win(self) -> bool:
        return (self.x, self.y) == (self.exit_x, self.exit_y)

    def move(self, allow_get: typing.Callable[[int, int], bool], move_keys: dict) -> None:
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
            if allow_get(nx, ny):
                self.x = nx
                self.y = ny
                self.current_direction = key  # Update current direction
                return  # Move just one step
