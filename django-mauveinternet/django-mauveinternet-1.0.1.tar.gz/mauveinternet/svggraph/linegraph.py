#!/usr/bin/python

import math
import re
import os
import cStringIO

from svg import xmlentities, Path, Graph
from axes import LineAxes
from table import Table
from colourscheme import *

LEGEND_ROW_HEIGHT = 20
SCALE = 0.70 # this is the proportion of the vertical space to use


class LineGraph(Graph):
    def __init__(self, table, colors=None, width=630, height=300, legend=True, shade_under=True, data_points=True, axes=None):
        Graph.__init__(self, table, width, height)

        if colors is None:
            self.colors = DefaultColorScheme(table)
        else:
            if issubclass(colors, ColorScheme):
                self.colors = colors(table)
            else:
                self.colors = colors

        self.axes = axes or LineAxes()

        self.legend = legend
        self.shade_under = shade_under
        self.data_points = data_points

        self.colwidth = (self.width-10)/float(self.table.cols-1)

    def legend_height(self):
        """Compute the amount of height to allocate to the legend"""
        if self.legend:
            return self.table.rows * LEGEND_ROW_HEIGHT + 0.5
        return 0

    def render(self, stream):
        """Render the graph to the file-like object stream"""
        self.svgHeader(stream)
        self.renderAxes(stream)
        for r in xrange(self.table.rows):
            self.renderRow(stream, r)
        if self.legend:
            self.renderLegend(stream)
        self.svgFooter(stream)

    def graph_dims(self):
        leg_h = self.legend_height()
        return (0.5, 0, self.width - 1, self.height - leg_h - 16.5)

    def renderAxes(self, stream):
        x, y, w, h = self.graph_dims()
        self.axes.render(stream, x, y, w, h, interval=h/4.0)

        #Vertical labelling
        #stream.write('<text text-anchor="end" transform="translate(14.5, %.2f) rotate(270)">%s</text>'%(h + 15, xmlentities(self.table.getColumnLabel(0))))
        #stream.write('<text text-anchor="end" transform="translate(%.2f, %.2f) rotate(270)">%s</text>'%(x + 5 + self.colwidth*(self.table.cols-1), h + 15, xmlentities(self.table.getColumnLabel(self.table.cols-1))))
        stream.write('<text style="fill: %s" text-anchor="start" transform="translate(%.2f, %.2f)">%s</text>'%(self.colors.getAxisColor(), x, h + 13, xmlentities(self.table.getColumnLabel(0))))
        stream.write('<text style="fill: %s" text-anchor="middle" transform="translate(%.2f, %.2f)">%s</text>'%(self.colors.getAxisColor(), x + self.colwidth*(self.table.cols-1), h + 13, xmlentities(self.table.getColumnLabel(self.table.cols-1))))
        stream.write('<text style="fill: %s; font-weight: bold" text-anchor="middle" transform="translate(%.2f, %.2f)">%s</text>' % (self.colors.getAxisColor(), x + w / 2, h + 13, xmlentities(self.table.getColumnAxisLabel())))

    def renderLegend(self, stream):
        x, y, w, h = self.graph_dims()
        for r in xrange(self.table.rows):
            leg_y = self.height - 0.5 - LEGEND_ROW_HEIGHT * (self.table.rows-r-1)
            stream.write('<g transform="translate(%0.1f, %0.1f)">'%(5.5, leg_y))
            stream.write('<path d="M 0,5 L 15, 5" stroke="%s" stroke-width="2"/>'%self.colors[r])
            stream.write('<text x="%0.1f" y="%0.1f">%s</text>'%(23, 8, xmlentities(self.table.getRowLabel(r))))
            stream.write('</g>')

    def renderRow(self, stream, r):
        x, y, w, h = self.graph_dims()
        p=Path()
        max=0
        cmax=None
        for c in xrange(self.table.cols):
            v = self.table.getValue(c, r)
            if float(v) >= max:
                max = float(v)
                cmax = c
            cx = x + self.colwidth * c
            cy = h - float(v) * SCALE * h
            if self.data_points:
                stream.write('<circle cx="%.1f" cy="%.1f" r="2" fill="%s" style="stroke: none" />\n'%(cx, cy, self.colors[r]))
            p.to(cx, cy)
        p.setClosed(False)
        stream.write('<path d="%s" stroke="%s" stroke-width="2" fill="none"/>\n'%(p, self.colors[r]))
        if self.shade_under:
            p.to(cx, y + h)
            p.to(x, y + h)
            stream.write('<path d="%s" fill="%s" fill-opacity="0.1"/>\n'%(p, self.colors[r]))

# Don't do this - we need an annotation system instead
#               if cmax and max:
#                       v = self.table.getValue(cmax, r)
#                       stream.write('<text x="%0.1f" y="%0.1f" text-anchor="middle" style="fill: %s">%s</text>'%(x + self.colwidth * cmax, h - 4 - float(v) * h * SCALE, self.colors[r], str(v)))


class InterpolatingLineGraph(LineGraph):
    def renderRow(self, stream, r):
        p=Path()
        max=0
        cmax=None
        for c in xrange(self.table.cols):
            v=self.table.getValue(c, r)
            if float(v) >= max:
                max=float(v)
                cmax=c
            x=9.5+self.colwidth*c
            y=159.5-float(v)*130
            p.to(x, y)
        p.setClosed(False)
        stream.write('<path d="%s V159.5 H9.5 z" stroke="none" fill="%s" fill-opacity="0.2"/>'%(p.toStringQuadratic(), self.colors[r]))
        if self.data_points:
            for c in p.coords:
                x,y=c
                stream.write('<circle cx="%.1f" cy="%.1f" r="2" fill="%s" style="stroke: none"/>\n'%(x,y, self.colors[r]))
        stream.write('<path d="%s" stroke="%s" stroke-width="2" fill="none"/>\n'%(p.toStringQuadratic(), self.colors[r]))
        if cmax != None:
            v=self.table.getValue(cmax, r)
            stream.write('<text x="%0.1f" y="%0.1f" text-anchor="middle" style="fill: %s">%s</text>'%(9.5+self.colwidth*cmax, 149.5-float(v)*130, self.colors[r], str(v)))
