# -*- encoding: utf-8 -*-
# classes.py
"""
The classes (or type names) in this project
"""

from dataclasses import dataclass

type Pos = tuple[int, int]
type MazeMap = list[list[int]]
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
