import socket
import sys

server = socket.create_connection(('192.168.4.1', 1234))
msj = [0xf0, 0x09, 0xf7]
server.sendall(''.join(map(chr, msj)))

while True:
    byte = ord(server.recv(1))
    sys.stdout.write('0x{:02x} '.format(byte))
    if byte == 0xf7:
        print('')
