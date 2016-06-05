# -*- coding: utf-8 -*-
from model.writer import writer


class filewriter(writer):
    """filewiter is a comodity class for writing C/C++ files"""
    def __init__(self, fhandle, language="c++"):
        """initialization"""
        super(filewriter, self).__init__(language)
        self.file = fhandle

    def writeln(self, txt=''):
        """write a line or secuence of lines with ident"""
        for l in txt.splitlines():
            self.file.write("{0}{1}\n".format(self.cident, l))

    def writenl(self, count=1):
        """write a newline"""
        for i in range(0, count):
            self.file.write("\n")


