#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable=I0011,W0231

"""Bomb class"""

__author__ = 'Bartosz Kościów'

import piader_1_1.item as item


class Bomb(item.Item):
    """Bomb"""
    def __init__(self, x, y, dmo):
        """init bomb"""
        item.Item.__init__(self, x, y)
        self.sprite = "@"
        self.dmo = dmo

    def tick(self):
        """action in tick - move bomb down"""
        self.move_down()

    def event_discard(self):
        """discard bomb, decrease DMO bomb counter"""
        self.dmo.bombs['current'] -= 1

    def can_hit(self):
        """bomb can hit something"""
        return True

    def is_hit(self, target):
        """bomb cant be hit"""
        return False
