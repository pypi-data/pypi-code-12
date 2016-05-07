#!/usr/bin/python
# -*- coding: utf-8 -*-

"""LCD Manager - Remote server to read - demo"""

import time
import sys
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
    lcd2 = buffered.CharLCD(16, 2, I2C(0x20, 1))
    lcd2.init()

    lcd = buffered.CharLCD(20, 4, gp.Gpio())
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    lcd_manager2 = manager.Manager(lcd2)
    disp = display.Display(0.5, True)
    disp.add(lcd_manager, 'one')
    disp.add(lcd_manager2, 'two')
    disp.start()
    disp.start_remote(1301, '0.0.0.0')
    label1 = Label(0, 0)
    lcd_manager.add_widget(label1)

    try:
        while True:
            label1.label = str(time.time())
            time.sleep(1)
    finally:
        print("stoping...")
        disp.join()


demo1()
