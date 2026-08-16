v1.0.0
-
- Python 3.12.2
- Use DFS to generate the maze
- Got add to the maze
- The exit always appear at the right down corner

v1.1.0
-
- The wall is black. Before, the road is black
- The generator now is an independent function
- Now use external configuration instead of hard coding
- Add type annotations and comments
- Use `json5` instead of `json`. Allow the config file to use comments

v1.1.1
-
- Python 3.13.14
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

v1.2.0
-
- Players need to light up the maze paths themselves

v1.2.1
-
- Changed the movement method and fixed a bug where cells wouldn't light up in certain situations
- Using pop-ups on Windows
- Changed the docstring and comments to English
- Upload to https://github.com/Cozywa/simple_labyrinth

v1.2.2
-
- Use distance tag to set the exit
- Add `WaitTick` to control the tick while waiting for exit
- Can use `Escape` to exit
- Switch rendering to use an independent graphic nested function

v1.2.3
-
- Now, type, configuration loading, and maze generation are separate scripts
- Reuse terminal output on Windows
- Even heights and widths will cause the script to raise a ValueError
- Use `colorama` to make colored output

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
- Move the heights and widths checks to `config_analysis.py`

v1.2.6
-
- Wrap the contents of the run loop and wait loop into nested functions
- Move the Player class to classes.py
- Change main.py to game.py