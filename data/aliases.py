# -*- encoding: utf-8 -*-
# aliases.py
"""
The type aliases in this project
"""
import pygame

type Pos = tuple[int, int]
type MazeMap = list[list[bool]]
type Color = tuple[int, int, int]
type Rect = tuple[int, int, int, int]
type RealNum = int | float
type Surface = pygame.surface.Surface
