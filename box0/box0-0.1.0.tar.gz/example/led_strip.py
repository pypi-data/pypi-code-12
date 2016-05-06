import box0
import time

dev = box0.usb.open_supported()
dio0 = dev.dio()

dio0.static_prepare()

def wait():
	time.sleep(.05)

for i in range(8):
	pin = dio0.pin(i)
	pin.output()
	pin.hiz = False

try:
	while True:
		for i in range(8):
			dio0.pin(i).value = True
			wait()

		for i in range(8):
			dio0.pin(i).value = False
			wait()

		for i in range(8):
			dio0.pin(7 - i).value = True
			wait()

		for i in range(8):
			dio0.pin(7 - i).value = False
			wait()

except KeyboardInterrupt:
	pass

dio0.close()
dev.close()
