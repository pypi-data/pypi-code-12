#!/usr/bin/python
# -*- coding: utf-8 -*-
"""test script for virtual direct lcd"""
import sys
sys.path.append("../../")
import RPi.GPIO as GPIO  # NOQA pylint: disable=I0011,F0401
from charlcd import direct as lcd  # NOQA
from charlcd.drivers.gpio import Gpio  # NOQA
from charlcd.drivers.i2c import I2C  # NOQA pylint: disable=I0011,F0401
from charlcd import virtual_direct as vlcd  # NOQA

GPIO.setmode(GPIO.BCM)


def test1():
    """demo: 16x2 + 20x4 = 20x6 top, down"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)
    lcd_1.init()
    lcd_2.init()

    vlcd_1 = vlcd.CharLCD(20, 6)
    vlcd_1.add_display(0, 0, lcd_2)
    vlcd_1.add_display(2, 4, lcd_1)

    vlcd_1.write('test me 123456789qwertyuiop')

    vlcd_1.set_xy(2, 0)
    vlcd_1.write('1')
    vlcd_1.write('2', 2, 1)
    vlcd_1.write('3', 2, 2)
    vlcd_1.set_xy(2, 3)
    vlcd_1.write('4')
    vlcd_1.write('5', 2, 4)
    vlcd_1.write('6', 2, 5)

    vlcd_1.set_xy(3, 4)
    vlcd_1.write('-Second blarg !')
    vlcd_1.set_xy(4, 5)
    vlcd_1.write("-second line")

    vlcd_1.set_xy(11, 3)
    vlcd_1.stream("two liner and screener")


def test2():
    """demo: 16x2 + 20x4 = 36x4 left, right"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)
    lcd_1.init()
    lcd_2.init()
    vlcd_1 = vlcd.CharLCD(36, 4)
    vlcd_1.add_display(0, 0, lcd_2)
    vlcd_1.add_display(20, 0, lcd_1)
    vlcd_1.write('test me 123456789qwertyuiopasdfghjkl12')


def test3():
    """demo: 16x2 + 20x4 = 16x6 (offset)"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)
    lcd_1.init()
    lcd_2.init()

    vlcd_1 = vlcd.CharLCD(16, 6)
    vlcd_1.add_display(0, 0, lcd_2, 4, 0)
    vlcd_1.add_display(0, 4, lcd_1)

    vlcd_1.set_xy(0, 0)
    vlcd_1.write('1234567890123456')
    vlcd_1.set_xy(0, 1)
    vlcd_1.write('2')
    vlcd_1.set_xy(0, 2)
    vlcd_1.write('3')
    vlcd_1.set_xy(0, 3)
    vlcd_1.write('4')
    vlcd_1.set_xy(0, 4)
    vlcd_1.write('5')
    vlcd_1.write('6', 0, 5)


def test4():
    """demo: 16x2 + 20x4 = 10x2 - offset left right """
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)
    lcd_1.init()
    lcd_2.init()

    vlcd_1 = vlcd.CharLCD(10, 2)
    vlcd_1.add_display(0, 0, lcd_1, 11)
    vlcd_1.add_display(5, 0, lcd_2)

    vlcd_1.write('1234567890123456')
    vlcd_1.write('/', 0, 1)
    vlcd_1.write('*', 9, 1)
    vlcd_1.write('-', 0, 0)
    vlcd_1.write('#', 9, 0)

    vlcd_1.set_xy(5, 1)
    vlcd_1.write('!')

    vlcd_1.set_xy(4, 1)
    vlcd_1.write('+')


def test5():
    """demo: 16x2 + 20x4 = 10x2 + 8x2 - offset left right """
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)

    vlcd_1 = vlcd.CharLCD(10, 2)
    vlcd_1.add_display(0, 0, lcd_1, 11)
    vlcd_1.add_display(5, 0, lcd_2)
    vlcd_1.init()

    vlcd_2 = vlcd.CharLCD(8, 2)
    vlcd_2.add_display(0, 0, lcd_1)
    vlcd_2.init()

    vlcd_1.write('1234567890123456')

    vlcd_1.write('/', 0, 1)
    vlcd_1.set_xy(9, 1)
    vlcd_1.write('*')
    vlcd_1.write('-', 0, 0)
    vlcd_1.set_xy(9, 0)
    vlcd_1.write('#')
    vlcd_1.write('!', 5, 1)
    vlcd_1.write('+', 4, 1)

    vlcd_2.set_xy(0, 0)
    vlcd_2.write('#')
    vlcd_2.write('#', 7, 0)
    vlcd_2.write('#', 7, 1)
    vlcd_2.write('#', 0, 1)


def test6():
    """demo: 40x4 = 20x4 + 20x4"""
    drv = I2C(0x3a, 1)
    drv.pins['E2'] = 6
    lcd_1 = lcd.CharLCD(40, 4, drv, 0, 0)
    vlcd_1 = vlcd.CharLCD(20, 4)
    vlcd_1.add_display(0, 0, lcd_1)

    vlcd_2 = vlcd.CharLCD(20, 4)
    vlcd_2.add_display(0, 0, lcd_1, 20)

    vlcd_1.init()
    vlcd_2.init()

    vlcd_1.write('-First blarg1 !')
    vlcd_1.write('-Second blarg2 !', 0, 1)
    vlcd_1.write('-Third blarg3 !', 0, 2)
    vlcd_1.write('-Fourth blarg4 !', 0, 3)

    vlcd_2.write('-First blarg1 !')
    vlcd_2.write('-Second blarg2 !', 0, 1)
    vlcd_2.write('-Third blarg3 !', 0, 2)
    vlcd_2.write('-Fourth blarg4 !', 0, 3)
    vlcd_1.set_xy(15, 2)
    vlcd_1.stream('1234567890qwertyuiopasdfghjkl')

test6()
