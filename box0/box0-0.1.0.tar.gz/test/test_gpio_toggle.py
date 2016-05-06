import box0
import time

dev = box0.usb.open_supported()

dio0 = dev.dio(0)

dio0.static_prepare()

dio0.output(0)
dio0.low(0)
dio0.hiz(0, dio0.DISABLE)

try:
	while True:
		dio0.toggle(0)
		time.sleep(0.5)
except KeyboardInterrupt:
	print("Bye bye")

dio0.low(0)
dio0.hiz(0, dio0.ENABLE)
dio0.close()

dev.close()
