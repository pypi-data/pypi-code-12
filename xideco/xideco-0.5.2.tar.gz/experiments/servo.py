import time  # import the time library

import pigpio  # import the GPIO library

pin = 25

# establish 2 pulse definitions to create a 1k hz tone
# the first entry sets pin 18 high for a duration of 1000 microseconds
# and the second entry set pin 18 low for a duration of 1000 microseconds
tone_1k = [pigpio.pulse(1 << pin, 0, 1000), pigpio.pulse(0, 1 << pin, 1000)]


# remember to execute "sudo pigpiod" on the Pi before executing

#instantiate pigpio
pi = pigpio.pi()
pi.set_mode(pin, pigpio.INPUT)
time.sleep(1)
pi.set_mode(pin, pigpio.OUTPUT)
delay_period = 1

# set the buzzer pin to output
#pi.set_mode(pin, pigpio.OUTPUT)
#pi.set_mode(17, pigpio.INPUT)

while True:

    # for angle in range(600, 2400):
    #     pi.set_servo_pulsewidth(pin, angle)
    #     time.sleep(delay_period)
    # for angle in range(2400, 600):
    #     pi.set_servo_pulsewidth(pin, angle)
    #     time.sleep(delay_period)

    pi.set_servo_pulsewidth(pin, 500)
    time.sleep(.2)
    pi.set_servo_pulsewidth(pin, 0)

    time.sleep(1)

    pi.set_servo_pulsewidth(pin, 1500)
    time.sleep(.2)
    pi.set_servo_pulsewidth(pin, 0)

    time.sleep(1)
