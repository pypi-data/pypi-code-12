from um7 import UM7

name = 'sensor'
port = '/dev/tty.usbserial-A903AAV1'

sensor = UM7(name, port)
sensor.settimer()
sensor.zerogyros()
sensor.resetekf()

while True:
    # sensor.grabsample(['xaccel', 'yaccel', 'zaccel', 'xgyro', 'rollpitch', 'yaw'])
    sensor.catchsample()
    print sensor.state


