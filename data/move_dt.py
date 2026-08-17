# -*- encoding: utf-8 -*-
# move_data.py
"""
Move data
"""

from dataclasses import dataclass
import pygame

from data.aliases import Pos


@dataclass
class MoveData:
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
