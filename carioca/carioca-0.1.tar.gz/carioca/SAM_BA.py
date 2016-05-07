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
from xmodem import XMODEM

import struct

SOL = bytes('\n\r', 'utf-8')	# start-of-line
EOL = bytes('\n\r>', 'utf-8')	# end-of-line

class Error(Exception):
    pass

class Monitor:

    @staticmethod
    def size_to_code(size):
        if size == 1:
            cmd = 'o'
        elif size == 2:
            cmd = 'h'
        elif size == 4:
            cmd = 'w'
        else:
            raise Error('Unsupported size', size)
        return cmd

    def __init__(self, serial_interface):
        self.serial = serial_interface
        self.binary_mode = False
        self.sol = SOL
        self.eol = EOL

    def _xmodem_getc(self, size, timeout=1):
        return self.serial.read(num_bytes=size)

    def _xmodem_putc(self, data, timeout=1):
        return self.serial.write(data)

    def _read_reply(self, sol, eol=None):
        eol_len = 0 if eol is None else len(eol)
        data = bytes()
        while True:
            ret = self.serial.read(1)
            if len(ret) == 0:
                continue
            data += ret
            if eol is None:
                if len(data) >= len(sol):
                    break
            elif data[len(data) - len(eol):] == eol:
                break
        if len(data) < len(sol):
            raise Error('Short read')
        if data[0:len(sol)] != sol:
            raise Error('Unexpected start-of-line', data)
        return data[len(sol):len(data) - eol_len]

    def version(self):
        self.serial.write(bytes('V#', 'utf-8'))
        return self._read_reply(sol=self.sol, eol=self.eol).decode('utf-8')

    def set_mode(self, binary_mode=False):
        if self.binary_mode == binary_mode:
            return
        if binary_mode:
            cmd = 'N'
            self.sol = bytes()	# No '\n\r' after command
            self.eol = SOL	# No '>' prompts
        else:
            cmd = 'T'
            self.eol = EOL	# '>' prompts in terminal mode
        self.serial.write(bytes('%c#' % cmd, 'utf-8'))
        self._read_reply(sol=self.eol)
        self.binary_mode = binary_mode

    def write(self, addr, value, size):
        cmd = self.size_to_code(size).upper()
        self.serial.write(bytes('%c%x,%x#' % (cmd, addr, value), 'utf-8'))
        if not self.binary_mode:
            self._read_reply(sol=self.eol)

    def write_byte(self, addr, value):
        self.write(addr, value, size=1)

    def write_halfword(self, addr, value):
        self.write(addr, value, size=2)

    def write_word(self, addr, value):
        self.write(addr, value, size=4)

    def read(self, addr, size):
        cmd = self.size_to_code(size).lower()
        self.serial.write(bytes('%c%x,#' % (cmd, addr), 'utf-8'))
        if self.binary_mode:
            code = 'BHHI'[size - 1]
            ret = self.serial.read(size)
            ret = struct.unpack('<%c' % code, ret)[0]
        else:
            ret = self._read_reply(sol=self.sol, eol=self.eol)
            ret = int(ret.decode('utf-8'), 16)
        return ret

    def read_byte(self, addr):
        return self.read(addr, 1)

    def read_halfword(self, addr):
        return self.read(addr, 2)

    def read_word(self, addr):
        return self.read(addr, 4)

    def send_file(self, addr, stream):
        self.serial.write(bytes('S%x,#' % addr, 'utf-8'))
        if not self.binary_mode:
            self._read_reply(sol=self.sol)
        prot = XMODEM(self._xmodem_getc, self._xmodem_putc)
        prot.send(stream)
        if not self.binary_mode:
            self._read_reply(sol=bytes('>', 'utf-8'))

    def receive_file(self, addr, size, stream):
        self.serial.write(bytes('R%x,%x#' % (addr, size), 'utf-8'))
        if not self.binary_mode:
            self._read_reply(sol=self.sol)
        prot = XMODEM(self._xmodem_getc, self._xmodem_putc)
        prot.recv(stream, delay=0)

    def go(self, addr):
        self.serial.write(bytes('G%x#' % addr, 'utf-8'))
        if not self.binary_mode:
            self._read_reply(sol=self.sol)
