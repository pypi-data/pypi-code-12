#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable=I0011,W0231

"""Missile class"""

__author__ = 'Bartosz Kościów'

import piader_1_1.item as item


class Missile(item.Item):
    """Missile"""
    sprite = "|"

    def __init__(self, x, y, player):
        """init bomb"""
        item.Item.__init__(self, x, y)
        self.player = player

    def tick(self):
        """action in tick - move missile up"""
        self.move_up()

    def event_discard(self):
        """discard missile, decrease Player bomb counter"""
        self.player.missile['current'] -= 1

    def can_hit(self):
        """missile can hit something"""
        return True

    def is_hit(self, target):
        """missile cant be hit"""
        return False
