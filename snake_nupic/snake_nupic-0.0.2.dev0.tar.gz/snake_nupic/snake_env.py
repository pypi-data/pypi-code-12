# -*- coding: utf-8 -*-
"""
settings for setup the environment, the snake plays at a playground that divided into grids
"""
# ----------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# Email: asterocean@gmail.com Author: Hui Gao
# ----------------------------------------------------------------------

# the number of grids count from horizon
GRID_X = 10

# the number of grids count from vertical
GRID_Y = 10

# the width of a grid in pixels
GRID_WIDTH = 40

# the size between grids and canvas
GRID_OFFSET = 10

# the sleep time after each move in microseconds
SLEEP_TIME = 300

# the pain that felt by the snake when hit the wall
PAIN_HITWALL = 20

# the pain that felt by the snake when desire not satisfied
PAIN_DESIRE = 5

# the energy felt by the snake when eat food
FOOD_ENERGY = 100

# the possible direction for sname to move
DIRECTIONS = ('Up', 'Right', 'Down', 'Left')

# the score of pain that would kill the snake
SNAKE_PAIN_DIE = 10000

# the score of desire that would kill the snake
SNAKE_DESIRE_DIE = -10000

# the score of desire that would the snake full satisfied
SNAKE_DESIRE_PEAK = 10000

# the sdr format represent the directions
SDR_DIRECTIONS = ((0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,),
                    (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,),
                    (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,),
                    (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,))

