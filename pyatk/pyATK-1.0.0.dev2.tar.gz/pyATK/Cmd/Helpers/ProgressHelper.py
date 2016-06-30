# -*- coding: utf-8 -*-


class ProgressBarHelper:
    """
    >>> helper = ProgressBarHelper()
    >>> helper.setWidth(80)
    >>> helper.getWidth()
    80
    >>> helper.advance(10)
    \r|=======>                                                                        | 10%
    >>> helper.advance(90)
    \r|===============================================================================>| 100%
    """
    def __init__(self, bar_width=80, filledChar="=", emptyChar=" "):
        self.barWidth = bar_width
        self.filledChar = filledChar
        self.emptyChar = emptyChar
        self.progress = 0

    def setWidth(self, width):
        self.barWidth = width

    def getWidth(self):
        return self.barWidth

    def advance(self, step=1):
        if self.progress < 100:
            self.progress += step
            self.render()

    def render(self):
        normalizedProgress = (self.progress * self.barWidth) // 100
        to_print = "\r|" + "".join((normalizedProgress-1) * [self.filledChar]) + ">" + \
            "".join((self.barWidth - normalizedProgress) * [self.emptyChar]) + "| " + \
                   str(self.progress) + "%"

        print(to_print, end="")

        if self.progress == 100:
            print("")
