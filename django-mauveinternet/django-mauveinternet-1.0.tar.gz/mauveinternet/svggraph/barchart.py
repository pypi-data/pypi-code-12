#!/usr/bin/python

import math
import re
import os
import cStringIO

from svg import xmlentities, Path, Graph
from table import Table
from colourscheme import *

class AbstractBarChart(object):
    """An abstract bar chart computes the underlying structure for a bar chart.

    A concrete implementation will convert this data to an SVG document."""
    class Bar(object):
        def __init__(self, color, label, x, w, h):
            self.color=color
            self.label=label
            self.h=h
            self.w=w
            self.x=x

        def label_xml(self):
            return xmlentities(self.label)

    class XAxisLabel(object):
        def __init__(self, label, x):
            self.label=label
            self.x=x        #x is the centreline for the label

        def label_xml(self):
            return xmlentities(self.label)

    class LegendLabel(object):
        def __init__(self, color, label):
            self.color=color
            self.label=label

        def label_xml(self):
            return xmlentities(self.label)

    def __init__(self, table, colors, width, height):
        """Expects a table whose values have been normalized to [0, 1]"""
        self.table=table
        self.width=width
        self.height=height
        self.colors=colors

    def __bar_spacing(self):
        """Retrieves a width of spacing to pad the bars in the graph apart.

        This calculation has been derived by trial and error and gives aesthetic spacings up to at least 25 cols."""
        if self.table.rows == 1 or self.table.cols == 1:
            return 0

        if self.table.cols > 25:
            pc_space=0.28
        else:
            pc_space=1-(self.table.cols**-0.1)

        return int((pc_space*(self.width-20))/(self.table.cols-1))

    def __bar_width(self):
        """Compute the space we can allocate to each bar"""
        return int((self.width-(self.table.cols-1)*self.__bar_spacing())/self.table.cols)

    def getBars(self):
        barspacing=self.__bar_spacing()
        barwidth=self.__bar_width()
        baroffset=barwidth/self.table.rows

        bars=[]

        for c in xrange(self.table.cols):
            for r in xrange(self.table.rows):
                v=self.table.getValue(c, r)

                h=int(float(v)*130)
                x=c*(barwidth+barspacing)+baroffset*r
                w=barwidth-(baroffset*(self.table.rows-1))

                col=self.colors.getColorForTableValue(v)
                bars.append(AbstractBarChart.Bar(color=col, label=str(v), x=x, w=w, h=h))

        return bars

    def getLabels(self):
        ls=[]
        barwidth=self.__bar_width()
        dx=barwidth+self.__bar_spacing()
        for c in range(self.table.cols):
            l=self.table.getColumnLabel(c)
            x=c*dx+barwidth/2
            if l:
                ls.append(AbstractBarChart.XAxisLabel(label=l, x=x))
        return ls

    def getLegend(self):
        if self.table.rows < 2:
            return []

        ls=[]
        for r in range(self.table.rows):
            ls.append(AbstractBarChart.LegendLabel(color=self.colors.getColor(r, 0), label=self.table.getRowLabel(r)))

        return ls


