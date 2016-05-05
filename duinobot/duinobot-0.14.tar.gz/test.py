import duinobot
import pyfirmata
import time

rid = 16

b = duinobot.TCPBoard()
print(b.report)
r = duinobot.Robot(b, 16)
r.forward(100, 1)
r.backward(100, 1)
r.turnLeft(100, 1)
r.turnRight(100, 1)
print(r.ping())
print(r.getLine())
print('Digital {}'.format(b.digital(2, rid)))
b.set_pin_mode(2, pyfirmata.pyfirmata.INPUT, rid)
print('Digital {}'.format(b.digital(2, rid)))

for i in range(20):
    print('Digital {}'.format(b.digital(2, rid)))
    time.sleep(5)
