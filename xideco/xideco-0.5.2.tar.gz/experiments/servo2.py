import time

import pigpio

servos = 25  # GPIO number
delay = .6

pi = pigpio.pi()
# pulsewidth can only set between 500-2500
print(pi.get_PWM_frequency(25))
print(pi.get_PWM_range(25))

pi.set_PWM_frequency(25, 800)
pi.set_PWM_range(25, 2500)

print(pi.get_PWM_frequency(25))
print(pi.get_PWM_range(25))
try:
    while True:
        # pi.set_servo_pulsewidth(servos, 1000)  # 0 degree
        # print("Servo {} {} micro pulses".format(str(servos), 500))
        # time.sleep(delay)
        # pi.set_servo_pulsewidth(servos, 0)
        # time.sleep(1)



        pi.set_servo_pulsewidth(servos, 500)  # 0 degree
        # print("Servo {} {} micro pulses".format(str(servos), 500))
        time.sleep(delay)
        pi.set_servo_pulsewidth(servos, 0)
        # time.sleep(.5)

        pi.set_servo_pulsewidth(servos, 2500)  # 0 degree
        # print("Servo {} {} micro pulses".format(str(servos), 1000))
        time.sleep(delay)
        pi.set_servo_pulsewidth(servos, 0)
        # time.sleep(.5)


        # switch all servos off
except KeyboardInterrupt:
    pi.set_servo_pulsewidth(servos, 0)

pi.stop()
