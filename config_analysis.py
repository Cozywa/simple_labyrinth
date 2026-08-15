# -*- encoding: utf-8 -*-
# config_analysis.py
"""
Analysis the config
"""

import typing
import os
from colorama import Fore, Style
import json

from classes import GameConfig, Color

_no_cfg_out = f"{Fore.RED}No config file. {Fore.YELLOW}Use default config.{Style.RESET_ALL}"
_invalid_cfg_out = f"{Fore.RED}Invalid config file. {Fore.YELLOW}Use default config.{Style.RESET_ALL}"

_DEFAULT_CONFIG: dict[str, typing.Any] = {
    "WINDOW": {"WIDTH": 41, "HEIGHT": 35, "TITLE": "Maze"},
    "CELL_SIZE": 15,
    "SEED": None,
    "Tick": 60,
    "WaitTick": 10,
    "MoveDelay": 70,
    "COLOR": {
        "WALL": [0, 0, 0],
        "ROAD": [255, 255, 255],
        "EXIT": [255, 0, 0],
        "PLAYER": [0, 255, 0],
        "START": [0, 0, 255]
    }
}
_CONFIG = _DEFAULT_CONFIG


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


# Load configuration
config_path = os.path.abspath("game_config.json")
if os.path.exists(config_path):
    with open(config_path, encoding='utf-8') as config_file:
        try:
            _CONFIG = json.load(config_file)  # If got the configuration, replace it with the one in the file
        except (TypeError, ValueError):
            print(_invalid_cfg_out)
else:
    print(_no_cfg_out)

try:
    setting: GameConfig = initial_setup(_CONFIG)
except KeyError:
    print(_invalid_cfg_out)
    setting = initial_setup(_DEFAULT_CONFIG)
