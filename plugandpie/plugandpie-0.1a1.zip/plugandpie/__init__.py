"""A package for ease of access to sensors data on Raspberry Pi

Standard sensor accessors:
- accelerometer
- thermometer
"""
from plugandpie.plugnplay import Proxy

accelerometer = Proxy('accelerometer')
thermometer = Proxy('thermometer')

