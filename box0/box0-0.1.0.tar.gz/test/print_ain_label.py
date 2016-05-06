import box0
import sys

dev = box0.usb.open_supported()
ain0 = dev.ain(0)

i = 0
for l in ain0.label.values:
	print(str(i) + ": " + l)
	i += 1

dev.close()
