#!/usr/bin/python

import math
import re
import os
import cStringIO

class ColorScheme(object):
    scheme=['red']

    def __init__(self):
        pass

    def getColor(self, row, col):
        return self[row]

    def __getitem__(self, index):
        return self.scheme[int(index) % len(self.scheme)]

class DefaultColorScheme(ColorScheme):
    scheme=['#ff0000', '#00C0FF', '#FFC000', '#60C060', '#6060FF', '#C080FF', '#FF8040', '#40D0C0', '#FF8080', '#C0C0C0']

class MauveColorScheme(ColorScheme):
    scheme=['#b59dda', '#748fd6']

class RatingColorScheme(ColorScheme):
    def __init__(self):
        self.scheme=self.createGradient('#C80000', '#C8C600', 10)+self.createGradient('#C8C600', '#3AC800', 11)[1:]

    def getColor(self, row, col):
        return self[col]

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

class Table(object):
    class Value(object):
        def __init__(self, table, col, row, val):
            self.table=table        #reference to the parent table
            self.row=row            #row index in the parent table
            self.col=col            #column index in the parent table
            self.value=float(val)           #value
            self.displayvalue=str(int(self.value+0.5))
            self.frac=None

        #instead of all these weird and wonderful functions,
        # allow the table to be renomalized by the consumer and just provide two casts
        # cast to string: the value to be displayed - may contain units etc
        # cast to float fracOfMax(): a fraction in [0,1]
        def __str__(self):
            return self.displayvalue

        def __float__(self):
            if not self.table.normalized:
                self.table.normalize()
            return self.frac

#               def fracOfRow(self):
#                       """Turns out we still need this one"""
#                       self.__normalize()
#                       try:
#                               return float(self.value)/self.table.rowtotals[self.row]
#                       except ZeroDivisionError:
#                               return 0
#
#               def percentOfRow(self):
#                       return int(self.fracOfRow()*100+0.5)
#
#               def fracOfTotal(self):
#                       self.__normalize()
#                       try:
#                               return float(self.value)/self.table.total
#                       except ZeroDivisionError:
#                               return 0
#
#               def percentOfTotal(self):
#                       return int(self.fracOfTotal()*100+0.5)
#
#
#               def fracOfMax(self):
#                       self.__normalize()
#                       try:
#                               return float(self.value)/self.table.max
#                       except ZeroDivisionError:
#                               return 0
#
#               def fracOfRowMaxFrac(self):
#                       return self.fracOfRow()/self.table.maxofmaxfracsofrow
#
#
#               def fracOfRowMax(self):
#                       self.__normalize()
#                       try:
#                               return float(self.value)/self.table.rowmax[self.row]
#                       except ZeroDivisionError:
#                               return 0
#
#               def __repr__(self):
#                       return "Value(%d)"%self.value "stupid vim """

    def __init__(self, cols, rows):
        self.values=[[Table.Value(self, col, row, 0) for col in xrange(cols)] for row in xrange(rows)]
        self.columnlabels=['']*cols
        self.rowlabels=['']*rows
        self.cols=cols
        self.rows=rows
        self.total=0
        self.forcetotal=None
        self.normalized=False
        self.columnaxislabel=''
        self.rowaxislabel=''

    def duplicate(self):
        t=Table(self.cols, self.rows)
        for r in xrange(self.rows):
            t.setRowLabel(r, self.rowlabels[r])
            for c in xrange(self.cols):
                t.setValue(c, r, self.values[r][c].value)
                t.getValue(c, r).displayvalue=self.values[r][c].displayvalue
        for c in xrange(self.cols):
            t.setColumnLabel(c, self.columnlabels[c])
        t.setRowAxisLabel(self.getRowAxisLabel())
        t.setColumnAxisLabel(self.getColumnAxisLabel())
        return t

    def asPercentOfConstant(self, constant):
        t=self.duplicate()
        if constant == 0:
            constant=1
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                v=t.getValue(c, r)
                v.value=v.value/constant
                v.displayvalue=str(int(v.value*100+0.5))+'%'
        return t

    def asPercentOfTotal(self):
        total=0
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                v=self.getValue(c, r)
                total+=v.value
        if total == 0:
            total=1
        return self.asPercentOfConstant(total)

    def asPercentOfRow(self):
        t=self.duplicate()
        for r in xrange(self.rows):
            rowtotal=0
            for c in xrange(self.cols):
                v=t.getValue(c, r)
                rowtotal+=v.value
            if rowtotal == 0:
                rowtotal=1
            for c in xrange(self.cols):
                v=t.getValue(c, r)
                v.value=v.value/rowtotal
                v.displayvalue=str(int(v.value*100))+'%'
        return t

    def asFracOfRow(self):
        t=self.duplicate()
        for r in xrange(self.rows):
            rowtotal=0
            for c in xrange(self.cols):
                v=self.getValue(c, r)
                rowtotal+=v.value
            for c in xrange(self.cols):
                v=t.getValue(c, r)
                try:
                    v.frac=v.value/rowtotal
                except ZeroDivisionError:
                    v.frac=0
        t.normalized=True
        return t


