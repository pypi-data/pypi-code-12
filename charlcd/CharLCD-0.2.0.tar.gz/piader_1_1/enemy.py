#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable=I0011,W0231

"""Enemy class"""

__author__ = 'Bartosz Kościów'
import random
import piader_1_1.item as item
import piader_1_1.bomb as bomb
import piader_1_1.missile as missile


class Enemy(item.Item):
    """DMO - defined moving object"""
    bombs = {
        "current": 0,
        "max": 1,
        "chance": 100
    }
    sprite = "<*>"

    def __init__(self, x, y, max_x, objects):
        """init enemy"""
        item.Item.__init__(self, x, y)
        self.max_x = max_x
        self.objects = objects

    def tick(self):
        """action in tick"""
        if self.bombs['max'] > self.bombs['current'] and \
                        random.randint(1, 100) < self.bombs['chance']:
            self.bombs['current'] += 1
            self.objects.append(bomb.Bomb(self.pos_x + 1, self.pos_y, self))

        direction = []
        if self.pos_x > 2:
            direction.append(-1)
        if self.pos_x < self.max_x - len(self.sprite) - 1:
            direction.append(1)
        self.pos_x += random.choice(direction)

    def event_discard(self):
        """discard enemy - we are discarding enemy elsewhere"""
        pass

    def can_hit(self):
        """enemy can't hit anything"""
        return False

    def is_hit(self, target):
        """enemy can be hit"""
        if isinstance(target, missile.Missile):
            target_position = target.get_position()
            if target_position[1] == self.pos_y and \
                self.pos_x <= target_position[0] <= self.pos_x + 2:
                return True

        return False
