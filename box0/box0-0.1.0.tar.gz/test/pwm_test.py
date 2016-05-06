import box0
import time

dev = box0.usb.open_supported()
pwm = dev.pwm(0)

speed, period = pwm.calc(1)
print("speed: ", speed)
print("period: ", period)

pwm.set(0, 1)
pwm.start()

for l in pwm.label.values:
	print("label: " + l)

for b in pwm.bitsize.values:
	print("bitsize: " + str(b))

while True:
	time.sleep(.5)

pwm.stop()
pwm.close()
dev.close()
