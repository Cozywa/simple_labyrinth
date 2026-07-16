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

import json5  # 带注释的 json 文件解析库
import os
import random
import typing
from collections import deque
from dataclasses import dataclass
import time
import ctypes
import threading

import pygame

# 初始化 pygame
pygame.init()


@dataclass
class GameConfig:
    """游戏配置类"""
    WIDTH: int
    HEIGHT: int
    TITLE: str
    CELL_SIZE: int  # 单元格尺寸
    SEED: int  # 种子 控制 random 地图生成
    TICK: int
    MOVE_DELAY: int
    WALL_COLOR: tuple
    ROAD_COLOR: tuple
    EXIT_COLOR: tuple
    PLAYER_COLOR: tuple
    START_COLOR: tuple

    @property
    def WINDOW_WIDTH(self) -> int:  # noqa: N802
        return self.WIDTH * self.CELL_SIZE

    @property
    def WINDOW_HEIGHT(self) -> int:  # noqa: N802
        return self.HEIGHT * self.CELL_SIZE


@dataclass
class MoveData:
    """移动相关数据"""
    # 移动键
    UP_KEY: int
    DOWN_KEY: int
    LEFT_KEY: int
    RIGHT_KEY: int
    # 方向
    MOVE_DIR: tuple[tuple[int, int], ...]

    @property
    def keys(self):
        """把键整合起来 便于索引"""
        return [self.UP_KEY, self.DOWN_KEY, self.LEFT_KEY, self.RIGHT_KEY]

    def __getitem__(self, index: int) -> int:
        """通过索引获得键"""
        return self.keys[index]


_CONFIG: dict[str, typing.Any] = {  # 默认配置
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

# 读取配置
config_path = os.path.abspath("config.jsonc")
if os.path.exists(config_path):
    with open(config_path, encoding='utf-8') as config:
        _CONFIG = json5.load(config)  # 如果可以获取配置 将配置替换为文件中的

_COLORS = _CONFIG["COLOR"]
_WINDOW = _CONFIG["WINDOW"]

setting: GameConfig = GameConfig(  # 配置
    WIDTH=_WINDOW["WIDTH"],
    HEIGHT=_WINDOW["HEIGHT"],
    TITLE=_WINDOW["TITLE"],
    CELL_SIZE=_CONFIG["CELL_SIZE"],
    SEED=_CONFIG["SEED"],
    TICK=_CONFIG["Tick"],
    MOVE_DELAY=_CONFIG["MoveDelay"],
    WALL_COLOR=tuple(_COLORS["WALL"]),
    ROAD_COLOR=tuple(_COLORS["ROAD"]),
    EXIT_COLOR=tuple(_COLORS["RED"]),
    PLAYER_COLOR=tuple(_COLORS["GREEN"]),
    START_COLOR=tuple(_COLORS["BLUE"])
)

move_data: MoveData = MoveData(
    UP_KEY=pygame.K_w,
    DOWN_KEY=pygame.K_s,
    LEFT_KEY=pygame.K_a,
    RIGHT_KEY=pygame.K_d,
    MOVE_DIR=(
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1)
    )
)


class Player:
    """玩家类"""
    move_method: dict[int, tuple[int, int]] = {  # 移动键与对应
        move_data[0]: (0, -1),
        move_data[1]: (0, 1),
        move_data[2]: (-1, 0),
        move_data[3]: (1, 0)
    }

    def __init__(
        self,
        pos: tuple[int, int],
        maze: list[list[bool]],
        exit_pos: tuple[int, int],
        screen
    ) -> None:
        """
        初始化需要的信息
        :param pos: 玩家初始坐标
        :param maze:
        :param exit_pos:
        :param screen:
        """
        self.x, self.y = pos
        self.maze: list = maze  # 迷宫
        self.exit_x, self.exit_y = exit_pos  # 出口

        self.screen = screen  # 屏幕
        self.current_direction = None  # 记录上一次成功移动的方向 (键值)
        self.last_key = None  # 记录最后按下的方向键 (由外部事件更新)

    @property
    def is_win(self) -> bool:
        """检查是否过关"""
        return self.x == self.exit_x and self.y == self.exit_y

    def move(self, move_keys: dict) -> None:
        """移动 优先转弯 转弯中最后按下的键优先"""
        # 获取所有按下的方向键
        pressed = [got_key for got_key, is_put in move_keys.items() if is_put]
        if not pressed:
            return

        cur = self.current_direction
        # 分为非当前方向 (转弯) 和当前方向
        turns = [k for k in pressed if k != cur] if cur is not None else pressed
        same = [k for k in pressed if k == cur] if cur is not None else []

        # 构建顺序: 转弯组中 最后按下的键排最前 其余保持原有顺序 (UP, LEFT, DOWN, RIGHT)
        if self.last_key is not None and self.last_key in turns:
            # 将 last_key 移到 turns 的最前面
            turns.remove(self.last_key)
            order = [self.last_key] + turns + same
        else:
            order = turns + same

        # 依次尝试移动 一旦成功立即退出
        for key in order:
            dx, dy = self.move_method[key]
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < setting.WIDTH and 0 <= ny < setting.HEIGHT and not self.maze[ny][nx]:
                self.x = nx
                self.y = ny
                self.current_direction = key  # 更新当前方向
                return  # 只移动一步

    def draw(self) -> None:
        """绘制玩家"""
        pygame.draw.rect(
            self.screen,
            setting.PLAYER_COLOR,
            (self.x * setting.CELL_SIZE, self.y * setting.CELL_SIZE, setting.CELL_SIZE, setting.CELL_SIZE)
        )


