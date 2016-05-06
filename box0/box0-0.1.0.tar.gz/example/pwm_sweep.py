#/bin/python

import box0
import time

dev = box0.usb.open_supported()
pwm1 = dev.pwm(1)
pwm1.speed.current = 1000
pwm1.period = 100
pwm1.width[0] = 0
pwm1.start()

try:
	while True:
		for i in range(1, 50, 5):
			pwm1.width[0] = i
			time.sleep(.1)

		for i in range(50, 1, -5):
			pwm1.width[0] = i
			time.sleep(.1)
except:
	pass

pwm1.stop()

pwm1.close()
dev.close()
