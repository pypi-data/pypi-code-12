#!/usr/bin/python
# -*- coding: utf-8 -*-

"""LCD Manager - pane demo"""


import sys
sys.path.append("../../")
import RPi.GPIO as GPIO  # NOQA pylint: disable=I0011,F0401
from charlcd import buffered as buffered  # NOQA
import charlcd.drivers.gpio as gp  # NOQA
from lcdmanager import manager  # NOQA
from lcdmanager.widget.label import Label  # NOQA
from lcdmanager.widget.pane import Pane  # NOQA

GPIO.setmode(GPIO.BCM)


def demo1():
    """basic demo"""
    lcd = buffered.CharLCD(20, 4, gp.Gpio())
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    label1 = Label(0, 0)
    label1.label = "1 - Hello !"
    label2 = Label(1, 2)
    label2.label = "3 - Meow !"
    label3 = Label(1, 1)
    label3.label = "2 - Woof !"

    pane1 = Pane(1, 0)
    pane1.add_widget(label1)
    pane1.add_widget(label2)
    pane1.add_widget(label3)
    lcd_manager.add_widget(pane1)
    lcd_manager.render()
    lcd_manager.flush()

demo1()
