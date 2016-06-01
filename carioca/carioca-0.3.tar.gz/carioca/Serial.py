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
import atexit
import os
import termios

from . import TTY

class Error(Exception):
    pass

class Device:

    def __init__(self, port, baudrate):
        self.fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
        baud_name = 'B%u' % baudrate
        if baud_name not in termios.__dict__:
            raise Error('Unknown baudrate %u.' % baudrate)
        baud_mask = termios.__dict__[baud_name]
        self.tty_mode = TTY.Mode(self.fd)
        atexit.register(self.tty_mode.restore)
        self.tty_mode.set_raw(baud_mask)

    def write(self, data):
        num_written = 0
        while num_written < len(data):
            ret = os.write(self.fd, data[num_written:])
            if ret < 0:
                raise Error('Write error %d after %u bytes written' %
                            (ret, num_written))
            num_written += ret

    def read(self, num_bytes):
        data = bytes()
        while True:
            ret = os.read(self.fd, num_bytes - len(data))
            data += ret
            if len(data) >= num_bytes:
                return data