def generate_maze() -> tuple[list[list[bool]], int, int, list]:
    """
    生成迷宫, 终点在路径最长处
    :return: 迷宫 maze, 出口坐标 exit_x, exit_y, 渲染墙
    """

    def road_yielder(
            _maze: list[list[bool]],
            _start_pos: tuple[int, int] = (0, 0),
    ) -> list[list[bool]]:
        """
        DFS 生成道路
        :param _start_pos: 入口坐标
        :param _maze: 迷宫数据
        :return: 生成道路后的迷宫
        """
        stack: list[tuple[int, int]] = [_start_pos]  # 存放分支节点 用于在分支结束后返回到上一个分支 充分利用空间
        directions: tuple = (
            (-2, 0),
            (2, 0),
            (0, -2),
            (0, 2)
        )
        while stack:  # 如果堆中有生成的单位
            _x, _y = stack[-1]  # 从 stack 里取出上一次生成的单位
            neighbors = []

            # 如果隔了一格的直线方向是墙 标记
            # 这里 dx (dy) 取 2, -2 是因为使用 1 (-1) 会使整个地图变为空地 使用 3 利用率降低
            for _dx, _dy in directions:
                _nx, _ny = _x + _dx, _y + _dy
                if 0 <= _nx < setting.WIDTH and 0 <= _ny < setting.HEIGHT and _maze[_ny][_nx]:
                    neighbors.append((_nx, _ny))

            if neighbors:
                _next_x, _next_y = random.choice(neighbors)
                _maze[(_next_y + _y) // 2][(_next_x + _x) // 2] = False
                _maze[_next_y][_next_x] = False  # 打通这条路
                stack.append((_next_x, _next_y))
            else:
                stack.pop()  # 删除已经无效的点 返回上一个点 继续分支
        return _maze

    # 迷宫二元列表 (初始化 均为墙)
    maze: list[list[bool]] = [[True] * setting.WIDTH for _ in range(setting.HEIGHT)]
    start_x, start_y = 0, 0  # 入口
    maze[start_y][start_x] = False  # 标记
    maze = road_yielder(maze)

    def find_farthest_exit() -> tuple[int, int]:
        """
        BFS 生成终点
        :return: 终点位置
        """
        dist: list[list[int]] = [[-1] * setting.WIDTH for _ in range(setting.HEIGHT)]
        queue: deque[tuple[int, int]] = deque()  # 生成双向列队
        queue.append((0, 0))
        dist[0][0] = 0
        while queue:
            _x, _y = queue.popleft()  #
            for _dx, _dy in move_data.MOVE_DIR:
                _nx, _ny = _x + _dx, _y + _dy
                if (
                        0 <= _nx < setting.WIDTH and 0 <= _ny < setting.HEIGHT
                        and not maze[_ny][_nx] and dist[_ny][_nx] == -1
                ):
                    dist[_ny][_nx] = dist[_y][_x] + 1
                    queue.append((_nx, _ny))
        # 找最大距离的点（若有多个，取第一个）
        max_dist = -1
        farthest = (0, 0)
        for y in range(setting.HEIGHT):
            for x in range(setting.WIDTH):
                if dist[y][x] > max_dist:
                    max_dist = dist[y][x]
                    farthest = (x, y)
        return farthest

    exit_x, exit_y = find_farthest_exit()

    walls: list[tuple[int, int, int, int]] = [  # pygame 的 rect 属性的墙列表 用于渲染
        (x * setting.CELL_SIZE, y * setting.CELL_SIZE, setting.CELL_SIZE, setting.CELL_SIZE)  # 显示的墙
        for y, row in enumerate(maze)
        for x, is_wall in enumerate(row)
        if is_wall
    ]

    return maze, exit_x, exit_y, walls


def main() -> None | typing.NoReturn:
    """游戏主循环"""
    document: str = __doc__.replace('\n\n', '\n') if __doc__ is not None else ""
    ctypes.windll.user32.MessageBoxW(0, document, "注意事项", 0)  # noqa: F821

    def graphic() -> None:
        """画面渲染"""
        screen.blit(visible_surface, (0, 0))
        player.draw()
        pygame.display.update()

    def draw_cell(draw_x: int, draw_y: int) -> None:
        """更新单元格"""
        rect = (draw_x * setting.CELL_SIZE, draw_y * setting.CELL_SIZE, setting.CELL_SIZE, setting.CELL_SIZE)
        if maze[draw_y][draw_x]:
            color = setting.WALL_COLOR
        else:
            color = setting.ROAD_COLOR
        pygame.draw.rect(visible_surface, color, rect)
        if draw_x == 0 and draw_y == 0:  # 绘制起点
            pygame.draw.rect(visible_surface, setting.START_COLOR, rect)
        elif draw_x == exit_x and draw_y == exit_y:  # 更新终点
            pygame.draw.rect(visible_surface, setting.EXIT_COLOR, rect)

    def reveal_area(cx: int = 0, cy: int = 0) -> None:
        """
        点亮走过的地方
        :param cx: 点亮的中心 x 坐标
        :param cy: 点亮的中心 y 坐标
        """
        for dx, dy in move_data.MOVE_DIR:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < setting.WIDTH and 0 <= ny < setting.HEIGHT and not explored[ny][nx]:
                explored[ny][nx] = True  # 修改已探索列表
                draw_cell(nx, ny)

    used_time = 0.0

    def show_message_box() -> None:
        """显示弹窗"""
        nonlocal used_time
        ctypes.windll.user32.MessageBoxW(0, f"used {used_time:.2f} seconds", "pass successfully", 0)  # noqa: F821

    random.seed(setting.SEED)
    screen = pygame.display.set_mode((setting.WINDOW_WIDTH, setting.WINDOW_HEIGHT))
    pygame.display.set_caption(setting.TITLE)

    # 控制移动速度的时钟
    clock = pygame.time.Clock()
    maze, exit_x, exit_y, walls = generate_maze()  # 生成迷宫

    explored = [[False] * setting.WIDTH for _ in range(setting.HEIGHT)]  # 已探索列表, True 为点亮
    visible_surface = pygame.Surface((setting.WINDOW_WIDTH, setting.WINDOW_HEIGHT))
    visible_surface.fill(setting.WALL_COLOR)
    reveal_area()

    player = Player((0, 0), maze, (exit_x, exit_y), screen)
    last_move_time = 0  # 上次移动时间 如果间隔 current_time - ~~ 小于 move_delay 就不允许移动
    win = False
    running = True

    # 方向键
    up_key = move_data[0]
    down_key = move_data[1]
    left_key = move_data[2]
    right_key = move_data[3]

    def event_handle() -> None:
        """事件处理"""
        nonlocal running
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 退出
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # 退出
                    running = False
                if event.key in (up_key, down_key, left_key, right_key):  # 移动
                    player.last_key = event.key

    start_time = time.time()

    while running:
        # 绘制游戏元素
        graphic()
        clock.tick(setting.TICK)

        current_time = pygame.time.get_ticks()
        event_handle()

        # 移动  如果时间间隔不够或胜利不允许移动
        keys = pygame.key.get_pressed()  # 检查按键长按状态
        move_keys = {  # 移动键
            up_key: keys[up_key],
            down_key: keys[down_key],
            left_key: keys[left_key],
            right_key: keys[right_key],
        }
        if current_time - last_move_time > setting.MOVE_DELAY and not win:
            if any(move_keys):
                old_x, old_y = player.x, player.y
                player.move(move_keys)
                if (player.x, player.y) != (old_x, old_y):
                    reveal_area(player.x, player.y)  # 揭示新位置周围
                    last_move_time = current_time  # 设置上次移动时间为当前时间

        # 检查是否到达出口
        if not win and player.is_win:
            win = True
            finish_time = time.time()

            used_time = finish_time - start_time
            # 胜利后揭示全图
            for y in range(setting.HEIGHT):
                for x in range(setting.WIDTH):
                    if not explored[y][x]:
                        explored[y][x] = True
                        draw_cell(x, y)
            graphic()
            threading.Thread(target=show_message_box, daemon=True).start()  # 显示弹窗, daemon 控制窗口随主进程结束而结束
            while running:  # 等待退出
                event_handle()
                clock.tick(setting.TICK)

    pygame.quit()


if __name__ == '__main__':
    main()
