#!/usr/bin/python
# -*- coding: utf-8 -*-

"""LCD Manager - label demo"""

import sys
import time
import RPi.GPIO as GPIO  # pylint: disable=I0011,F0401
sys.path.append("../../")
from charlcd import buffered as buffered  # NOQA
from charlcd.drivers.i2c import I2C  # NOQA
import charlcd.drivers.gpio as gp  # NOQA
from lcdmanager import manager  # NOQA
from lcdmanager.widget.label import Label  # NOQA

GPIO.setmode(GPIO.BCM)


def demo1():
    """basic demo"""
    lcd = buffered.CharLCD(16, 2, I2C(0x20, 1))
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    label1 = Label(0, 0)
    label1.label = "Hello !"
    lcd_manager.add_widget(label1)
    lcd_manager.render()
    lcd_manager.flush()


def demo2():
    """width demo"""
    lcd = buffered.CharLCD(16, 2, I2C(0x20, 1))
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    label1 = Label(0, 0)
    label1.width = 3
    label1.label = "Hello !!!111"
    lcd_manager.add_widget(label1)
    lcd_manager.render()
    lcd_manager.flush()

    time.sleep(2)
    label1.width = 6
    lcd_manager.render()
    lcd_manager.flush()

    time.sleep(2)
    label1.autowidth = True
    lcd_manager.render()
    lcd_manager.flush()


def demo3():
    """multi line 16x2 demo"""
    lcd = buffered.CharLCD(16, 2, I2C(0x20, 1))
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    label1 = Label(1, 0)
    label1.label = ['one', 'two', 'three']
    lcd_manager.add_widget(label1)
    lcd_manager.render()
    lcd_manager.flush()


def demo4():
    """multi line 20x4 demo"""
    lcd = buffered.CharLCD(20, 4, gp.Gpio())
    lcd.init()
    lcd_manager = manager.Manager(lcd)
    label1 = Label(1, 0)
    label1.label = ['one', 'two', 'three']
    lcd_manager.add_widget(label1)
    lcd_manager.render()
    lcd_manager.flush()


demo4()
