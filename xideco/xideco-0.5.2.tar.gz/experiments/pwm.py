import pigpio
import time

pi = pigpio.pi()

pi.set_mode(4, pigpio.OUTPUT)

print(pi.get_PWM_range(4))
print(pi.get_PWM_real_range(4))


# pi.write(4,1)
# time.sleep(2)
# pi.write(4,0)
# time.sleep(1)

pi.set_PWM_dutycycle(4, 20) # PWM 3/4 on

time.sleep(3)
pi.stop()