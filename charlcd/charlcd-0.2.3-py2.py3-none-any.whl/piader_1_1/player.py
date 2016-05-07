#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable=I0011,W0231

"""Player class"""

__author__ = 'Bartosz Kościów'
import piader_1_1.item as item
import piader_1_1.missile as missile
import piader_1_1.bomb as bomb


class Player(item.Item):
    """Player class"""
    sprite = {
        'left': "&#",
        'right': "#&"
    }
    heading = 'left'
    missile = {
        "current": 0,
        "max": 1
    }

    def __init__(self, x, y, max_x, objects):
        """init player"""
        item.Item.__init__(self, x, y)
        self.max_x = max_x
        self.objects = objects

    def move_right(self):
        """move player right"""
        if self.pos_x > self.max_x - 1:
            return
        item.Item.move_right(self)
        self.heading = "right"

    def move_left(self):
        """move player left"""
        if self.pos_x < 2:
            return
        item.Item.move_left(self)
        self.heading = "left"

    def fire(self):
        """fire a missile"""
        if self.missile['current'] < self.missile['max']:
            self.missile['current'] += 1
            if self.heading == "right":
                self.objects.append(missile.Missile(self.pos_x,
                                                    self.pos_y,
                                                    self))
            else:
                self.objects.append(missile.Missile(self.pos_x + 1,
                                                    self.pos_y,
                                                    self))

    def tick(self):
        """action in tick"""
        pass

    def get_sprite(self):
        """get sprite"""
        return self.sprite[self.heading]

    def event_discard(self):
        """discard player - not implemented"""
        pass

    def can_hit(self):
        """Player can't hit anything"""
        return False

    def is_hit(self, target):
        """Player can be hit"""
        if isinstance(target, bomb.Bomb):
            target_position = target.get_position()
            if target_position[1] == self.pos_y and \
                self.pos_x <= target_position[0] <= self.pos_x + 1:
                return True

        return False
