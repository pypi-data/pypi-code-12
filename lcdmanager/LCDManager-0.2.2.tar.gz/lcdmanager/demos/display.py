#!/usr/bin/python
# -*- coding: utf-8 -*-

"""LCD Manager - Display demo"""

import sys
import time
import RPi.GPIO as GPIO  # pylint: disable=I0011,F0401
sys.path.append("../../")
from charlcd import buffered as buffered  # NOQA
from charlcd.drivers.i2c import I2C  # NOQA
import charlcd.drivers.gpio as gp  # NOQA
from lcdmanager import manager  # NOQA
from lcdmanager.widget.label import Label  # NOQA
from lcdmanager import display  # NOQA

GPIO.setmode(GPIO.BCM)


def demo1():
    """basic demo"""
    lcd = buffered.CharLCD(20, 4, gp.Gpio())
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    disp = display.Display(0.5, True)
    disp.add(lcd_manager, 'one')
    disp.start()

    label1 = Label(0, 0)
    label1.label = "This"
    lcd_manager.add_widget(label1)
    time.sleep(1)
    label1.label = " is "
    time.sleep(1)
    label1.label = "spartaa !"
    time.sleep(2)
    disp.join()


def demo2():
    """basic demo"""
    lcd = buffered.CharLCD(16, 2, I2C(0x20, 1))
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    disp = display.Display(0.5, True)
    disp.add(lcd_manager, 'one')
    disp.start()

    label1 = Label(0, 0)
    label1.label = "This"
    lcd_manager.add_widget(label1)
    time.sleep(1)
    label1.label = " is "
    time.sleep(1)
    label1.label = "spartaa !"
    time.sleep(2)
    disp.join()

demo2()
