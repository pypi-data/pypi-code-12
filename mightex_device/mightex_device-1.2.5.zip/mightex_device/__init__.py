'''
This Python package (mightex_device) creates classes named
MightexDevice, MightexDevices, and MightexStage, which contain an instance
of serial_device2.SerialDevice and adds methods to it to interface to
Mightex LED controllers.
'''
from mightex_device import MightexDevice, MightexDevices, MightexError, find_mightex_device_ports, find_mightex_device_port, __version__
