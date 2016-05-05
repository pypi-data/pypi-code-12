from duinobot import *

try:
    #b = TCPBoard('localhost')
    b = TCPBoard()
except NameError:
    b = Board()
r = Robot(b, 12)

while True:
    i, d = r.getLine()
    print((i, d) if i != d else '({}, {}) son iguales'.format(i, d))
    print(b.report())

b.exit()
