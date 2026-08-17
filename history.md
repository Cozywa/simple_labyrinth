v1.0.0
-
- _Python 3.12.2_
- Use DFS to generate the maze
- Got add to the maze
- The exit always appear at the right down corner
- By [DeepSeek](https://www.deepseek.com)
****
v1.1.0
-
- The wall is black. Before, the road is black
- The generator now is an independent function
- Now use external configuration instead of hard coding
- Add type annotations and comments
- Use `json5` instead of `json`. Allow the config file to use comments

v1.1.1
-
- _Python 3.13.14_
- Use BFS to set the exit
- Use dataclass to load the config
- Changed the move keys to `W` `A` `S` `D`
- Cache background data to boost performance
- Remove logging

v1.1.2
-
- The cell size can be configured
- Use a seed to control map generation
- A victory message will pop up on the terminal
- Changed some names
- Use `Pos` `MazeMap` and  `Color` as type annotations
- Optimized various logics
****
v1.2.0
-
- Players need to light up the maze paths themselves
- It will record the used time

v1.2.1
-
- Changed the movement method and fixed a bug where cells wouldn't light up in certain situations
- Using pop-ups on Windows
- Changed the docstring and comments to English
- Upload to [_GitHub_](https://github.com/Cozywa/simple_labyrinth)

v1.2.2
-
- Use distance tag to set the exit
- Add `WaitTick` to control the tick while waiting for exit
- Can use `Escape` to exit
- Switch rendering to use an independent graphic nested function
- It will handle turning and pressing actions first

v1.2.3
-
- Now, type, configuration loading, and maze generation are separate scripts
- Reuse terminal output on Windows
- Even heights and widths will cause the script to raise a ValueError
- Use `colorama` to make colored output
- Some name of colors changed to the role in the game

v1.2.4
-
- Add `README.md` and `history.md`
- Use `json` instead of `json5`, reduce unnecessary dependence on third-party libraries
- Remove the comments in the config
- Use game_config.json

v1.2.5
-
- The locate of exit is random, no longer the furthest
- Print the usage time with only 3 decimal places
- Move the heights and widths checks to `data/config_analysis.py`

v1.2.6
-
- Wrap the contents of the run loop and wait loop into nested functions
- Move the Player class to classes.py
- Change main.py to game.py
- Optimized various logics
- Add `RealNum` and `Rect` as type annotations
- Change `classes.py` to `aliases.py`
- Use bool `debug` to control config-loading

v1.2.7
-
- Move `aliases.py`, `config_analysis.py` to `data/`
- Now, dataclass `GameConfig` is in `data/config_analysis.py`
- dataclass `MoveData` and var `move_data` are in `data/move_dt.py`
- class `Player` is in `role/player.py`
- The configuration loading is wrapped into a function
- Move `generate.py` to `func/`
- **Walking against the bottom or right boundary can cause the player's expected position coordinates to be invalid, leading to an IndexError due to an out-of-bounds index.**

v1.2.8
-
- Fixed the index error
- Change the default `WaitTick` to 20