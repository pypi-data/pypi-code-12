#!/usr/bin/python

import math
import re
import os
import cStringIO

def xmlentities(st):
    s=''
    for c in st:
        if ord(c) > 127 or ord(c) < 28:
            s+='&#'+ord(c)+';'
        elif c == '&':
            s+='&amp;'
        elif c == '<':
            s+='&lt;'
        elif c == '>':
            s+='&gt;'
        elif c == '"':
            s+='&quot;'
        else:
            s+=c
    return s

class Path(object):
    def __init__(self):
        self.coords=[]
        self.closed=True

    def duplicate(self):
        p=Path()
        p.coords=self.coords[:]
        p.closed=self.closed
        return p

    def setClosed(self, closed):
        self.closed=closed

    def to(self, x, y):
        self.coords.append((float(x), float(y)))

    def toStringQuadratic(self):
        if not self.coords:
            return ''
        c=self.coords[0]
        s='M%.1f,%.1f'%c
        x,y=c
        for ci in xrange(0, len(self.coords)):
            c=self.coords[ci]
            if ci < (len(self.coords) - 1):
                nextx,nexty=self.coords[ci+1]
                s+=' Q%.2f,%.2f %.2f,%.2f'%(c[0], c[1], (nextx+c[0])/2, (nexty+c[1])/2)
            else:
                s+=' L%.2f,%.2f'%(c[0], c[1])
            x,y=c
        if self.closed:
            s+=' z'
        return s

    def toStringSmooth(self):
        if not self.coords:
            return ''
        c=self.coords[0]
        s='M%.1f,%.1f'%c
        x,y=c
        for ci in xrange(1, len(self.coords)):
            c=self.coords[ci]
            dx=c[0]-x
            dy=c[1]-y
            if ci < len(self.coords) - 1:
                nextx,nexty=self.coords[ci+1]
                coeff=0.2
                tangx,tangy=nextx-x, nexty-y
                tlen=1 #math.sqrt(tangx**2+tangy**2)
                tangx,tangy=coeff*tangx/tlen,coeff*tangy/tlen
                s+=' s%.1f,%.1f %.1f,%.1f'%(dx-tangx, dy-tangy, dx, dy)
            else:
                s+=' s%.1f,%.1f %.1f,%.1f'%(dx, dy, dx, dy)
            x,y=c
        if self.closed:
            s+=' z'
        return s

    def toStringCosine(self):
        if not self.coords:
            return ''
        c=self.coords[0]
        s='M%.1f,%.1f'%c
        x,y=c
        for ci in xrange(1, len(self.coords)):
            c=self.coords[ci]
            dx=c[0]-x
            dy=c[1]-y
            s+=' s%.1f,%.1f %.1f,%.1f'%(dx*0.5, dy, dx, dy)
            x,y=c
        if self.closed:
            s+=' z'
        return s

    def __str__(self):
        if not self.coords:
            return ''
        c=self.coords[0]
        s='M%.1f,%.1f'%c
        x,y=c
        for c in self.coords[1:]:
            dx=c[0]-x
            dy=c[1]-y
            if dx == 0:
                s+=' v%.1f'%dy
            elif dy == 0:
                s+=' h%.1f'%dx
            else:
                s+=' l%.1f,%.1f'%(c[0]-x, c[1]-y)
            x,y=c
        if self.closed:
            s+=' z'
        return s


class SVGDocument(object):
    """Utility class for drawing procedurally to an SVG document."""
    def __init__(self, width=625, height=300, stylesheet=None):
        self.stream = StringIO()

        if stylesheet is None:
            stylesheet = """
text {font-family: "Arial", sans-serif; font-size: 8pt; fill: black}
circle {stroke: black; stroke-width: 0.5px}
.bar .b {stroke-width: 0.5px; stroke: black}
.bar .s {stroke: none; fill: black; fill-opacity: 0.3}
.bar .h {fill: none; stroke: white; stroke-opacity: 0.4}
.tit {font-weight: bold; font-size: 12px}
.pieslice path {stroke: black; stroke-width: 0.5px;}
"""

        self.stream.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="%dpx" height="%dpx" version="1.1"
xmlns="http://www.w3.org/2000/svg">
<style type="text/css"><![CDATA[
""" % (width, height))
        self.stream.write(stylesheet)
        self.stream.write("""]]></style>       """)

    def getvalue(self):
        return self.stream.getvalue() + "</svg>"

    def write(self, s):
        self.stream.write(s)

    def rect(self, x, y, w, h, fill_color='black', stroke_color='none', stroke_width=1):
        self.write('<rect x="%f" y="%f" width="%f" height="%f" stroke-width="%d" stroke="%s" fill="%s"/>\n' % (x, y, w, h, stroke_width, stroke_color, fill_color))

    def line(self, x1, y1, x2, y2, stroke_color='black', stroke_width=1):
        p = Path()
        p.to(x1, y1)
        p.to(x2, y2)
        self.path(p, stroke_color, 'none', stroke_width)

    def path(self, path, stroke_color='black', fill_color='rgba(0, 0, 0, 0.1)', stroke_width=1):
        self.write('<path d="%s" stroke="%s" stroke-width="%d" fill="%s" />' % (path, stroke_color, stroke_width, fill_color))

    def text(self, x, y, text, color='black', anchor='start'):
        self.write('<text style="fill: %s" text-anchor="%s" transform="translate(%.2f, %.2f)">%s</text>' % (color, anchor, x, y, xmlentities(text)))


class Graph(object):
    class Value(object):
        pass
    def __init__(self, table, width=625, height=300):
        self.table=table
        self.width=width
        self.height=height

    def setSize(self, width, height):
        self.width=width
        self.height=height

    def renderToString(self):
        s=cStringIO.StringIO()
        self.render(s)
        svg=s.getvalue()
        s.close()
        return svg

    def svgHeader(self, stream):
        stream.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="%dpx" height="%dpx" version="1.1"
xmlns="http://www.w3.org/2000/svg">
<style type="text/css"><![CDATA[
text {font-family: "Arial", sans-serif; font-size: 8pt; fill: black}
circle {stroke: black; stroke-width: 0.5px}
.bar .b {stroke-width: 0.5px; stroke: black}
.bar .s {stroke: none; fill: black; fill-opacity: 0.3}
.bar .h {fill: none; stroke: white; stroke-opacity: 0.4}
.tit {font-weight: bold; font-size: 12px}
.pieslice path {stroke: black; stroke-width: 0.5px;}
"""%(self.width, self.height))
        stream.write("""]]></style>       """)

    def svgFooter(self, stream):
        stream.write("</svg>")
