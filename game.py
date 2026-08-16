# -*- encoding: utf-8 -*-
# game.py
"""
**A maze game**\n
* rule: use WASD to move, Escape to exit when you win\n
====\n\n====\n
By *Cozy_wa*\n
Email: ``Cozy_wa_9149U4@outlook.com``\n
"""

from time import time

import pygame
from colorama import Fore, Style

from classes import Player, move_data
from config_analysis import setting
from generator import generate_maze

# Initialize pygame
pygame.init()


def main() -> None:
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
        if any((draw_x > 0, draw_y > 0)) and maze_map[draw_y][draw_x]:
            pygame.draw.rect(visible_surface, setting.road_color, rect)
            if draw_x == exit_x and draw_y == exit_y:  # Update end
                pygame.draw.rect(visible_surface, setting.exit_color, rect)
        elif all((draw_x == 0, draw_y == 0)):  # Draw start
            pygame.draw.rect(visible_surface, setting.start_color, rect)
        dirty_rects.append(rect)

    def reveal_area(cx: int = 0, cy: int = 0) -> None:
        """
        Light the cell which passed
        :param cx: X-coordinate of the lit center
        :param cy: Y-coordinate of the lit center
        """
        for dx, dy in move_data.move_dir.values():
            nx, ny = cx + dx, cy + dy
            if all((0 <= nx < setting.width, 0 <= ny < setting.height, not explored[ny][nx])):
                explored[ny][nx] = True  # Edit explored list
                update_cell(nx, ny)

    def graphic() -> None:
        screen.blit(visible_surface, (0, 0))
        pygame.draw.rect(
            player.screen,
            setting.player_color,
            (player.x * setting.cell_size, player.y * setting.cell_size, setting.cell_size, setting.cell_size)
        )
        if dirty_rects:
            pygame.display.update(dirty_rects)  # Only update the dirty rects
            dirty_rects.clear()
        else:
            pygame.display.flip()

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

    def run() -> None:
        """
        Game run code snippet
        """
        nonlocal last_move_time
        graphic()  # Draw game elements
        clock.tick(setting.tick)
        current_time: int = pygame.time.get_ticks()
        event_handle()

        # Move if the time gap isn’t enough or victory doesn’t allow moving
        keys = pygame.key.get_pressed()  # Check if the button is being held down
        # The pressed state of the movement key
        pressed_move_keys: dict[int, bool] = {key: keys[key] for key in move_data.move_dir}
        got_delay: bool = current_time - last_move_time > setting.move_delay
        if all((got_delay, not win, any(pressed_move_keys))):
            old_pos = (player.x, player.y)
            player.move(
                lambda nx, ny: all(
                    (0 <= nx < setting.width, 0 <= ny < setting.height, maze_map[ny][nx])
                ),
                pressed_move_keys
            )

            if (player.x, player.y) != (old_pos[0], old_pos[1]):
                reveal_area(player.x, player.y)  # Reveal around the new location
                last_move_time = current_time  # Set the last move time to the current time

    def wait() -> None:
        """
        Event loop after victory
        """
        nonlocal win
        # Check if reach end
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
        print(f"Pass successfully\nUsed {Fore.GREEN}{used_time:.3f}s{Style.RESET_ALL}")
        while running:  # Wait for exit
            event_handle()
            clock.tick(setting.wait_tick)

    screen = pygame.display.set_mode((setting.window_width, setting.window_height))
    pygame.display.set_caption(setting.title)

    # Clock that controls movement speed
    clock = pygame.time.Clock()
    maze_map, exit_x, exit_y = generate_maze(setting=setting)

    explored = [[False] * setting.width for _ in range(setting.height)]  # Explored list, True means lit up
    visible_surface = pygame.Surface((setting.window_width, setting.window_height))
    visible_surface.fill(setting.wall_color)

    dirty_rects = []  # Store the cells which needs to update
    reveal_area()

    player = Player((0, 0), (exit_x, exit_y), maze_map, screen)
    # Last move time: if the interval current_time - last_move_time is less than move_delay, moving is not allowed
    last_move_time = 0
    win = False
    running = True

    start_time = time()

    while running:
        run()
        if not win and player.is_win:
            wait()
    pygame.quit()


if __name__ == '__main__':
    main()
