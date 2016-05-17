#!/usr/bin/env python
import os

AInis = [90,100,75]
AMins = [50,70,20] 
AMaxs = [130,130,120] 
ACurs = AInis

os.system('sudo /home/pi/servo_tests/PiBits/ServoBlaster/user/servod --idle-timeout=500')


def setServo(servo_number,angle):
    if angle >= AMins[servo_number] and angle <= AMaxs[servo_number]:
        ACurs[servo_number]=angle
        micro = 1000 + (angle*8.3333)
        print "Moving %d to %d" % (servo_number , angle)
        os.system("echo %d=%dus > /dev/servoblaster" % (servo_number,micro))
    else:
        print "Limit angle reached"

def setAllServos(angle1,angle2,angle3,reset=False):
    setServo(0,angle1)
    setServo(1,angle2)
    setServo(2,angle3)
    if reset:
        reset()

def reset():
    setServo(0,AInis[0])
    setServo(1,AInis[1])
    setServo(2,AInis[2])

def getPosition():
    print "Servo 0 position: %d" % ACurs[0]
    print "Servo 1 position: %d" % ACurs[1]
    print "Servo 2 position: %d" % Acurs[2]

