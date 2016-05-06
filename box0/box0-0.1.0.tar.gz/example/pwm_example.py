import box0
import time

dev = box0.usb.open_supported()
pwm0 = dev.pwm()

pwm0.speed.current = 1000
pwm0.period = 250
pwm0.width[0] = 100
# same as 4Hz  40% duty cycle

pwm0.start()

try:
	while True:
		time.sleep(0.1)
except KeyboardInterrupt:
	pass

pwm0.stop()
pwm0.close()
dev.close()
