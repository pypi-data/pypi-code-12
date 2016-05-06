import box0
import sys

dev = box0.usb.open_supported()
ain0 = dev.ain(0)
ain0.info()
print("byte byte....")
