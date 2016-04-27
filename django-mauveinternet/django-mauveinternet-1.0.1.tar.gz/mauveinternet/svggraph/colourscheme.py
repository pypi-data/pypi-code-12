#!/usr/bin/python

import math
import re
import os
import cStringIO

class Color(object):
    def __init__(self, triple):
        self.t=triple

    def __str__(self):
        return '#%02X%02X%02X'%self.t

    def darker(self):
        return Color(tuple([int(comp*0.7) for comp in self.t]))

    @staticmethod
    def parseHex(s):
        n=int(s[1:], 16)
        return Color(((n & 0xff0000) >> 16, (n & 0xff00) >> 8, n & 0xff))

    names={'red':'#ff0000',
            'white':'#ffffff',
            'black':'#000000',
            'silver':'#cccccc',
            'lime':'#00ff00',
            'blue':'#0000ff'}

    @staticmethod
    def forName(n):
        return Color.parseHex(Color.names[n])

class ColorScheme(object):
    scheme=['#ff0000']
    axes = '#000000'

    def __init__(self, table):
        self.table=table

    def getColor(self, row, col):
        return self[row]

    def getAxisColor(self):
        return Color.parseHex(self.axes)

    def getColorForTableValue(self, value):
        return self.getColor(value.row, value.col)

    def __getitem__(self, index):
        return Color.parseHex(self.scheme[int(index) % len(self.scheme)])

class DefaultColorScheme(ColorScheme):
    scheme=['#ff0000', '#00C0FF', '#FFC000', '#60C060', '#6060FF', '#C080FF', '#FF8040', '#40D0C0', '#FF8080', '#C0C0C0']

class MauveColorScheme(ColorScheme):
    scheme=['#b59dda', '#748fd6']

class GradientColorScheme(ColorScheme):
    def __init__(self, table, startcolor='#ff0000', endcolor='#0000ff'):
        ColorScheme.__init__(self, table)
        self.scheme=self.createGradient(startcolor, endcolor, self.table.cols)

    def createGradient(self, start, stop, steps):
        startc=self.parseHex(start)
        stopc=self.parseHex(stop)
        colors=[]

        for i in range(steps):
            col=[0]*3
            for comp in [0, 1, 2]:
                col[comp]=startc[comp]+int((stopc[comp]-startc[comp])*float(i)/steps)
            colors.append(self.makeHex(tuple(col)))

        return colors

    def parseHex(self, s):
        n=int(s[1:], 16)
        return ((n & 0xff0000) >> 16, (n & 0xff00) >> 8, n & 0xff)

    def makeHex(self, t):
        return '#%02X%02X%02X'%t

class RatingColorScheme(GradientColorScheme):
    def __init__(self, table):
        GradientColorScheme.__init__(self, table)
        self.scheme=self.createGradient('#C80000', '#C8C600', 10)+self.createGradient('#C8C600', '#3AC800', 11)[1:]
