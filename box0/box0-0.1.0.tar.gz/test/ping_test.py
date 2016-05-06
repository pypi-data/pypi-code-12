import box0
import time

dev = box0.usb.open_supported()

print("ping")
try:
	dev.ping()
	print("pong")
except:
	print("ping failed")

dev.close()
