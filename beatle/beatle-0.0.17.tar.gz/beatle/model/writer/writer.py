# -*- coding: utf-8 -*-


class writer(object):
    """Implements a generic C++ writer."""
    def __init__(self, language="c++"):
        """initialize the writer class"""
        self.cident = ""
        self._language = language
        super(writer, self).__init__()

    @classmethod
    def for_file(cls, fhandle, language="c++"):
        """method for new writer"""
        from model.writer import filewriter
        return filewriter(fhandle, language)

    @classmethod
    def for_mem(cls):
        """method for new writer"""
        from model.writer import memwriter
        return memwriter()

    def ident(self):
        """Increase ident size"""
        self.cident += "\t"

    def unident(self):
        """Increase ident size"""
        self.cident = self.cident[:-1]

    def openbrace(self, text=''):
        """Opens a brace"""
        if self._language == 'c++':
            self.writeln("{}{{".format(text))
        else:
            self.writeln("{}".format(text))
        self.ident()

    def closebrace(self, text=''):
        """Closes a brace"""
        self.unident()
        if self._language == 'c++':
            self.writeln("}}{}".format(text))
        else:
            self.writeln("{}".format(text))

    def writecomment(self, text):
        """Write a multiline comment respecting nesting"""
        self.opencomment()
        if type(text) is not str:  # avoid null fields
            text = str(text)
        for x in text.split('\n'):
            self.writeln('{}'.format(x.strip()))
        self.closecomment()

    def writeblock(self, text):
        """Write a text increasing nesting as required"""
        for x in text.split('\n'):
            self.writeln(x)

    def opencomment(self):
        """Open a c comment"""
        if self._language == 'c++':
            self.writeln("/*")
        if self._language == 'python':
            self.writeln("\"\"\"")

    def closecomment(self):
        """Close a c commen"""
        if self._language == 'c++':
            self.writeln("*/")
        elif self._language == 'python':
            self.writeln("\"\"\"")