class BarChart(Graph):
    def __init__(self, table, colors=None, width=630, height=300):
        Graph.__init__(self, table, width=width, height=height)

        if colors is None:
            colors=DefaultColorScheme(table)

        self.chart=AbstractBarChart(table, colors, width-25, 159)

    def render(self, stream):
        self.svgHeader(stream)
        self.renderBars(stream)
        self.renderAxes(stream)
        self.svgFooter(stream)

    def renderAxes(self, stream):
        p=Path()
        p.to(9.5, 0)
        p.to(9.5, 159.5)
        p.to(self.width, 159.5)
        p.setClosed(False)
        stream.write('<path id="axes" d="%s" stroke="black" stroke-width="1" fill="none"/>\n'%p)

    def renderBars(self, stream):
        for bar in self.chart.getBars():
            self.renderGraphBar(stream, bar)

        for label in self.chart.getLabels():
            self.renderLabel(stream, label)

        legend=self.chart.getLegend()
        for r, l in enumerate(legend):
            stream.write('<g class="legend" transform="translate(%0.1f, %0.1f)">\n'%(5.5, self.height-19.5-20*(len(legend)-r-1)))
            self.renderAbstractBar(stream, 0, 0, 15, 15, l.color)
            stream.write('\t<text x="%0.1f" y="%0.1f">%s</text>\n'%(23, 8, l.label_xml()))
            stream.write('</g>\n')

    def renderGraphBar(self, stream, bar):
        y=159.5-bar.h
        x=bar.x+9.5
        self.renderAbstractBar(stream, x, y, bar.w, bar.h, bar.color, bar.label_xml())

    def renderAbstractBar(self, stream, x, y, w, h, color, labelxml=''):
        stream.write('<g>')
        stream.write('<rect x="%f" y="%f" width="%f" height="%f" stroke="black" stroke-width="1" fill="%s"/>'%(x, y, w, h, color))
        if labelxml:
            stream.write('<text transform="translate(%.1f, %.1f) rotate(270)">%s</text>'%(x+w/2+7, y-5, labelxml))
        stream.write('</g>\n')

    def renderLabel(self, stream, label):
        stream.write('<text class="label" text-anchor="end" transform="translate(%.2f, %.2f) rotate(270)">%s</text>\n'%(label.x+7+9.5, 164.5, label.label_xml()))

class BarChart3D(BarChart):
    def renderAbstractBar(self, stream, x, y, w, h, color, labelxml=''):
        stream.write('<g class="bar">\n')

        dy=2
        dx=4

        p=Path()
        p.to(x, y)
        p.to(x+dx, y-dy)
        p.to(x+w+dx, y-dy)
        p.to(x+w+dx, y-dy+h)
        p.to(x+w, y+h)
        p.to(x, y+h)
        stream.write('\t<path class="b" d="%s" fill="%s"/>\n'%(p, color))

        p=Path()
        p.to(x+w, y)
        p.to(x+w+dx, y-dy)
        p.to(x+w+dx, y-dy+h)
        p.to(x+w, y+h)
        stream.write('\t<path class="s" d="%s"/>\n'%p)

        p=Path()
        p.setClosed(False)
        p.to(x, y)
        p.to(x+w, y)
        stream.write('\t<path class="h" d="%s"/>\n'%p)

        if labelxml:
            stream.write('<text transform="translate(%.1f, %.1f) rotate(270)">%s</text>'%(x+w/2+7, y-5, labelxml))
        stream.write('</g>\n')

class PrettyBarChart(BarChart):
    def render(self, stream):
        self.svgHeader(stream)

        stream.write("""<defs>
<linearGradient id="highlight" gradientUnits="objectBoundingBox" x2="0%" y2="100%">
        <stop offset="0%" stop-color="white"/>
        <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
</defs>
""")
        self.renderAxes(stream)
        self.renderBars(stream)
        self.svgFooter(stream)

    def renderAxes(self, stream):
        stream.write('<g id="axes" opacity="0.2">)')
        stream.write('<rect x="7.5" y="0.5" width="%f" height="161" rx="6" stroke="black" fill="none" stroke-width="1" />'%(self.width-8))
        stream.write('<rect x="8" y="32" width="%f" height="32" fill="#e2d1f4" />'%(self.width-9))
        stream.write('<rect x="8" y="96" width="%f" height="32" fill="#e2d1f4" />'%(self.width-9))
        stream.write('</g>\n')

    def renderAbstractBar(self, stream, x, y, w, h, color, labelxml=''):
        inset=2
        stream.write('<g class="bar">\n')
        stream.write('\t<rect x="%f" y="%f" width="%f" height="%f" stroke="black" fill="%s" stroke-width="1" rx="4" />\n'%(x, y, w, h, color))
        stream.write('\t<rect x="%f" y="%f" width="%f" height="%f" fill="url(#highlight)" rx="3" />\n'%(x+inset, y+inset, w-inset*2, h/2))
        if labelxml:
            stream.write('\t<text transform="translate(%.1f, %.1f) rotate(270)">%s</text>\n'%(x+w/2+7, y-5, labelxml))
        stream.write('</g>\n')
