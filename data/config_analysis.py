# -*- encoding: utf-8 -*-
# config_analysis.py
"""
Analysis the config
"""

import json
import os
import typing
from colorama import Fore, Style
from dataclasses import dataclass

from data.aliases import Color

_DEFAULT_CONFIG: dict[str, typing.Any] = {
    "WINDOW": {"WIDTH": 31, "HEIGHT": 19, "TITLE": "Maze"},
    "CELL_SIZE": 15,
    "SEED": None,
    "Tick": 60,
    "WaitTick": 20,
    "MoveDelay": 70,
    "COLOR": {
        "WALL": [0, 0, 0],
        "ROAD": [255, 255, 255],
        "EXIT": [255, 0, 0],
        "PLAYER": [0, 255, 0],
        "START": [0, 0, 255]
    }
}


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
    def window_height(self) -> int:
        return self.height * self.cell_size


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
        wait_tick=config["WaitTick"],
        move_delay=config["MoveDelay"],
        wall_color=tuple(colors["WALL"]),
        road_color=tuple(colors["ROAD"]),
        exit_color=tuple(colors["EXIT"]),
        player_color=tuple(colors["PLAYER"]),
        start_color=tuple(colors["START"])
    )


def load_config(
        config_path: typing.AnyStr = "data/game_config.json",
        check: bool = True,
        debug: bool = False
) -> GameConfig:
    """Load configuration"""
    _CONFIG = _DEFAULT_CONFIG

    _no_cfg_out = f"{Fore.RED}No config file. {Fore.YELLOW}Use default config.{Style.RESET_ALL}"
    _invalid_cfg_out = f"{Fore.RED}Invalid config file. {Fore.YELLOW}Use default config.{Style.RESET_ALL}"

    if os.path.exists(config_path):
        with open(config_path, encoding='utf-8') as config_file:
            try:
                _CONFIG = json.load(config_file)  # If got the configuration, replace it with the one in the file
            except (TypeError, ValueError):
                print(_invalid_cfg_out)
    else:
        print(_no_cfg_out)

    if debug:
        _setting = initial_setup(_DEFAULT_CONFIG)
    else:
        try:
            _setting: GameConfig = initial_setup(_CONFIG)
        except KeyError:
            print(_invalid_cfg_out)
            _setting = initial_setup(_DEFAULT_CONFIG)

    # Check the height and width
    area_warn = (
        f"{Fore.YELLOW}The height and width should be odd numbers:"
        f"{Fore.LIGHTRED_EX}{_setting.height}, {_setting.width}{Style.RESET_ALL}"
    )
    is_height_even = _setting.height % 2 == 0 and _setting.height > 0
    is_width_even = _setting.width % 2 == 0 and _setting.width > 0
    if any((is_height_even, is_width_even)) and check:
        raise ValueError(area_warn)

    return _setting

setting: GameConfig = load_config(debug=True)
