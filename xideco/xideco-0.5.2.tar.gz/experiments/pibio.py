import time

import pigpio

pi = pigpio.pi()

pi.set_mode(22, pigpio.INPUT)

pi.set_mode(22, pigpio.OUTPUT)
pi.set_mode(9, pigpio.INPUT)
pi.write(22,0)
print('read1: ', pi.read(9))
pi.write(22, 1)
print('read2: ', pi.read(9))
time.sleep(3)
pi.write(22,0)
print('read3: ', pi.read(9))

pi.stop()
