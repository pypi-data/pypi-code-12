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
import copy
import termios

class Mode:

    def __init__(self, fd):
        self.fd = fd
        self.saved_attrs = termios.tcgetattr(fd)

    def set_raw(self, baudmask=None):
        if baudmask is None:
            baudmask = self.saved_attrs[4]
        attr = copy.copy(self.saved_attrs)
        attr[0] = termios.IGNBRK	# iflag
        attr[1] = 0			# oflag
        attr[2] = termios.CS8|termios.CREAD|termios.CLOCAL|baudmask	# cflag
        attr[3] = 0			# lflag
        attr[4] = baudmask		# ispeed
        attr[5] = baudmask		# ospeed
        attr[6][termios.VMIN] = 0	# min. characters to fulfill a read
        attr[6][termios.VTIME] = 1	# deciseconds to wait for reads
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, attr)

    def restore(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.saved_attrs)
