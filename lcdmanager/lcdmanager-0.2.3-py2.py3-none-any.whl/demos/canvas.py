#!/usr/bin/python
# -*- coding: utf-8 -*-

"""LCD Manager - canvas demo"""

import sys
sys.path.append("../../")
import RPi.GPIO as GPIO  # NOQA pylint: disable=I0011,F0401
from charlcd import buffered as buffered  # NOQA
import charlcd.drivers.gpio as gp  # NOQA
from lcdmanager import manager  # NOQA
from lcdmanager.widget.canvas import Canvas  # NOQA

GPIO.setmode(GPIO.BCM)


def demo1():
    """20x4 demo"""
    lcd = buffered.CharLCD(20, 4, gp.Gpio())
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    canvas1 = Canvas(0, 0, 20, 4)
    canvas1.write('Hi !', 4, 1)
    lcd_manager.add_widget(canvas1)
    lcd_manager.render()
    lcd_manager.flush()

demo1()
