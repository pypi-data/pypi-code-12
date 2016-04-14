#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,W0231
"""Driver for LCD. Uses i2c. Chip 8574,
Simpe wiring:
GPIO    PCF8574
GND     A0
GND     A1
GND     A2
GND     GND
+5V     Vcc
SDA     SDA
SCL     SCL

PCF8574     LCD
P4          LCD4 (RS)
P5          LCD6 (E)
P6          E2
P3          LCD14 (DB7)
P2          LCD13 (DB6)
P1          LCD12 (DB5)
P0          LCD11 (DB4)

"""

import time
import smbus  # pylint: disable=I0011,F0401
from charlcd.drivers.base import BaseDriver


class I2C(BaseDriver):
    """I2C LCD driver"""
    def __init__(self, address, port):
        """
        Set address port, pins
        Args:
            address: hex i2c address
            port: bus number
        """
        self.address = address
        self.port = port
        self.mode = 8
        self.pins = {
            'RS': 4,
            'E': 5,
            'E2': None,  # 6
            'DB4': 0,
            'DB5': 1,
            'DB6': 2,
            'DB7': 3
        }
        self.bus = smbus.SMBus(port)
        self.char_buffer = None
        self.initialized = False

    def init(self):
        """recalculate pins to values"""
        if self.initialized:
            return
        pins = {}
        for k in self.pins:
            if self.pins[k] is not None:
                pins[k] = int(pow(2, self.pins[k]))
        self.pins = pins

        self.initialized = True

    def cmd(self, char, enable=0):
        """
        Send command to lcd
        Args:
            char: hex command to write
        """
        if self.mode == 8:
            self.prepare_send(char & 0x0F, enable)
        else:
            self.prepare_send(char >> 4, enable)
            self.prepare_send(char & 0x0F, enable)

    def shutdown(self):
        """shutdown routine"""
        pass

    def prepare_send(self, char, enable=0):
        """
        Prepares data for send and call send
            char: char to write
            enable: line to use
        """
        self.char_buffer = char
        self.send(enable)

    def send(self, enable=0):
        """
        Send enable signal
        Args:
            enable: line to use
        """
        if enable == 0:
            pin = self.pins['E']
        elif enable == 1:
            pin = self.pins['E2']

        if pin is None:
            raise IndexError("Wrong enable index")

        self.write(self.char_buffer | pin)
        time.sleep(0.005)
        self.write(self.char_buffer & (0xFF - pin))

    def write(self, byte, enable=0):
        """
        Write data to bus
        Args:
            byte: hex to write to i2c bus
        """
        self.bus.write_byte(self.address, byte)

    def char(self, char, enable=0):
        """
        Send char
        Args:
            char: char to swrite
            enable: enable line
        """
        char = ord(char)
        if self.mode == 8:
            self.prepare_send(self.pins['RS'] | (char & 0x0F), enable)
        else:
            self.prepare_send(self.pins['RS'] | (char >> 4), enable)
            self.prepare_send(self.pins['RS'] | (char & 0x0F), enable)

    def set_mode(self, mode):
        """
        Set working mode (4/8-bit)
        Args:
            mode: mode to set
        """
        self.mode = mode
