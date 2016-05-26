# -*- coding: utf-8 -*-
import socket
import sys

def handle(msj, client):
    c = handle.c
    if msj[0] == 0x06:
        response = [0xf0, 0x06]
        response.append(c / 128)
        response.append(c % 128)
        # Robot id
        response.append(12)
        response.append(0xf7)
        response = ''.join(map(chr, response))
        print("Respuesta {}".format(
            ['0x{:02x}'.format(ord(b)) for b in response]
        ))
        client.sendall(response)
    c = (c + 1) % 2**14
    handle.c = c
handle.c = 0

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 1234))
server.listen(1)

START = 0xf0
END = 0xf7
DELIM = (START, END)

while True:
    client, clientaddr = server.accept()
    try:
        while True:
            sys.stderr.write('Esperando 0xf0\n')
            data = ord(client.recv(1))
            while data != START:
                sys.stderr.write("0x{:02x} ".format(data))
                data = ord(client.recv(1))
            sys.stderr.write('\n')
            assert data != END
            if data == START:
                sys.stderr.write('Leyendo y esperando 0xf7\n')
                msj = []
                data = ord(client.recv(1))
                while data not in DELIM:
                    sys.stderr.write("0x{:02x} ".format(data))
                    msj.append(data)
                    data = ord(client.recv(1))
                sys.stderr.write('\n')
                if data == END:
                    print(msj)
                    handle(msj, client)
                else:
                    print('Mensaje incompleto {}'.format(msj))
    except TypeError as e:
        print(e.message)
        client.close()
        continue
    except:
        client.close()
        server.close()
        raise

