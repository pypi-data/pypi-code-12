#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test script for virtual buffered lcd"""
import sys
sys.path.append("../../")
import RPi.GPIO as GPIO  # NOQA pylint: disable=I0011,F0401
from charlcd import buffered as lcd  # NOQA
from charlcd.drivers.gpio import Gpio  # NOQA
from charlcd.drivers.i2c import I2C  # NOQA pylint: disable=I0011,F0401
from charlcd import virtual_buffered as vlcd  # NOQA

GPIO.setmode(GPIO.BCM)


def test1():
    """demo: 16x2 + 20x4 = 20x6"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)

    vlcd_1 = vlcd.CharLCD(20, 6)
    vlcd_1.add_display(0, 0, lcd_2)
    vlcd_1.add_display(0, 4, lcd_1)
    vlcd_1.init()

    vlcd_1.write('First line')
    vlcd_1.write('Second line', 0, 1)
    vlcd_1.write('Fifth Line', 0, 4)

    vlcd_1.set_xy(4, 2)
    vlcd_1.write('third line')

    vlcd_1.flush()


def test2():
    """demo: 16x2 + 20x4 = 36x4"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)

    vlcd_1 = vlcd.CharLCD(36, 4)

    vlcd_1.add_display(0, 0, lcd_2)
    vlcd_1.add_display(20, 0, lcd_1)
    vlcd_1.init()
    vlcd_1.write('test me 123456789qwertyuiopasdfghjkl12')
    vlcd_1.flush()


def test3():
    """demo: 16x2 + 20x4 = 16x6"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)

    vlcd_1 = vlcd.CharLCD(16, 6)
    vlcd_1.add_display(0, 0, lcd_2, 4, 0)
    vlcd_1.add_display(0, 4, lcd_1)
    vlcd_1.init()

    vlcd_1.write('1234567890123456')
    vlcd_1.set_xy(0, 1)
    vlcd_1.write('2')
    vlcd_1.write('3', 0, 2)
    vlcd_1.write('4', 0, 3)
    vlcd_1.write('5', 0, 4)
    vlcd_1.write('6', 0, 5)

    vlcd_1.flush()


def test4():
    """demo: 16x2 + 20x4 = 10x2"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))
    lcd_2 = lcd.CharLCD(20, 4, Gpio(), 0, 0)

    vlcd_1 = vlcd.CharLCD(10, 2)
    vlcd_1.add_display(0, 0, lcd_1, 11)
    vlcd_1.add_display(5, 0, lcd_2)
    vlcd_1.init()

    vlcd_1.write('1234567890123456')
    vlcd_1.write('-', 0, 0)
    vlcd_1.write('/', 0, 1)
    vlcd_1.write('*', 9, 1)
    vlcd_1.write('#', 9, 0)
    vlcd_1.write('!', 5, 1)
    vlcd_1.write('+', 4, 1)

    vlcd_1.flush()


def test5():
    """demo: 16x2 + 20x4 = 10x2 and 8x2"""
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
    vlcd_1.write('-', 0, 0)
    vlcd_1.write('/', 0, 1)
    vlcd_1.write('*', 9, 1)
    vlcd_1.write('#', 9, 0)
    vlcd_1.write('!', 5, 1)
    vlcd_1.write('+', 4, 1)

    vlcd_2.write("1", 0, 0)
    vlcd_2.write("2", 0, 1)
    vlcd_2.write("3", 7, 0)
    vlcd_2.write("4", 7, 1)

    vlcd_1.flush()
    vlcd_2.flush()


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

    vlcd_1.flush()

    vlcd_2.write('-First blarg1 !')
    vlcd_2.write('-Second blarg2 !', 0, 1)
    vlcd_2.write('-Third blarg3 !', 0, 2)
    vlcd_2.write('-Fourth blarg4 !', 0, 3)

    vlcd_2.flush()


def test7():
    """demo: 16x2 + 20x4 = 10x2"""
    lcd_1 = lcd.CharLCD(16, 2, I2C(0x20, 1))

    vlcd_1 = vlcd.CharLCD(5, 2)
    vlcd_1.add_display(0, 0, lcd_1, 11)
    vlcd_1.init()

    vlcd_1.stream('1234567890qwertyui')

    vlcd_1.flush()

test7()
