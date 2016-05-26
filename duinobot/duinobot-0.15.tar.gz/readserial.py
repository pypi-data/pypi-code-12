import serial
import sys
import time

print(sys.argv)
sp = serial.Serial(port=sys.argv[1], baudrate=57600)

while True:
    byte = ord(sp.read())
    if not byte:
        time.sleep(0.2)
        continue
    sys.stdout.write('0x{:02x} '.format(byte))
    print('')
