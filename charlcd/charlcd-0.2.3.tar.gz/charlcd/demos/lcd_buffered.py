#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test script for buffered lcd"""

import sys
sys.path.append("../../")
import RPi.GPIO as GPIO  # NOQA pylint: disable=I0011,F0401
from charlcd import buffered as lcd  # NOQA
from charlcd.drivers.gpio import Gpio  # NOQA
from charlcd.drivers.i2c import I2C  # NOQA

GPIO.setmode(GPIO.BCM)


def test1():
    """demo 20x4 and 16x2"""
    lcd_2 = lcd.CharLCD(20, 4, Gpio())
    lcd_2.init()
    lcd_2.write('-  Blarg !')
    lcd_2.write('-   Grarg !', 0, 1)
    lcd_2.write('-    ALIVE  !!!!', 0, 2)

    lcd_2.flush()

    lcd_2.write('-    ALIVE  !!!!.', 0, 2)
    lcd_2.flush()

    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1), 0, 0)
    lcd_1.init()
    lcd_1.write('-!Second blarg!')
    lcd_1.write("-second line", 0, 1)
    lcd_1.flush()


def test2():
    """demo 40x4"""
    drv = Gpio()
    drv.pins['E2'] = 10
    drv.pins['E'] = 24
    lcd_1 = lcd.CharLCD(40, 4, drv, 0, 0)
    lcd_1.init()
    lcd_1.write('-  Blarg !')
    lcd_1.write('-   Grarg !', 0, 1)
    lcd_1.write('-    ALIVE  !!!!', 0, 2)
    lcd_1.flush()

    lcd_1.write('/* ', 19, 0)
    lcd_1.write('|*|', 19, 1)
    lcd_1.write(' */', 19, 2)

    lcd_1.flush()


def test3():
    """demo 16x2"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1), 0, 0)
    lcd_1.init()
    lcd_1.set_xy(10, 0)
    lcd_1.stream("1234567890qwertyuiopasdfghjkl")
    lcd_1.flush()


test1()
