#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,W0231
"""Driver for lcd. Uses GPIO outputs
Examples:
l = lcd.CharLCD(20, 4, Gpio())

g = Gpio()
g.pins = {
    'RS': 24,
    'E': 17,
    'E2': None,
    'DB4': 27,
    'DB5': 25,
    'DB6': 23,
    'DB7': 22
}
l = lcd.CharLCD(20, 4, g)
"""

import RPi.GPIO as GPIO  # pylint: disable=I0011,F0401
import time
from charlcd.drivers.base import BaseDriver


class Gpio(BaseDriver):
    """Gpio LCD driver"""
    def __init__(self):
        """pins in 4bit mode"""
        self.pins = {
            'RS': 25,  # 0 ->instruction, 1->data
            'E': 24,
            'E2': None,
            'DB4': 22,
            'DB5': 23,
            'DB6': 27,
            'DB7': 17
        }
        self.data_pins = [
            'DB4',
            'DB5',
            'DB6',
            'DB7'
        ]
        self.mode = 8
        self.initialized = False

    def init(self):
        """Set gpio pins"""
        if self.initialized:
            return
        for pin in self.pins:
            if self.pins[pin] is not None:
                GPIO.setup(self.pins[pin], GPIO.OUT)
                GPIO.output(self.pins[pin], 0)

        self.initialized = True

    def cmd(self, char, enable=0):
        """Write output as command. Sets RS to 0
        Args:
            char: hex to write
        """
        GPIO.output(self.pins['RS'], 0)
        self.write(char, enable)

    def shutdown(self):
        """Clean GPIO pins"""
        GPIO.cleanup()

    def send(self, enable=0):
        """Send E signal"""
        if enable == 0:
            pin = self.pins['E']
        elif enable == 1:
            pin = self.pins['E2']

        if pin is None:
            raise IndexError("Wrong enable index")

        GPIO.output(pin, 1)
        time.sleep(0.005)
        GPIO.output(pin, 0)

    def _write8(self, char, enable=0):
        """Write 8 bits"""
        self._write(char)
        self.send(enable)

    def _write4(self, char, enable=0):
        """Prepare and write 4/4 bits"""
        data = (char >> 4)
        self._write(data)
        self.send(enable)

        data = (char & 0x0F)
        self._write(data)
        self.send(enable)

    def _write(self, data):
        """Write to gpio"""
        for i in self.data_pins:
            value = data & 0x01
            GPIO.output(self.pins[i], value)
            data >>= 1

    def write(self, char, enable=0):
        """Write char to lcd
        Args:
            char: hex char to write
        """
        if self.mode == 4:
            self._write4(char, enable)
        else:
            self._write8(char, enable)

    def char(self, char, enable=0):
        """Write char to lcd
        Args:
            char: char to write
        """
        GPIO.output(self.pins['RS'], 1)
        self.write(ord(char), enable)

    def set_mode(self, mode):
        """Set lcd mode
        Args:
            mode: 4 | 8 bit mode
        """
        self.mode = mode