#       def setTotal(self, t):
#               """Sets a total value which lies outside the table"""
#               self.forcetotal=t

    def normalize(self):
        """Compute the max in the table and the total of each row"""
        if self.normalized:
            return
        max=0
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                v=self.getValue(c, r)
                if not v:
                    continue
                if v.value > max:
                    max=v.value
        if max == 0:
            max=1
        for r in xrange(self.rows):
            for c in xrange(self.cols):
                v=self.getValue(c, r)
                v.frac=v.value/max

#       def old_normalize(self):
#               self.max=0
#               self.total=0
#               self.rowtotals=[0]*self.rows
#               self.rowmax=[0]*self.rows
#               for r in xrange(self.rows):
#                       for c in xrange(self.cols):
#                               v=self.getValue(c, r)
#                               if not v:
#                                       continue
#                               if v.value > self.max:
#                                       self.max=v.value
#                               if v.value > self.rowmax[r]:
#                                       self.rowmax[r]=v.value
#                               self.total+=v.value
#                               self.rowtotals[r]+=v.value
#               self.rowtotalsmax=max(self.rowtotals)
#               self.maxfracsofrow=[self.rowmax[r]/(self.rowtotals[r]+0.0000001) for r in xrange(self.rows)]
#               self.maxofmaxfracsofrow=max(self.maxfracsofrow)
#               if self.forcetotal != None:
#                       self.total=self.forcetotal
#               self.normalized=True

    def transpose(self):
        oldvals=self.values
        self.values=[[oldvals[row][col] for row in xrange(self.rows)] for col in xrange(self.cols)]
        rs=self.rows
        self.rows=self.cols
        self.cols=rs
        rls=self.rowlabels
        self.rowlabels=self.columnlabels
        self.columnlabels=rls
        self.normalized=False
        ral=self.rowaxislabel
        self.rowaxislabel=self.columnaxislabel
        self.columnaxislabel=ral

    def transposed(self):
        t=self.duplicate()
        t.transpose()
        return t

    def getValue(self, col, row):
        return self.values[row][col]

    def setValue(self, col, row, val):
        self.values[row][col]=Table.Value(self, col, row, val)
        self.normalized=False

    def addToValue(self, col, row, val):
        if not self.values[row][col]:
            self.setValue(col, row, 0)
        v=self.values[row][col]
        self.setValue(col, row, v.value+val)
        self.normalized=False

    def getRow(self, row):
        return self.values[row][:]

    def getColumn(self, col):
        return [row[col] for row in self.values]

    def setColumnLabel(self, col, label):
        self.columnlabels[col]=label

    def setRowLabel(self, row, label):
        self.rowlabels[row]=label

    def getColumnLabel(self, col):
        return self.columnlabels[col]

    def getRowLabel(self, col):
        return self.rowlabels[col]

    def setColumnLabels(self, labels):
        if len(labels) !=  self.cols:
            raise ValueError("Incompatible size for column labels")
        self.columnlabels=labels

    def setRowLabels(self, labels):
        if len(labels) !=  self.rows:
            raise ValueError("Incompatible size for row labels")
        self.rowlabels=labels

    def setRowAxisLabel(self, l):
        self.rowaxislabel=l

    def setColumnAxisLabel(self, l):
        self.columnaxislabel=l

    def getRowAxisLabel(self):
        return self.rowaxislabel

    def getColumnAxisLabel(self):
        return self.columnaxislabel

    def __repr__(self):
        return "Table("+str(self.values)+")"

