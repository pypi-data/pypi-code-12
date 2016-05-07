#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable=I0011,W0231

"""Keyboard control"""

__author__ = 'Bartosz Kościów'
__credits__ = "http://stackoverflow.com/questions/510357/" \
              "python-read-a-single-character-from-the-user"

import socket
import termios
import sys, tty

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024


def getch():
    """get char from io buffer"""
    file_description = sys.stdin.fileno()
    old_settings = termios.tcgetattr(file_description)
    try:
        tty.setraw(file_description)
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(file_description, termios.TCSADRAIN, old_settings)

    if char == '\x03':
        raise KeyboardInterrupt
    elif char == '\x04':
        raise EOFError
    return char


def keyboard_main():
    """main loop"""
    try:
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_socket.connect((TCP_IP, TCP_PORT))
        while True:
            key = getch()
            if key == 'a':
                conn_socket.send('player.move.left')
            if key == 'd':
                conn_socket.send('player.move.right')
            if key == ' ':
                conn_socket.send('player.move.fire')

    finally:
        conn_socket.close()

if __name__ == '__main__':
    keyboard_main()
