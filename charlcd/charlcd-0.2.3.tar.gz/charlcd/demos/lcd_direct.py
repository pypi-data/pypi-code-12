#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test script for direct lcd input"""
import sys
sys.path.append("../../")
import RPi.GPIO as GPIO  # NOQA pylint: disable=I0011,F0401
from charlcd.drivers.gpio import Gpio  # NOQA
from charlcd import direct as lcd  # NOQA
from charlcd.drivers.i2c import I2C  # NOQA pylint: disable=I0011,F0401

GPIO.setmode(GPIO.BCM)


def test1():
    """demo 16x2 by i2c and 20x4 by gpio"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_1.init()
    lcd_1.write('-Second blarg !')
    lcd_1.set_xy(0, 1)
    lcd_1.write("-second line")

    lcd_2 = lcd.CharLCD(20, 4, Gpio())
    lcd_2.init()
    lcd_2.write('-  Blarg !')
    lcd_2.write('-   Grarg !', 0, 1)
    lcd_2.set_xy(0, 2)
    lcd_2.write('-    ALIVE !!!!')


def test2():
    """demo - 20x4 by gpio"""
    lcd_2 = lcd.CharLCD(20, 4, Gpio())
    lcd_2.init()
    lcd_2.write('-  Blarg !')
    lcd_2.write('-   Grarg !', 0, 1)
    lcd_2.set_xy(0, 2)
    lcd_2.write('-    ALIVE !!!!')
    lcd_2.stream('1234567890qwertyuiopasdfghjkl')


def test3():
    """demo 3 - lcd 40x4 by gpio"""
    drv = I2C(0x3a, 1)
    drv.pins['E2'] = 6
    lcd_1 = lcd.CharLCD(40, 4, drv, 0, 0)
    lcd_1.init()
    lcd_1.write('-First blarg1 !')
    lcd_1.write('-Second blarg2 !', 0, 1)
    lcd_1.write('-Third blarg3 !', 0, 2)
    lcd_1.write('-Fourth blarg4 !', 0, 3)
    lcd_1.write('12345678901234567890', 15, 1)
    lcd_1.stream('1234567890qwertyuiopasdfghjkl')


def test4():
    """demo 4 - lcd 40x4 by i2c"""
    drv = I2C(0x3a, 1)
    drv.pins['E2'] = 6
    lcd_1 = lcd.CharLCD(40, 4, drv, 0, 0)
    lcd_1.init()
    lcd_1.write('-First blarg1 !')
    lcd_1.write('-Second blarg2 !', 0, 1)
    lcd_1.write('-Third blarg3 !', 0, 2)
    lcd_1.write('-Fourth blarg4 !', 0, 3)

test3()
