#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Simple game"""
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
from past.utils import old_div
__author__ = 'Bartosz Kościów'

import random
import time
import piader_1_1.enemy as enemy
import piader_1_1.player as player
import piader_1_1.event_server as event_server
import queue
import piader_1_1.local_key as keyboard


class Piader(object):
    """Piader main class"""
    game_tick = 0.5 #1.0
    objects = []
    score = 0
    game_on = True

    def __init__(self, lcds):
        """init class"""
        if len(lcds) != 1 and len(lcds) != 2:
            raise ValueError("Must have 1 or 2 lcds")

        self.info_lcd = None
        if len(lcds) == 2:
            self.game_lcd = lcds[0]
            self.info_lcd = lcds[1]
        if len(lcds) == 1:
            self.game_lcd = lcds[0]

        self.width = self.game_lcd.get_width()
        self.height = self.game_lcd.get_height()
        if self.width < 6:
            raise ValueError("Width must be larger than 5")
        if self.height < 3:
            raise ValueError("Height must be larger than 2")

        self.player = player.Player(
            (self.width // 2) - 2,
            self.height - 1,
            self.width,
            self.objects
        )
        self.queue = queue.Queue()
        self.event_server = event_server.EventServerThread(self.queue)
        self.local_keyboard = keyboard.Keyboard()
        self.start_game()

    def start_game(self):
        """starts game, add enemy, player and start control server"""
        self.objects.append(enemy.Enemy(2, 0, self.width, self.objects))
        self.objects.append(self.player)
        self.event_server.start()

    def tick(self):
        """game tick"""
        try:
            event = self.queue.get(True, 0.05)
            if event == "player.move.left":
                self.player.move_left()
            if event == "player.move.right":
                self.player.move_right()
            if event == "player.move.fire":
                self.player.fire()

        except queue.Empty:
            pass

        self.game_lcd.buffer_clear()
        for item in self.objects:
            item.tick()
            self.draw(item)

        if self.info_lcd:
            self.info_lcd.write(str(self.score), 0, 0)

        self.game_lcd.flush()

        self.collision_check()

    def collision_check(self):
        """checks for collisions"""
        for source in self.objects:
            if source.can_hit():
                for target in self.objects:
                    if target.is_hit(source):
                        if isinstance(target, player.Player):
                            self.game_over()
                        if isinstance(target, enemy.Enemy):
                            self.enemy_hit(source, target)
                            self.score += 1

    def draw(self, item):
        """draw sprite on screen"""
        (position_x, position_y) = item.get_position()

        if position_y >= self.height or position_y < 0:
            self.objects.remove(item)
            item.event_discard()
            return

        self.game_lcd.write(item.get_sprite(), position_x, position_y)

    def game_over(self):
        """displays game over and stops game"""
        self.game_on = False
        self.game_lcd.buffer_clear()
        if self.info_lcd:
            self.info_lcd.buffer_clear()
        self.game_lcd.write("Game Over", 2, 2)
        self.game_lcd.flush()
        self.event_server.join()

    def enemy_hit(self, source, target):
        """event enemy hit"""
        target.event_discard()
        source.event_discard()
        self.objects.remove(source)
        self.objects.remove(target)
        self.objects.append(
            enemy.Enemy(
                random.randint(1, self.width - 3),
                random.randint(0, self.height - 3),
                self.width,
                self.objects
            )
        )

    def game(self):
        """game loop"""
        try:
            while self.game_on:
                start = time.time()
                self.local_keyboard.read()
                self.tick()
                end = time.time()
                if end - start < self.game_tick:
                    t_delta = end - start
                    time.sleep(max(0, self.game_tick - t_delta))
        finally:
            self.local_keyboard.shutdown()
            self.event_server.join()
