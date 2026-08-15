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

from time import time
import typing
from colorama import Fore,  Style

import pygame

from generator import generate_maze
from classes import Pos, MazeMap, MoveData
from config_analysis import setting

# Initialize pygame
pygame.init()

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

# Check the height and width
area_warn = (
    f"{Fore.YELLOW}The height and width should be odd numbers:"
    f"{Fore.LIGHTRED_EX}{setting.height}, {setting.width}{Style.RESET_ALL}"
)
is_height_even = setting.height % 2 == 0 and setting.height > 0
is_width_even = setting.width % 2 == 0 and setting.width > 0
if any((is_height_even, is_width_even)):
    raise ValueError(area_warn)


class Player:
    def __init__(
            self,
            start_pos: Pos,
            exit_pos: Pos,
            maze: MazeMap,
            screen
    ) -> None:
        """
        :param start_pos: Player's starting coordinates
        :param exit_pos: The location of exit
        :param maze: The data of maze
        :param screen: The screen (pygame)
        """
        self.x, self.y = start_pos
        self.exit_x, self.exit_y = exit_pos
        self.maze: MazeMap = maze

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


def main() -> None | typing.NoReturn:
    # Handle the original script document
    document: str = __doc__.replace('\n\n', '\n') if __doc__ is not None else ""
    print("Notes:\n", document)

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
        dirty_rects.append(rect)

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

    def graphic() -> None:
        screen.blit(visible_surface, (0, 0))
        player.draw()
        if dirty_rects:
            pygame.display.update(dirty_rects)  # Only update the dirty rects
            dirty_rects.clear()
        else:
            pygame.display.flip()

    screen = pygame.display.set_mode((setting.window_width, setting.window_height))
    pygame.display.set_caption(setting.title)

    # Clock that controls movement speed
    clock = pygame.time.Clock()
    maze, exit_x, exit_y = generate_maze(setting=setting)

    explored = [[False] * setting.width for _ in range(setting.height)]  # Explored list, True means lit up
    visible_surface = pygame.Surface((setting.window_width, setting.window_height))
    visible_surface.fill(setting.wall_color)

    dirty_rects = []  # Store the cells which needs to update
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

    start_time = time()

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
                old_pos = (player.x, player.y)
                player.move(move_keys)
                if (player.x, player.y) != (old_pos[0], old_pos[1]):
                    reveal_area(player.x, player.y)  # Reveal around the new location
                    last_move_time = current_time  # Set the last move time to the current time

        # Check if reach end
        if not win and player.is_win:
            win = True
            finish_time = time()

            used_time = finish_time - start_time
            # Reveal the full map after victory
            for y in range(setting.height):
                for x in range(setting.width):
                    if not explored[y][x]:
                        explored[y][x] = True
                        update_cell(x, y)
            graphic()
            print("Pass successfully\n", f"Used {used_time}s")
            while running:  # Wait for exit
                event_handle()
                clock.tick(setting.wait_tick)

    pygame.quit()


if __name__ == '__main__':
    main()
