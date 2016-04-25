#!/usr/bin/python

import math
import re
import os
import cStringIO

from svg import xmlentities, Path, Graph
from table import Table
from colourscheme import *

class AbstractPieChart(object):
    class PieSlice(object):
        def __init__(self, angle, color, label=''):
            self.startangle=0
            self.arcangle=angle
            self.color=color
            self.label=label

        def rotate(self, angle):
            self.startangle=(self.startangle+angle)%(2*math.pi)

        def label_xml(self):
            return xmlentities(self.label)

        def arc(self, cx=0.0, cy=0.0, rx=1.0, ry=None):
            if ry is None:
                ry=rx
            """Returns a list of 2 pairs of coordinates corresponding to the x and y positions of the slice"""
            return [(cx+rx*math.cos(self.startangle), cy-ry*math.sin(self.startangle)), (cx+rx*math.cos(self.startangle+self.arcangle), cy-ry*math.sin(self.startangle+self.arcangle))]

        def label_pos(self, cx=0.0, cy=0.0, rx=1.0, ry=None):
            if ry is None:
                ry=rx
            return (cx+rx*math.cos(self.startangle+self.arcangle/2), cy-ry*math.sin(self.startangle+self.arcangle/2))

        def front_edge(self, cx, cy, rx, ry):
            if self.startangle < math.pi and self.startangle+self.arcangle > math.pi:
                return [(cx-rx, cy),
                        self.arc(cx, cy, rx, ry)[1]]
            elif self.startangle >= math.pi:
                return self.arc(cx, cy, rx, ry)
            return None

    def __init__(self, table, row_number, colorscheme):
        self.table=table.asFracOfRow()
        self.colorscheme=colorscheme
        self.row=row_number

    def getSlices(self):
        slices=[]

        for c in xrange(self.table.cols):
            l=self.table.getColumnLabel(c)
            val=self.table.getValue(c, self.row)
            col=self.colorscheme.getColorForTableValue(val)
            if float(val) == 1.0:
                angle=math.pi*1.9999    # Correct a rendering glitch in Firefox 2
            else:
                angle=float(val)*2*math.pi
            slices.append(AbstractPieChart.PieSlice(angle, col, l))

        slices.sort(key=lambda s: -s.arcangle)

        #replace tiny slices with other

        other=[s for s in slices if s.arcangle < 0.2]
        for s in other:
            slices.remove(s)

        slices.append(AbstractPieChart.PieSlice(sum([s.arcangle for s in other]), Color.forName('silver'), u'Other'))

        angle=0
        for s in slices:
            s.rotate(angle)
            angle+=s.arcangle

        return slices

    def label_xml(self):
        return xmlentities(self.table.getRowLabel(self.row))

class PieChart(Graph):
    def __init__(self, table, cx=250, cy=130.5, r=100, value_labels=True, colors=None, width=625, height=300):
        Graph.__init__(self, table.asFracOfRow(), width=width, height=height)
        if colors is None:
            colors=DefaultColorScheme(table)
        self.colors=colors
        self.cx=cx
        self.cy=cy
        self.r=r
        self.value_labels=value_labels

    def render(self, stream):
        self.svgHeader(stream)
        rs=self.table.rows
        self.r=int(100/rs)
        for r in xrange(rs):
            self.angle=0
            self.cx=int((2*r+1)*self.width/(2*rs))+0.5

            chart=AbstractPieChart(self.table, r, self.colors)

            for slice in chart.getSlices():
                self.renderPieSlice(stream, slice)

            label=chart.label_xml()
            if label:
                stream.write('<text class="tit" x="%d" y="%d" text-anchor="middle">%s</text>'%(self.cx, self.cy+self.r+35, label))

        self.svgFooter(stream)

    def renderPieSlice(self, stream, slice):
        stream.write('<g class="pieslice">')
        s, e=slice.arc(self.cx, self.cy, self.r)
        stream.write('<path d="M %f,%f L %f,%f A %d,%d 0 %d,0 %f %f Z" fill="%s"/>'%(self.cx, self.cy, s[0], s[1], self.r, self.r, slice.arcangle > math.pi, e[0], e[1], slice.color))
        l=slice.label_pos(self.cx, self.cy, self.r+10)

        if l[0] > self.cx:
            tpos='start'
        else:
            tpos='end'

        if self.value_labels:
            label=slice.label_xml()+" (%s)"%val
        else:
            label=slice.label_xml()

        stream.write('<text x="%f" y="%f" font-size="10" text-anchor="%s">%s</text>'%(l[0], l[1], tpos, label))

        stream.write('</g>')

class PieChart3D(PieChart):
    def renderPieSlice(self, stream, slice):
        stream.write('<g class="pieslice">')

        rx=self.r
        ry=self.r*0.707

        s, e=slice.arc(self.cx, self.cy, rx, ry)
        stream.write('<path class="top" d="M %f,%f L %f,%f A %d,%d 0 %d,0 %f %f Z" fill="%s"/>'%(self.cx, self.cy, s[0], s[1], rx, ry, slice.arcangle > math.pi, e[0], e[1], slice.color))

        front=slice.front_edge(self.cx, self.cy, rx, ry)

        depth=5
        if front is not None:
            fs,fe=front
            stream.write('<path class="front" d="M %f,%f L %f,%f A %d,%d 0 0,0 %f %f L %f,%f A %d,%d 0 0,1 %f,%f Z" fill="%s"/>'%(fs[0], fs[1], fs[0], fs[1]+depth, rx, ry, fe[0], fe[1]+depth, fe[0], fe[1], rx, ry, fs[0], fs[1], slice.color.darker()))

        l=slice.label_pos(self.cx, self.cy, rx+10, ry+7)

        if l[1] > self.cy:
            l=(l[0],l[1]+depth+4)

        if l[0] > self.cx:
            tpos='start'
        else:
            tpos='end'

        if self.value_labels:
            label=slice.label_xml()+" (%s)"%val
        else:
            label=slice.label_xml()

        stream.write('<text x="%f" y="%f" font-size="10" text-anchor="%s">%s</text>'%(l[0], l[1], tpos, label))

        stream.write('</g>')
