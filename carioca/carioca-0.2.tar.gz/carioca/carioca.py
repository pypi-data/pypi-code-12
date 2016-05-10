#!/usr/bin/env python3
#
# The MIT License (MIT)
#
# Copyright (c) 2016 eGauge Systems LLC
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import argparse
import atexit
import os
import re
import select
import sys

from . import SAM_BA
from . import Serial
from . import TTY
from . import commands

PROMPT = 'carioca> '
samba = None

def execute_script(serial, script, scope, text_mode):
    def get_samba():
        global samba
        if samba is None:
            samba = SAM_BA.Monitor(serial)
            if not text_mode:
                samba.set_mode(binary_mode=True)
            print('Connected to SAM-BA Monitor %s' % samba.version())
        return samba

    line_number = 0
    cmd = ''
    if script.isatty():
        os.write(script.fileno(), PROMPT.encode('utf-8'))
    for line in script:
        line_number += 1
        cmd += line.strip(' \t\r\n')
        if len(cmd) < 1:
            continue
        if cmd[0] == '#':	# comment
            cmd = ''
            continue
        if cmd[len(cmd) - 1] == '\\':
            cmd = cmd[0:len(cmd) - 1]
        else:
            try:
                commands.execute(scope, get_samba, cmd)
            except commands.Error:
                print('%s:%u: Error: %s' % \
                      (script.name, line_number, sys.exc_info()[1]),
                      file=sys.stderr)
                return
            except commands.Command_Done as e:
                if e.args[0] == 'quit':
                    return False
                elif e.args[0] == 'go':
                    return True
                else:
                    print('%s: unknown Command_Done %s' % (parser.prog, e))
            cmd = ''
        if script.isatty():
            os.write(script.fileno(), PROMPT.encode('utf-8'))

def terminal_mode(serial):
    print(79*'-' + '\n' +
          'Entering terminal-emulation mode (exit with: Ctrl-] quit):\n' +
          79*'-')

    ctty_mode = TTY.Mode(0)
    atexit.register(ctty_mode.restore)
    ctty_mode.set_raw()
    stdin_fd = sys.stdin.fileno()
    while True:
        # select.select() is the most portable version and we're only dealing
        # with two file descriptors, so scalability is not a concern:
        rlist, wlist, xlist = select.select ([ serial.fd, stdin_fd ], [], [])
        if stdin_fd in rlist:
            data = os.read(stdin_fd, 128)
            if len(data) == 1 and data[0] == 0x1d:
                # User typed Ctrl-]
                ctty_mode.restore()
                print('')
                while True:
                    cmd = input('carioca> ').strip()
                    if cmd == 'quit':
                        sys.exit(0)
                    elif cmd == '' or cmd == 'send':
                        ctty_mode.set_raw()
                        if cmd == 'send':
                            serial.write(b'\x1d')
                        break
                    else:
                        print(
                            'Available commands:\n'
                            '\t   quit: Exit carioca\n'
                            '\t   send: Send Ctrl-] character\n'
                            '\t<Enter>: Return to terminal-emulation mode')
            else:
                serial.write(data)
        if serial.fd in rlist:
            ret = os.read(serial.fd, 128)
            os.write(1, ret)

def main():
    parser = argparse.ArgumentParser(description='Carioca is an open-source '
                                     'variant of Atmel\'s SAM-BA utility.  '
                                     'It provides scriptable support for '
                                     'interacting with a Atmel '
                                     'microcontroller\'s SAM-BA Monitor '
                                     'through a serial interface '
                                     '(serial-over-USB or direct serial port, '
                                     'such as the Debug serial port found '
                                     'on most Atmel microcontrollers).  '
                                     'Once a "go" '
                                     'command is issued, Carioca enters '
                                     'terminal-emulation mode.  This enables '
                                     'interacting with the target system as '
                                     'needed.  To exit terminal-emulation '
                                     'mode, use Ctrl-] followed by "quit".',
                                     formatter_class=\
                                     argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('script_or_assignment',
                        help='Filename of script to execute or a variable '
                        'assignment of the form NAME=VALUE.',
                        nargs='*')
    parser.add_argument('-p', '--serial-port',
                        help='Name of the serial port to open.',
                        nargs='?', default='/dev/ttyUSB0')
    parser.add_argument('-b', '--baud-rate',
                        help='Baudrate to use with serial-port.',
                        nargs='?', type=int, default=115200)
    parser.add_argument('-s', '--set', help='Set variable NAME to value VAL.',
                        nargs=2, action='append', metavar=('NAME', 'VAL'))
    parser.add_argument('-t', '--text-mode',
                        help='Use text-mode instead of binary mode to '
                        'communicate with the SAM-BA Monitor.',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    serial = Serial.Device(args.serial_port, args.baud_rate)
    scope = {}	# variable scope

    num_scripts = 0
    for assignment_or_script in args.script_or_assignment:
        m = re.match(r'([a-z_][a-z_0-9]*)=(.*)', assignment_or_script,
                     re.IGNORECASE)
        if m:
            name = m.group(1)
            value = m.group(2)
            scope[name] = value
        else:
            num_scripts += 1
            if assignment_or_script == '-':
                script = sys.stdin
            else:
                script = open(assignment_or_script, 'r')
            if execute_script(serial, script, scope, args.text_mode):
                terminal_mode(serial)
                break

    if num_scripts == 0:
        terminal_mode(serial)

if __name__ == '__main__':
    main()
