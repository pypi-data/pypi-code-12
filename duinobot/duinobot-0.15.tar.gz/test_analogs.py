from duinobot import *
import os
import time


b = TCPBoard()
r = Robot(b)

while True:
    os.system('clear')
    for i in range(A0, A5 + 1):
        print('Pin {}: {}'.format(i, b.analog(i)))
    time.sleep(0.5)
