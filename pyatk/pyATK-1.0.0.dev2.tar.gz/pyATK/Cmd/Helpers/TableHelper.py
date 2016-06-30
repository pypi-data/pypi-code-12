# -*- coding: utf-8 -*-


class TableHelper:
    """
    >>> helper = TableHelper(79)
    >>> helper.addColumn('first name')
    >>> helper.addColumn('last name')
    >>> helper.setData([['my first name', 'my last name'], ['first']])
    >>> helper.display()
    +--------------------------------------------------------------------------------+
    |               first name              |               last name                |
    +--------------------------------------------------------------------------------+
    |             my first name             |              my last name              |
    +--------------------------------------------------------------------------------+
    |                 first                 |                                        |
    +--------------------------------------------------------------------------------+

    """
    def __init__(self, width=80):
        self.width = width
        self.headers = []
        self.dataSet = []
        self.columnWidth = 0

    def addColumn(self, title):
        self.headers.append(title)
        if self.width % len(self.headers) != 0:
            self.width += len(self.headers) - (self.width % len(self.headers))
        self.columnWidth = int(self.width / len(self.headers))

    def setData(self, dataset):
        self.dataSet = dataset
        for line in self.dataSet:
            if len(line) < len(self.headers):
                for i in range(0, len(self.headers) - len(line)):
                    line.append(" ")

    def display(self):
        self.printHeader()
        for line in self.dataSet:
            self.printDataLine(line)

    def printDataLine(self, data_line):
        for item in data_line:
            print("|" + str(item).center(self.columnWidth - 1), end="")
        print(" |")
        self.printLineSeparator()

    def printHeader(self):
        self.printLineSeparator()
        self.printDataLine(self.headers)

    def printLineSeparator(self):
        print("+" + str(self.width * "-") + "+")

