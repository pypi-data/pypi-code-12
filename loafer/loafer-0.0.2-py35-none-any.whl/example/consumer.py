# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4


import asyncio
import random


class RandomIntConsumer(object):

    def __init__(self, *args, **kwargs):
        self._blacklist = []

    async def consume(self):
        selected = random.randint(1, 200)
        while selected in self._blacklist:
            selected = random.randint(1, 200)
        return [selected]

    async def confirm_message(self, message):
        if message not in self._blacklist:
            self._blacklist.append(message)
        return True
