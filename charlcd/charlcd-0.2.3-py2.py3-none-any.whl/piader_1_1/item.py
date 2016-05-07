#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable=I0011,R0921

"""Item interface"""
from builtins import object
__author__ = 'Bartosz Kościów'


class Item(object):
    """Base class for all elements in game"""
    sprite = "*"

    def __init__(self, x, y):
        """init function"""
        self.pos_x = x
        self.pos_y = y

    def tick(self):
        """tick function"""
        raise NotImplementedError("tick not implemented")

    def get_sprite(self):
        """get sprite"""
        return self.sprite

    def get_position(self):
        """get position"""
        return self.pos_x, self.pos_y

    def event_discard(self):
        """called when object is discarded"""
        raise NotImplementedError("event_discard not implemented")

    def is_hit(self, target):
        """check if object is hit by target"""
        raise NotImplementedError("is_hit not implemented")

    def can_hit(self):
        """object can hit something else"""
        raise NotImplementedError("can_hit not implemented")

    def move_up(self):
        """move object up"""
        self.pos_y -= 1

    def move_down(self):
        """move object down"""
        self.pos_y += 1

    def move_right(self):
        """move object right"""
        self.pos_x += 1

    def move_left(self):
        """move object left"""
        self.pos_x -= 1
