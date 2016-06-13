"""A package for ease of access to sensors data on Raspberry Pi

Standard sensor accessors:
- accelerometer
- thermometer
"""
from plugandpie.device.Device import Sensor
from plugandpie.device.Proxy import Proxy
from plugandpie.discovery import plug

Proxy.RESOLVE = plug

accelerometer = Proxy(Sensor.ACCELEROMETER)
thermometer = Proxy(Sensor.THERMOMETER)

