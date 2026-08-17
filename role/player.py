# -*- encoding: utf-8 -*-
# player.py

from data.move_dt import move_data
from data.aliases import Pos, MazeMap, Surface
from data.config_analysis import setting


class Player:
    def __init__(
            self,
            start_pos: Pos,
            exit_pos: Pos,
            maze_map: MazeMap,
            screen: Surface,
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
        # The same keys as last time
        sames: list[int] = [
            put_key for put_key in pressed if put_key == current_dir
        ] if current_dir is not None else []

        # Build order: In the turn group, the key pressed last comes first, the rest stay in their original order
        if self.last_key is not None and self.last_key in turns:
            # Move last_key to the very front of turns
            turns.remove(self.last_key)
            order: list[int] = [self.last_key] + turns + sames  # Handling: last key pressed -> turn key -> straight key
        else:
            order = turns + sames

        # Try moving one by one, and exit immediately once successful
        for key in order:
            dx, dy = move_data.move_dir[key]
            nx, ny = self.x + dx, self.y + dy
            if all((0 <= nx < setting.width, 0 <= ny < setting.height)) and self.maze_map[ny][nx]:
                self.x = nx
                self.y = ny
                self.current_direction = key  # Update current direction
                return  # Move just one step