class BasicBarRenderer(object):
    def __init__(self, stream):
        self.stream=stream
    def renderLabel(self, x, y, width, label):
        self.stream.write('<text transform="translate(%.1f, %.1f) rotate(270)">%s</text>'%(x+width/2+7, y-5, label))

    def renderBar(self, x, y, width, height, color, label=None):
        self.stream.write('<g>')
        self.stream.write('<rect x="%f" y="%f" width="%f" height="%f" stroke="black" stroke-width="1" fill="%s"/>'%(x, y, width, height, color))
        if label:
            self.renderLabel(x, y, width, label)
        self.stream.write('</g>')

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

class BarRenderer3D(BasicBarRenderer):
    def __init__(self, stream):
        BasicBarRenderer.__init__(self, stream)

    def renderBar(self, x, y, width, height, color, label=None):
        self.stream.write('<g class="bar">\n')

        p=Path()
        p.to(x, y)
        p.to(x+6, y-3)
        p.to(x+width+6, y-3)
        p.to(x+width+6, y-3+height)
        p.to(x+width, y+height)
        p.to(x, y+height)
        self.stream.write('\t<path class="b" d="%s" fill="%s"/>\n'%(p, color))

        p=Path()
        p.to(x+width, y)
        p.to(x+width+6, y-3)
        p.to(x+width+6, y-3+height)
        p.to(x+width, y+height)
        self.stream.write('\t<path class="s" d="%s"/>\n'%p)

        p=Path()
        p.setClosed(False)
        p.to(x, y)
        p.to(x+width, y)
        self.stream.write('\t<path class="h" d="%s"/>\n'%p)

        if label:
            self.renderLabel(x, y, width, label)
        self.stream.write('</g>\n')


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
.bar .b {stroke-width: 1px; stroke: black}
.bar .s {stroke: none; fill: black; fill-opacity: 0.3}
.bar .h {fill: none; stroke: white; stroke-opacity: 0.4}
.tit {font-weight: bold; font-size: 12px}
"""%(self.width, self.height))
        stream.write("""]]></style>       """)

    def svgFooter(self, stream):
        stream.write("</svg>")

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

                col=self.colors.getColor(r, c)
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
    def __init__(self, table, colors=DefaultColorScheme(), width=630, height=300):
        Graph.__init__(self, table, width=width, height=height)
        self.chart=AbstractBarChart(table, colors, width-25, 159)

    def render(self, stream):
        #self.barrenderer=BarRenderer3D(stream)
        self.barrenderer=BasicBarRenderer(stream)
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
            self.renderBar(stream, bar)

        for label in self.chart.getLabels():
            self.renderLabel(stream, label)

        legend=self.chart.getLegend()
        for r, l in enumerate(legend):
            stream.write('<g class="legend" transform="translate(%0.1f, %0.1f)">\n'%(5.5, self.height-19.5-20*(len(legend)-r-1)))
            self.barrenderer.renderBar(0, 0, 15, 15, l.color)
            stream.write('\t<text x="%0.1f" y="%0.1f">%s</text>\n'%(23, 8, l.label_xml()))
            stream.write('</g>\n')

    def renderBar(self, stream, bar):
        y=159.5-bar.h
        self.barrenderer.renderBar(bar.x+9.5, y, bar.w, bar.h, bar.color, bar.label_xml())

    def renderLabel(self, stream, label):
        stream.write('<text class="label" text-anchor="end" transform="translate(%.2f, %.2f) rotate(270)">%s</text>\n'%(label.x+7+9.5, 164.5, label.label_xml()))


class PieChart(Graph):
    def __init__(self, table, cx=250, cy=130.5, rx=100, ry=100, value_labels=True, colors=DefaultColorScheme(), width=625, height=300):
        Graph.__init__(self, table.asFracOfRow(), width=width, height=height)
        self.colors=colors
        self.cx=cx
        self.cy=cy
        self.rx=rx
        self.ry=ry
        self.value_labels=value_labels

    def render(self, stream):
        self.svgHeader(stream)
        rs=self.table.rows
        self.rx=self.ry=int(100/rs)
        for r in xrange(rs):
            self.angle=0
            self.cx=int((2*r+1)*self.width/(2*rs))+0.5
            svals=self.table.getRow(r)
            svals=zip(range(0,len(svals)),svals)
            svals.sort(lambda x,y:cmp(float(x[1]),float(y[1])))
            for i in xrange(len(svals)):
                slice=float(svals[i][1])*2*math.pi
                if slice < 0.005:
                    continue
                if float(svals[i][1]) == 1.0:
                    slice=1.9999*math.pi #prevent rendering glitch in Firefox SVG
                self.renderPie(stream, slice, svals[i][0], svals[i][1])
                self.angle+=slice
            label=self.table.getRowLabel(r)
            if label:
                stream.write('<text class="tit" x="%d" y="%d" text-anchor="middle">%s</text>'%(self.cx, self.cy+self.ry+35, xmlentities(label)))
        self.svgFooter(stream)

    def renderLabel(self, stream, slice, index, val):
        tang=self.angle+slice/2
        if tang < math.pi/2:
            tpos='start'
        elif tang < 3*math.pi/2:
            tpos='end'
        else:
            tpos='start'

        if self.value_labels:
            label=xmlentities(self.table.getColumnLabel(index)+" (%s)"%str(val))
        else:
            label=xmlentities(self.table.getColumnLabel(index))

        stream.write('<text x="%f" y="%f" font-size="10" text-anchor="%s">%s</text>'%(self.cx+(self.rx+10)*math.cos(tang), self.cy+(self.ry+10)*math.sin(tang), tpos, label))

    def renderPie(self, stream, slice, index, val):
        stream.write('<g>')
        stream.write('<path d="M %f,%f L %f,%f A %d,%d 0 %d,1 %f %f Z" stroke="black" stroke-width="1" fill="%s"/>'%(self.cx, self.cy, self.cx+self.rx*math.cos(self.angle), self.cy+self.ry*math.sin(self.angle), self.rx, self.ry, slice > math.pi, self.cx+self.rx*math.cos(self.angle+slice), self.cy+self.ry*math.sin(self.angle+slice), self.colors[index]))
        self.renderLabel(stream, slice, index, val)
        stream.write('</g>')

class SplitBarGraph(Graph):
    def __init__(self, table):
        Graph.__init__(self, table.asFracOfRow())
        self.colors=DefaultColorScheme()
        self.barheight=20
        self.barspacing=int((self.height-10)/(self.table.rows))-(self.barheight)
        self.labelspace=200

    def render(self, stream):
        self.barrenderer=BarRenderer3D(stream)
        self.svgHeader(stream)
        for r in xrange(self.table.rows):
            self.renderRow(stream, r)
        self.svgFooter(stream)

    def renderRow(self, stream, r):
        x=self.labelspace+10
        stream.write('<g transform="translate(5.5, %0.1f)">'%(5.5+r*self.barheight+(r+1)*self.barspacing))
        stream.write('<text x="%0.1f" y="%0.1f">%s</text>'%(0, 10, xmlentities(self.table.getRowLabel(r))))
        for c in xrange(self.table.cols):
            val=self.table.getValue(c, r)
            if float(val) < 0.005:
                continue
            w=float(val)*(self.width-self.labelspace-22)
            #self.barrenderer.renderBar(x, 0, w, self.barheight, self.colors[c], '%s (%s)'%(xmlentities(self.table.getColumnLabel(c)),str(val)))
            self.barrenderer.renderBar(x, 0, w, self.barheight, self.colors[c])
            stream.write('<text text-anchor="middle" transform="translate(%0.1f -17)"><tspan x="0">%s</tspan><tspan x="0" dy="12">(%s)</tspan></text>\n'%(x+w/2, xmlentities(self.table.getColumnLabel(c)), str(val)))
            x+=w
        stream.write('</g>\n')

class LineGraph(Graph):
    def __init__(self, table):
        Graph.__init__(self, table)
        self.colors=DefaultColorScheme()
        self.colwidth=(self.width-20)/(self.table.cols-1)

    def render(self, stream):
        self.svgHeader(stream)
        for r in xrange(self.table.rows):
            self.renderRow(stream, r)
        self.renderAxes(stream)
        if self.table.rows > 1:
            self.renderLegend(stream)
        self.svgFooter(stream)

    def renderAxes(self, stream):
        p=Path()
        p.to(9.5, 0)
        p.to(9.5, 159.5)
        p.to(self.width, 159.5)
        p.setClosed(False)
        stream.write('<path d="%s" stroke="black" stroke-width="1" fill="none"/>\n'%p)
        stream.write('<text text-anchor="end" transform="translate(14.5, 164.5) rotate(270)">%s</text>'%xmlentities(self.table.getColumnLabel(0)))
        stream.write('<text text-anchor="end" transform="translate(%.2f, %.2f) rotate(270)">%s</text>'%(14.5+self.colwidth*(self.table.cols-1), 164.5, xmlentities(self.table.getColumnLabel(self.table.cols-1))))

    def renderLegend(self, stream):
        for r in xrange(self.table.rows):
            stream.write('<g transform="translate(%0.1f, %0.1f)">'%(5.5, 280.5-20*(self.table.rows-r-1)))
            stream.write('<path d="M 0,5 L 15, 5" stroke="%s" stroke-width="2"/>'%self.colors[r])
            stream.write('<text x="%0.1f" y="%0.1f">%s</text>'%(23, 8, xmlentities(self.table.getRowLabel(r))))
            stream.write('</g>')

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
            stream.write('<circle cx="%.1f" cy="%.1f" r="2" stroke="%s"/>\n'%(x,y,self.colors[r]))
            p.to(x, y)
        p.setClosed(False)
        stream.write('<path d="%s" stroke="%s" stroke-width="2" fill="none"/>\n'%(p, self.colors[r]))
        if cmax != None:
            v=self.table.getValue(cmax, r)
            stream.write('<text x="%0.1f" y="%0.1f" text-anchor="middle" style="fill: %s">%s</text>'%(9.5+self.colwidth*cmax, 149.5-float(v)*130, self.colors[r], str(v)))

class InterpolatingLineGraph(LineGraph):
    def __init__(self, table):
        LineGraph.__init__(self, table)

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
        for c in p.coords:
            x,y=c
            stream.write('<circle cx="%.1f" cy="%.1f" r="2" fill="%s"/>\n'%(x,y, self.colors[r]))
        stream.write('<path d="%s" stroke="%s" stroke-width="2" fill="none"/>\n'%(p.toStringQuadratic(), self.colors[r]))
        if cmax != None:
            v=self.table.getValue(cmax, r)
            stream.write('<text x="%0.1f" y="%0.1f" text-anchor="middle" style="fill: %s">%s</text>'%(9.5+self.colwidth*cmax, 149.5-float(v)*130, self.colors[r], str(v)))


import os
import popen2
import select

class GraphRasterizer(object):
    def __init__(self, graph):
        self.graph=graph

    def asPNG(self):
        return self.__rasterize('image/png', '.png')

    def asJPEG(self):
        return self.__rasterize('image/jpeg', '.jpg')

    def __rasterize(self, mimetype, ext):
        tmpfile=os.tempnam()
        f=open(tmpfile, 'w')
        self.graph.render(f)
        f.close()

        outtmpfile=tmpfile+ext

        proc=popen2.Popen4('/usr/bin/rasterizer -scriptSecurityOff -m %s %s'%(mimetype, tmpfile))
        self.graph.render(proc.tochild)
        proc.tochild.close()
        out=''
        while proc.poll() == -1:
            i, o, s=select.select([proc.fromchild], [], [], 100)
            if proc.fromchild in i:
                out+=proc.fromchild.read()

        out+=proc.fromchild.read()

        try:
            f=open(outtmpfile, 'rb')
            image=f.read()
            f.close()
        except IOError:
            return out

        os.unlink(tmpfile)
        os.unlink(outtmpfile)
        return image
