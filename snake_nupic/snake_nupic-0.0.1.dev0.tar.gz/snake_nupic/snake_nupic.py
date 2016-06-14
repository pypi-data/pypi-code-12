# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# Email: asterocean@gmail.com Author: Hui Gao
# ----------------------------------------------------------------------

try:
    # for Python2
    from Tkinter import *  ## notice capitalized T in Tkinter
except ImportError:
    # for Python3
    from tkinter import *  ## notice here too
import tkMessageBox, sys
from random import choice
from snake_env import *
from snake_brain import *

class Grid(object):
    def __init__(self, master=None, grid_x=GRID_X, grid_y=GRID_Y, grid_width=GRID_WIDTH, offset=GRID_OFFSET):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid_width = grid_width
        self.width = self.grid_x * self.grid_width
        self.height = (self.grid_y + 1) * self.grid_width

        self.offset = offset

        self.bg = "#EBEBEB"
        self.canvas = Canvas(master, width=self.width + 2 * self.offset, height=self.height + 2 * self.offset,
                             bg=self.bg)
        self.canvas.pack()
        self.grid_list()

    def draw(self, pos, color, ):
        x = pos[0] * self.grid_width + self.offset
        y = pos[1] * self.grid_width + self.offset
        self.canvas.create_rectangle(x, y, x + self.grid_width, y + self.grid_width, fill=color, outline=self.bg)

    def grid_list(self):
        grid_list = []
        for y in range(0, self.grid_y):
            for x in range(0, self.grid_x):
                grid_list.append((x, y))
        self.grid_list = grid_list


class Food(object):
    def __init__(self, Grid):
        self.grid = Grid
        self.color = "#23D978"
        self.pos = (0, 0)

    def set_pos(self, pos):
        self.pos = pos

    def display(self):
        self.grid.draw(self.pos, self.color)


class Snake(object):
    def __init__(self, Grid):
        self.grid = Grid
        self.body = [(0, 2), (0, 1), (0, 0)]
        self.direction = "Right"
        self.status = ['run', 'stop']
        self.speed = SLEEP_TIME
        self.color = ("#3366FF","#FF3366","#33FF66","#002EB8","#6633FF","#CC33FF","#FF33CC","#FF6633","#FFCC33","#CCFF33","#66FF33","#33FFCC","#33CCFF","#003DF5","#F5B800","#B88A00")
        self.score = 0
        # pain
        self.pain = 0
        # desire
        self.desire = 100
        self.die = False
        self.brain = Snake_Brain()

    def change_direction(self, direction):
        self.direction = direction

    def display(self):
        i = 0
        colorlen = len(self.color)
        for (x, y) in self.body:
            self.grid.draw((x, y), self.color[i % colorlen])
            i+=1

    #@property
    def move(self, direction):
        if not direction:
            direction = self.direction
            self.desire -= 1
            if self.desire < SNAKE_DESIRE_DIE:
                self.die = True
            elif self.desire < 0:
                self.pain += PAIN_DESIRE
                if self.pain > SNAKE_PAIN_DIE:
                    self.die = True
        head = self.body[0]
        if direction == 'Up':
            new = (head[0], head[1] - 1)
        elif direction == 'Down':
            new = (head[0], head[1] + 1)
        elif direction == 'Left':
            new = (head[0] - 1, head[1])
        else:
            new = (head[0] + 1, head[1])
        return new

    def struggle(self):
        # 蛇挣扎改变方向
        directions = list(DIRECTIONS)
        while 1:
            if not directions:
                self.die = True
                break
            direction = choice(directions)
            newcell = self.move(direction)
            if newcell in self.body:
                directions.remove(direction)
            else:
                self.direction = direction
                break


class SnakeGame(Frame):
    def __init__(self, master=None, *args, **kwargs):
        Frame.__init__(self, master)
        self.master = master
        self.grid = Grid(master=master, *args, **kwargs)
        self.snake = Snake(self.grid)
        self.snake.display()
        self.food = Food(self.grid)
        self.setfood()
        self.bind_all("<KeyRelease>", self.key_release)
        self.steps = 0
        self.point_score = self.grid.canvas.create_text(GRID_WIDTH*GRID_X/2 + GRID_OFFSET, GRID_WIDTH*(GRID_Y+1) + GRID_OFFSET, fill='Blue', text=self.getinfo())

    def getinfo(self):
        return 'Steps: %d, Scores: %d, Pain: %d, Hungary: %d' % (self.steps, self.snake.score, self.snake.pain, self.snake.desire)

    def availableGRID(self):
        return [i for i in self.grid.grid_list if i not in self.snake.body]

    def setfood(self):
        availableGRID = self.availableGRID()
        if not availableGRID:
            return False
        else:
            self.food.set_pos(choice(availableGRID))
            self.food.display()
            return True

    def checkmove(self, new):
        if self.food.pos == new:
            # 吃到食物
            self.snake.desire += FOOD_ENERGY
            if self.snake.desire > SNAKE_DESIRE_PEAK:
                self.snake.desire = SNAKE_DESIRE_PEAK
            self.snake.score += 1
            #self.grid.draw(new, self.snake.color)
            # 若蛇增长需注释以下内容
            pop = self.snake.body.pop()
            self.grid.draw(pop, self.grid.bg)
            self.setfood()
        elif new in self.availableGRID():
            # 正常移动
            pop = self.snake.body.pop()
            self.grid.draw(pop, self.grid.bg)
        else:
            # 撞墙
            self.snake.pain += PAIN_HITWALL
            if self.snake.pain > SNAKE_PAIN_DIE:
                self.snake.die = True
            return False
        assert isinstance(new, TupleType)
        self.snake.body.insert(0, new)
        self.snake.display()
        return True

    def run(self):
        if not self.snake.status[0] == 'stop':
            new = self.snake.move(None)
            if not self.checkmove(new):
                self.snake.struggle()
                if self.snake.die == True:
                    self.report()
            self.steps += 1
            self.grid.canvas.itemconfigure(self.point_score,text=self.getinfo())
            self.snake.brain.runNetwork(self)
        self.after(self.snake.speed, self.run)

    def report(self):
        message = tkMessageBox.showinfo("Game info",
            "Score: %d, Pain: %d, Desire: %d" % (self.snake.score, self.snake.pain, self.snake.desire))
        if message == 'ok':
            sys.exit()

    def getvisionsdr(self):
        sdrlist = [ 1 if i in self.snake.body or i == self.food.pos else 0 for i in self.grid.grid_list]
        return sdrlist

    def key_release(self, event):
        key = event.keysym
        key_dict = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if key_dict.has_key(key) and not key == key_dict[self.snake.direction]:
            self.snake.change_direction(key)
        elif key == 'p':
            self.snake.status.reverse()

if __name__ == '__main__':
    root = Tk()
    snakegame = SnakeGame(root)
    snakegame.run()
    snakegame.mainloop()
