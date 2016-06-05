# -*- coding: utf-8 -*-
from model.writer import writer


class memwriter(writer):
    """memwriter is a comodity class for writing C/C++ files"""
    def __init__(self, language="c++"):
        """initialization"""
        super(memwriter, self).__init__(language)
        self.data = []

    def writeln(self, txt=''):
        """write a line or secuence of lines with ident"""
        for l in txt.splitlines():
            self.data.append("{0}{1}\n".format(self.cident, l))

    def writenl(self, count=1):
        """write a newline"""
        for i in range(0, count):
            self.data.append('\n')

    def __str__(self):
        """dumps the string"""
        return ''.join(self.data)



