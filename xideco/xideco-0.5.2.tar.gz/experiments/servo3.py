import pigpio
import time

servos = 25  # GPIO number
# delay = .7

pi = pigpio.pi()
pi.set_mode(25, pigpio.OUTPUT)

try:

    while True:
       pi.write(25, 1)
       time.sleep(0.0015)
       pi.write(25, 0)
       time.sleep(0.0185)
except KeyboardInterrupt:
    pi.set_servo_pulsewidth(servos, 0)

pi.stop()
