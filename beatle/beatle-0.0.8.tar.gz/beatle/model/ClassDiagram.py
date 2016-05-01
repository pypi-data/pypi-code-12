# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import wx
from math import sqrt
from ctx import theContext as context
import model
import app.resources as rc
import tran
import copy

NO_WHERE = 0
IN_CLASS = 1
IN_INHERIT = 2
IN_AGGREG = 3
IN_NOTE = 4
IN_LINE = 5
IN_LINE_MARK = 7
IN_SHAPE = 6


def RectCorners(r):
    """Obtiene los vertices en orden SE NE NW SW"""
    (x, y, w, h) = r.Get()
    p0 = wx.Point(x, y)
    p1 = wx.Point(x, y + h)
    p2 = wx.Point(x + w, y + h)
    p3 = wx.Point(x + w, y)
    return (p0, p1, p2, p3)


def RectSides(r):
    """Obtiene los lados de un rectangulo en orden RLBT"""
    (p0, p1, p2, p3) = RectCorners(r)
    return ([p2, p3], [p0, p1], [p1, p2], [p0, p3])


def RectMiddles(r):
    """Obtiene los puntos centrales de cara de un rectangulo en orden RLBT"""
    return [wx.Point((a.x + b.x) // 2,
        (a.y + b.y) // 2) for [a, b] in RectSides(r)]


def dot2(v1, v2):
    """Obtiene el producto escalar de dos vectores"""
    return (float(v1.x) * float(v2.x)) + (float(v1.y) * float(v2.y))


def norm(v):
    """obtiene la norma de un vector"""
    return sqrt(dot2(v, v))


def vfact(v, a):
    """multiplica un vector por un escalar"""
    x = float(v.x) * a
    y = float(v.y) * a
    return wx.Point(int(x), int(y))


def NearPoint(r, p):
    """Obtiene el punto mas proximo a p en el borde del rectangulo r
    y el indice de cara en orden RLBT"""
    c = RectSides(r)
    # print "RectSides:\n"
    # for side in c:
    #    print("[({x0},{y0}),({x1},{y1})]\n".format(
    #        x0=str(side[0].x), y0=str(side[0].y),
    #        x1=str(side[1].x), y1=str(side[1].y)))
    d2 = None
    ir = None
    m2 = None
    for i in range(4):
        segment = c[i]
        # los puntos de la recta son de la forma q(a) = c[0] + a*(c[1]-c[0])
        # el punto mas proximo es aquel para que (p-q(a))*(c[1]-c[0]) = 0, de
        # donde
        # (p-c[0])*(c[1]-c[0]) = a*||c[0]-c[1]||²  Si a esta en el rango
        # [0, 1], la solucion esta en [c[0],c[1]]. En caso contrario, el
        # extremo mas proximo será c[0] si a<0 o c[1] si a>1
        director = segment[1] - segment[0]
        m = dot2(director, director)
        a = dot2(p - segment[0], director) / m
        if a <= 0:
            u = p - segment[0]
            s = dot2(u, u)
            if d2 is None or d2 > s or (d2 == s and m < m2):
                # si la distancia es la primera o es menor que la
                # anteriormente determinada o es igual, pero el lado es
                # mas pequeño ...
                d2 = s
                ir = i
                m2 = m
                point = segment[0]
            continue
        elif a >= 1:
            u = p - segment[1]
            s = dot2(u, u)
            if d2 is None or d2 > s or (d2 == s and m < m2):
                # si la distancia es la primera o es menor que la
                # anteriormente determinada o es igual, pero el lado es
                # mas pequeño ...
                d2 = s
                ir = i
                m2 = m
                point = segment[1]
            continue
        else:
            q = segment[0] + vfact(director, a)
            u = p - q
            s = dot2(u, u)
            if d2 is None or d2 > s or (d2 == s and m < m2):
                # si la distancia es la primera o es menor que la
                # anteriormente determinada o es igual, pero el lado es
                # mas pequeño ...
                d2 = s
                ir = i
                m2 = m
                point = q
            continue
    return ir, point


class DiagramElement(object):
    """Base class for diagram elements"""
    def __init__(self, obj, pos):
        """Initialization"""
        super(DiagramElement, self).__init__()
        self._obj = obj
        self._pos = wx.Point(0, 0)
        if pos is not None:
            self._pos = wx.Point(pos.x, pos.y)
        self._selected = False

    @property
    def object(self):
        """Return the referent object"""
        return self._obj

    def Draw(self, ctx):
        """Draw element"""
        pass

    def HitTest(self, pos):
        """Check about element near pos"""
        return (None, NO_WHERE)

    def Select(self, value=True):
        """Set selected state"""
        self._selected = value

    def Selected(self):
        """Get selected state"""
        return self._selected

    def ToggleSelected(self):
        """Toggle selected state"""
        self._selected = not self._selected

    def Erase(self, dc):
        """Delete element"""
        pass

    def Remove(self, diag):
        """Remove element from class diagram"""
        pass

    def Shift(self, shift):
        """Displaces elements"""
        self._pos += shift


class ClosedShape(DiagramElement):
    """Represents a closed shape"""
    def __init__(self, obj, pos):
        """Initialization"""
        super(ClosedShape, self).__init__(obj, pos)
        self.Layout()
        self._rgn = self.Region()

    def __getstate__(self):
        """Get pickle context"""
        state = dict(self.__dict__)
        if '_rgn' in state:
            del state['_rgn']
        return state

    def __setstate__(self, state):
        """Set pickle context"""
        for attr in state:
            setattr(self, attr, state[attr])
        self._rgn = self.Region()

    def Layout(self):
        """Initialize geometrical properties"""
        pass

    def Shift(self, shift):
        """Displaces element"""
        super(ClosedShape, self).Shift(shift)
        self._rgn.Offset(shift.x, shift.y)

    def HitTest(self, pos):
        """Check about element near pos"""
        if self._rgn.ContainsPoint(pos) == wx.InRegion:
            return (self, IN_SHAPE)
        else:
            return (None, NO_WHERE)


class RectShape(ClosedShape):
    """Represents a rect, closed shape"""
    def __init__(self, obj, pos, **karg):
        """"""
        super(RectShape, self).__init__(obj, pos)
        if 'size' in karg:
            self._rectSize = karg['size']
        else:
            self._rectSize = None
        self.Layout()

    def Rect(self):
        """"""
        return wx.Rect(self._pos.x, self._pos.y,
            self._rectSize.x, self._rectSize.y)

    def RectSize(self):
        """Get rectangle"""
        return self._rectSize

    def Region(self):
        """Gets the class region"""
        return wx.Region(self._pos.x, self._pos.y,
            self._rectSize.x, self._rectSize.y)

    def HitTest(self, pos):
        """Check about element near pos"""
        r = wx.RectPS(self._pos, self._rectSize)
        if r.Contains(pos):
            return (self, IN_SHAPE)
        return (None, NO_WHERE)


class NoteElement(RectShape):
    """Represents a text note in diagram"""
    def __init__(self, obj, pos):
        """Initialization"""
        # in order to ensure correct class initialization we need to
        # first define the members, prior to super call
        super(NoteElement, self).__init__(obj, pos)

    def Layout(self):
        """Update some properties"""
        self._rectSize = wx.Size(0, 0)
        dc = wx.ScreenDC()
        (width, height) = dc.GetTextExtent(self._obj.note)
        self._textSize = wx.Size(width, height)
        rectSize = wx.Size(width + 45 - (width % 5), height + 25 - (height % 5))
        if not hasattr(self, '_rectSize'):
            self._rectSize = rectSize
        else:
            if rectSize.x > self._rectSize.x:
                self._rectSize.x = rectSize.x
            if rectSize.y > self._rectSize.y:
                self._rectSize.y = rectSize.y
        self._xOffset = (self._rectSize.x - width) // 2
        self._yOffset = (self._rectSize.y - height) // 2

    def Draw(self, dc):
        """Draw class element"""
        dc.SetLogicalFunction(wx.COPY)
        pen = wx.GREY_PEN
        if self.Selected():
            brush = wx.Brush(wx.TheColourDatabase.Find('GOLDENROD'))
        else:
            brush = wx.Brush(wx.TheColourDatabase.Find('THISTLE'))
        dc.SetPen(pen)
        dc.SetBrush(brush)
        if self.Selected():
            dc.DrawRectanglePointSize(self._pos, self._rectSize)
        else:
            dc.DrawRectanglePointSize(self._pos, self._rectSize)
        dc.DrawText(self._obj.note, self._pos.x +
            self._xOffset, self._pos.y + self._yOffset)

    def Erase(self, dc):
        """Erase element"""
        dc.SetLogicalFunction(wx.COPY)
        dc.SetPen(wx.WHITE_PEN)
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.DrawRectanglePointSize(self._pos, self._rectSize)

    def Remove(self, diag):
        """Remove element from class diagram"""
        pass


class ClassElement(RectShape):
    """Represents a class in diagram"""
    def __init__(self, obj, pos):
        """Initialization"""
        # in order to ensure correct class initialization we need to
        # first define the members, prior to super call
        self._ancestors = []
        self._derivatives = []
        self._fromRelation = []
        self._toRelation = []
        super(ClassElement, self).__init__(obj, pos)

    @property
    def label(self):
        """Return the label of the element"""
        return self._obj.label

    def Layout(self):
        """Update some properties"""
        self._rectSize = wx.Size(0, 0)
        dc = wx.ScreenDC()
        (width, height) = dc.GetTextExtent(self.label)
        self._textSize = wx.Size(width, height)
        rectSize = wx.Size(width + 45 - (width % 5), height + 25 - (height % 5))
        sizeChange = False
        if not hasattr(self, '_rectSize'):
            self._rectSize = rectSize
            sizeChange = True
        else:
            if rectSize.x > self._rectSize.x:
                self._rectSize.x = rectSize.x
                sizeChange = True
            if rectSize.y > self._rectSize.y:
                self._rectSize.y = rectSize.y
                sizeChange = True
        self._xOffset = (self._rectSize.x - width) // 2
        self._yOffset = (self._rectSize.y - height) // 2
        if sizeChange:
            # se han de redimensionar las relaciones
            for inh in self._ancestors:
                inh.Initialize()
            for inh in self._derivatives:
                inh.Initialize()
            for rel in self._fromRelation:
                rel.Initialize()
            for rel in self._toRelation:
                rel.Initialize()

    def Draw(self, dc):
        """Draw class element"""
        dc.SetLogicalFunction(wx.COPY)
        pen = wx.GREY_PEN
        if self.Selected():
            brush = wx.Brush(wx.TheColourDatabase.Find('GOLDENROD'))
        else:
            brush = wx.Brush(wx.TheColourDatabase.Find('AQUAMARINE'))
        dc.SetPen(pen)
        dc.SetBrush(brush)
        if self.Selected():
            dc.DrawRectanglePointSize(self._pos, self._rectSize)
        else:
            dc.DrawRectanglePointSize(self._pos, self._rectSize)
        dc.DrawText(self.label, self._pos.x +
            self._xOffset, self._pos.y + self._yOffset)

    def Erase(self, dc):
        """Erase element"""
        dc.SetLogicalFunction(wx.COPY)
        dc.SetPen(wx.WHITE_PEN)
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.DrawRectanglePointSize(self._pos, self._rectSize)
        for e in self._ancestors:
            e.Erase(dc)
        for e in self._derivatives:
            e.Erase(dc)

    def Remove(self, diag):
        """Remove element from class diagram"""
        k = copy.copy(self._ancestors)
        for inh in k:
            diag.RemoveElement(inh)
        k = copy.copy(self._derivatives)
        for inh in k:
            diag.RemoveElement(inh)
        k = copy.copy(self._fromRelation)
        for rel in k:
            diag.RemoveElement(rel)
        k = copy.copy(self._fromRelation)
        for rel in k:
            diag.RemoveElement(rel)


class ConnectorSegment(object):
    """Represents a segment"""
    def __init__(self, start, end):
        """Initialization"""
        self._start = wx.Point(start.x, start.y)
        self._end = wx.Point(end.x, end.y)
        if self._start.x == self._end.x:
            self._orientation = wx.VERTICAL
        else:
            self._orientation = wx.HORIZONTAL
        self._mark = start + end
        self._mark.x //= 2
        self._mark.y //= 2
        self._mark.x -= 3
        self._mark.y -= 3

    def HitTest(self, pos, selected):
        """Check about mouse position"""
        if selected:
            # when selected, markers must selected first
            r = wx.Rect(self._mark.x, self._mark.y, 7, 7)
            if r.Contains(pos):
                return (self, IN_LINE_MARK)
        if self._orientation == wx.HORIZONTAL:
            if (self._start.x - pos.x) * (self._end.x - pos.x) < 0:
                if abs(self._start.y - pos.y) < 4:
                    return (self, IN_LINE)
        else:
            if (self._start.y - pos.y) * (self._end.y - pos.y) < 0:
                if abs(self._start.x - pos.x) < 4:
                    return (self, IN_LINE)
        return (None, NO_WHERE)

    def Draw(self, dc):
        """Draw element"""
        dc.DrawLine(self._start.x, self._start.y, self._end.x, self._end.y)

    def DrawMark(self, dc):
        """Draw selected marks"""
        sz = wx.Size(7, 7)
        dc.DrawRectanglePointSize(self._mark, sz)

    def Shift(self, shift):
        """Shift position"""
        self._start += shift
        self._end += shift
        self._mark += shift


class ConnectorStartSegment(ConnectorSegment):
    """Represents an start segment"""
    def __init__(self, start, end):
        """Initialization"""
        super(ConnectorStartSegment, self).__init__(start, end)
        if self._orientation is wx.HORIZONTAL:
            self._mark.x = self._start.x - 3
        else:
            self._mark.y = self._start.y - 3
        self._touch = False


class ArrowStartSegment(ConnectorStartSegment):
    """Represents an start arrow"""
    def __init__(self, start, end):
        """Initialization"""
        super(ArrowStartSegment, self).__init__(start, end)

    def Draw(self, dc):
        """Draw element"""
        p = self._start
        if self._orientation is wx.HORIZONTAL:
            if p.x > self._end.x:
                q = wx.Point(p.x - 10, p.y - 5)
                r = wx.Point(p.x - 10, p.y + 5)
            else:
                q = wx.Point(p.x + 10, p.y - 5)
                r = wx.Point(p.x + 10, p.y + 5)
        elif self._orientation is wx.VERTICAL:
            if p.y > self._end.y:
                q = wx.Point(p.x - 5, p.y - 10)
                r = wx.Point(p.x + 5, p.y - 10)
            else:
                q = wx.Point(p.x - 5, p.y + 10)
                r = wx.Point(p.x + 5, p.y + 10)
        else:
            return
        self._points = [p, q, p, r, p, self._end]
        dc.DrawLines(self._points)


class LanceStartSegment(ConnectorStartSegment):
    """Represents an lance"""
    def __init__(self, start, end):
        """Initialization"""
        super(LanceStartSegment, self).__init__(start, end)

    def Draw(self, dc):
        """Draw element"""
        p = self._start
        if self._orientation is wx.HORIZONTAL:
            if p.x > self._end.x:
                q = wx.Point(p.x - 10, p.y - 5)
                r = wx.Point(p.x - 10, p.y + 5)
                s = wx.Point(p.x - 10, p.y)
            else:
                q = wx.Point(p.x + 10, p.y - 5)
                r = wx.Point(p.x + 10, p.y + 5)
                s = wx.Point(p.x + 10, p.y)
        elif self._orientation is wx.VERTICAL:
            if p.y > self._end.y:
                q = wx.Point(p.x - 5, p.y - 10)
                r = wx.Point(p.x + 5, p.y - 10)
                s = wx.Point(p.x, p.y - 10)
            else:
                q = wx.Point(p.x - 5, p.y + 10)
                r = wx.Point(p.x + 5, p.y + 10)
                s = wx.Point(p.x, p.y + 10)
        else:
            return
        self._points = [p, q, s, self._end, s, r, p]
        dc.DrawLines(self._points)


class DiamondStartSegment(ConnectorStartSegment):
    """Represents an diamod <>"""
    def __init__(self, start, end):
        """Initialization"""
        super(DiamondStartSegment, self).__init__(start, end)

    def Draw(self, dc):
        """Draw element"""
        p = self._start
        if self._orientation is wx.HORIZONTAL:
            if p.x > self._end.x:
                q = wx.Point(p.x - 10, p.y - 5)
                r = wx.Point(p.x - 10, p.y + 5)
                s = wx.Point(p.x - 20, p.y)
            else:
                q = wx.Point(p.x + 10, p.y - 5)
                r = wx.Point(p.x + 10, p.y + 5)
                s = wx.Point(p.x + 20, p.y)
        elif self._orientation is wx.VERTICAL:
            if p.y > self._end.y:
                q = wx.Point(p.x - 5, p.y - 10)
                r = wx.Point(p.x + 5, p.y - 10)
                s = wx.Point(p.x, p.y - 20)
            else:
                q = wx.Point(p.x - 5, p.y + 10)
                r = wx.Point(p.x + 5, p.y + 10)
                s = wx.Point(p.x, p.y + 20)
        else:
            return
        self._points = [p, q, s, self._end, s, r, p]
        dc.DrawLines(self._points)


class ConnectorEndSegment(ConnectorSegment):
    """Represents an start segment"""
    def __init__(self, start, end):
        """Initialization"""
        super(ConnectorEndSegment, self).__init__(start, end)
        if self._orientation is wx.HORIZONTAL:
            self._mark.x = self._end.x - 3
        else:
            self._mark.y = self._end.y - 3
        self._touch = False



class ArrowEndSegment(ConnectorEndSegment):
    """Represents an end arrow"""
    def __init__(self, start, end):
        """Initialization"""
        super(ArrowEndSegment, self).__init__(start, end)

    def Draw(self, dc):
        """Draw element"""
        p = self._end
        if self._orientation is wx.HORIZONTAL:
            if p.x > self._start.x:
                q = wx.Point(p.x - 10, p.y - 5)
                r = wx.Point(p.x - 10, p.y + 5)
            else:
                q = wx.Point(p.x + 10, p.y - 5)
                r = wx.Point(p.x + 10, p.y + 5)
        elif self._orientation is wx.VERTICAL:
            if p.y > self._start.y:
                q = wx.Point(p.x - 5, p.y - 10)
                r = wx.Point(p.x + 5, p.y - 10)
            else:
                q = wx.Point(p.x - 5, p.y + 10)
                r = wx.Point(p.x + 5, p.y + 10)
        else:
            return
        self._points = [p, q, p, r, p, self._start]
        dc.DrawLines(self._points)


class LanceEndSegment(ConnectorEndSegment):
    """Represents an lance"""
    def __init__(self, start, end):
        """Initializes lance"""
        super(LanceEndSegment, self).__init__(start, end)

    def Draw(self, dc):
        """Draw element"""
        p = self._end
        if self._orientation is wx.HORIZONTAL:
            if p.x > self._start.x:
                q = wx.Point(p.x - 10, p.y - 5)
                r = wx.Point(p.x - 10, p.y + 5)
            else:
                q = wx.Point(p.x + 10, p.y - 5)
                r = wx.Point(p.x + 10, p.y + 5)
        elif self._orientation is wx.VERTICAL:
            if p.y > self._start.y:
                q = wx.Point(p.x - 5, p.y - 10)
                r = wx.Point(p.x + 5, p.y - 10)
            else:
                q = wx.Point(p.x - 5, p.y + 10)
                r = wx.Point(p.x + 5, p.y + 10)
        else:
            return
        self._points = [p, q, r, self._start, r, p]
        dc.DrawLines(self._points)


class DiamondEndSegment(ConnectorEndSegment):
    """Represents an diamod <>"""
    def __init__(self, start, end):
        """Initialization"""
        super(DiamondEndSegment, self).__init__(start, end)

    def Draw(self, dc):
        """Draw element"""
        p = self._end
        if self._orientation is wx.HORIZONTAL:
            if p.x > self._start.x:
                q = wx.Point(p.x - 10, p.y - 5)
                r = wx.Point(p.x - 10, p.y + 5)
                s = wx.Point(p.x - 20, p.y)
            else:
                q = wx.Point(p.x + 10, p.y - 5)
                r = wx.Point(p.x + 10, p.y + 5)
                s = wx.Point(p.x + 20, p.y)
        elif self._orientation is wx.VERTICAL:
            if p.y > self._end.y:
                q = wx.Point(p.x - 5, p.y - 10)
                r = wx.Point(p.x + 5, p.y - 10)
                s = wx.Point(p.x, p.y - 20)
            else:
                q = wx.Point(p.x - 5, p.y + 10)
                r = wx.Point(p.x + 5, p.y + 10)
                s = wx.Point(p.x, p.y + 20)
        else:
            return
        self._points = [p, q, s, self._start, s, r, p]
        dc.DrawLines(self._points)


class ConectorElement(DiagramElement):
    """Represents a conector between diagram elements"""
    def __init__(self, obj, fromShape, toShape):
        """Initialize a connector element"""
        super(ConectorElement, self).__init__(obj, None)
        self._FROM = fromShape
        self._TO = toShape
        self.segments = []

    def SelectFromClients(self):
        """Select element only if both extrems are selected"""
        self._selected = self._FROM._selected and self._TO._selected

    def DrawLines(self, dc):
        """Draw lines"""
        for segment in self.segments:
            segment.Draw(dc)

    def DrawMarkers(self, dc):
        """Draw track markers"""
        for segment in self.segments:
            segment.DrawMark(dc)

    def RefreshChanges(self):
        """Actualiza los extremos de los segmentos"""
        if len(self.segments) > 1:
            s = self.segments[0]
            e = self.segments[-1]
            self.segments[0] = self.StartSegment(s._start, s._end)
            self.segments[-1] = self.EndSegment(e._start, e._end)

    def StartSegment(self, p0, p1):
        """Create a new start segment"""
        return ConnectorStartSegment(p0, p1)

    def EndSegment(self, p0, p1):
        """Create a new end segment"""
        return ConnectorEndSegment(p0, p1)

    def LineStep(self, p0, p1, orientation=None, start=False, end=False):
        """Create a line step from p0 to p1"""
        sx = p1.x - p0.x
        sy = p1.y - p0.y
        if abs(sx) >= abs(sy) and orientation is not wx.VERTICAL:
            if sx == 0:
                return None
            q = wx.Point(p1.x, p0.y)
        else:
            q = wx.Point(p0.x, p1.y)
        if start is True:
            return self.StartSegment(p0, q)
        elif end is True:
            return self.EndSegment(p0, q)
        else:
            return ConnectorSegment(p0, q)

    def ShiftSegment(self, index, pos):
        """Desplaza el segmento seleccionado"""
        #Lo primero, es determinar de que segmento se trata
        #print("called shift with pos value ({x},{y})".format(
        #    x=str(pos.x), y=str(pos.y)))
        segment = self.segments[index]
        if index == 0:
            # se trata de mover el primer segmento. Para esto,
            # se determina primero el lado mas proximo
            side, point = NearPoint(self._FROM.Rect(), pos)
            #print("NearPoint devuelve cara {cara} posicion ({x},{y})".format(
            #    x=str(point.x), y=str(point.y), cara=str(side)))
            last = self.segments[-1]
            target = last._start
            self.segments = []
            # add first segment
            q = point
            u = side % 4
            if u < 2:
                #change is in x
                qq = wx.Point(q.x +
                (1 - 2 * u) * self.GetStartConnectorSize().x, q.y)
            else:
                #change is in y
                qq = wx.Point(q.x, q.y +
                    (5 - 2 * u) * self.GetStartConnectorSize().y)
            l = self.LineStep(q, qq, start=True)
            l._touch = True
            if l is not None:
                self.segments.append(l)
            q = qq
            while True:
                l = self.LineStep(q, target)
                if l is None:
                    break
                q = l._end
                self.segments.append(l)
            # add last segment
            self.segments.append(last)
            self.JoinExtremes()
            return 0
        elif index == len(self.segments) - 1:
            # ok, en este caso se trata, reciprocamente, del ultimo segmento
            side, point = NearPoint(self._TO.Rect(), pos)
            first = self.segments[0]
            target = first._end
            self.segments = []
            q = point
            u = side % 4
            if u < 2:
                #change is in x
                qq = wx.Point(q.x +
                (1 - 2 * u) * self.GetEndConnectorSize().x, q.y)
            else:
                #change is in y
                qq = wx.Point(q.x, q.y +
                    (5 - 2 * u) * self.GetEndConnectorSize().y)
            l = self.LineStep(qq, q, end=True)
            l._touch = True
            q = qq
            if l is not None:
                self.segments.append(l)
            while True:
                l = self.LineStep(q, target)
                if l is None:
                    break
                q = l._end
                l._end = l._start
                l._start = q
                self.segments.insert(0, l)
            # add last segment
            self.segments.insert(0, first)
            self.JoinExtremes()
            return len(self.segments) - 1
        else:
            #se trata de mover un segmento del medio. En este caso,
            #la simple orientacion determina que es lo que se mueve
            if segment._orientation is wx.HORIZONTAL:
                segment._start.y = pos.y
                segment._end.y = pos.y
                segment._mark.y = pos.y - 3
                self.segments[index - 1]._end.y = pos.y
                if index > 1:
                    self.segments[index - 1]._mark.y = (
                        self.segments[index - 1]._end.y +
                        self.segments[index - 1]._start.y) // 2
                self.segments[index + 1]._start.y = pos.y
                if index < len(self.segments) - 2:
                    self.segments[index + 1]._mark.y = (
                        self.segments[index + 1]._end.y +
                        self.segments[index + 1]._start.y) // 2
            else:
                segment._start.x = pos.x
                segment._end.x = pos.x
                segment._mark.x = pos.x - 3
                self.segments[index - 1]._end.x = pos.x
                if index > 1:
                    self.segments[index - 1]._mark.x = (
                        self.segments[index - 1]._end.x +
                        self.segments[index - 1]._start.x) // 2
                self.segments[index + 1]._start.x = pos.x
                if index < len(self.segments) - 2:
                    self.segments[index + 1]._mark.x = (
                        self.segments[index + 1]._end.x +
                        self.segments[index + 1]._start.x) // 2
            return index

    def GetEndConnectorSize(self):
        """Return the connector size"""
        return wx.Size(20, 20)

    def GetStartConnectorSize(self):
        """Return the connector size"""
        return wx.Size(20, 20)

    def GetSidePositions(self, p, size):
        """Obtiene los puntos centrales de los lados de un cuadrado
        centrado en el punto p"""
        p0 = wx.Point(p.x + size.x, p.y)
        p1 = wx.Point(p.x - size.x, p.y)
        p2 = wx.Point(p.x, p.y + size.y)
        p3 = wx.Point(p.x, p.y - size.y)
        return [p0, p1, p2, p3]

    def JoinExtremes(self):
        """Revisa los extremos, y elimina segmentos adyacentes que solo
        son prolongaciones"""
        l = len(self.segments) - 2
        if l > 0:
            if self.segments[0]._orientation == self.segments[1]._orientation:
                self.segments[0]._end = self.segments[1]._end
                self.segments.pop(1)
                l = l - 1
        if l > 0:
            z = l + 1
            if self.segments[l]._orientation == self.segments[z]._orientation:
                self.segments[z]._start = self.segments[l]._start
                self.segments.pop(l)

    def Initialize(self):
        """Create initial lines"""
        # decide sides
        sz = self.GetStartConnectorSize()
        starts = RectMiddles(self._FROM.Rect().Inflate(sz.x, sz.y))
        sz = self.GetEndConnectorSize()
        ends = RectMiddles(self._TO.Rect().Inflate(sz.x, sz.y))
        # find best distance
        d2m = None
        si = 0
        # if the start segment or the end segment already exist
        # and is touched, respect it
        stouch = False
        etouch = False
        if len(self.segments):
            if self.segments[0]._touch:
                start = self.segments[0]
                starts = [start._start] * 4
                stouch = True
            if self.segments[-1]._touch:
                end = self.segments[-1]
                ends = [end._end] * 4
                etouch = True
        for i in range(0, 16):
            p = starts[i % 4]
            q = ends[i // 4]
            d2x = p.x - q.x
            d2y = p.y - q.y
            d2 = (d2x * d2x) + (d2y * d2y)
            if d2m is None or d2 < d2m:
                d2m = d2
                bestFrom = p
                bestTo = q
                si = i
        self.segments = []
        # add first segment
        if stouch:
            l = start
            bestFrom = start._end
        else:
            q = bestFrom
            u = si % 4
            if u < 2:
                #change is in x
                q = wx.Point(q.x +
                    (2 * u - 1) * self.GetStartConnectorSize().x, q.y)
            else:
                #change is in y
                q = wx.Point(q.x, q.y +
                    (2 * u - 5) * self.GetStartConnectorSize().y)
            l = self.LineStep(q, bestFrom, start=True)
        if l is not None:
            self.segments.append(l)
        q = bestFrom
        if etouch:
            bestTo = end._start

        while True:
            l = self.LineStep(q, bestTo)
            if l is None:
                break
            q = l._end
            self.segments.append(l)
        # add last line
        if etouch:
            l = end
        else:
            q = bestTo
            u = si // 4

            if u < 2:
                #change is in x
                q = wx.Point(q.x +
                    (2 * u - 1) * self.GetEndConnectorSize().x, q.y)
            else:
                #change is in y
                q = wx.Point(q.x, q.y +
                    (2 * u - 5) * self.GetEndConnectorSize().y)
            l = self.LineStep(bestTo, q, end=True)
        if l is not None:
            self.segments.append(l)

        # After create the segments, the last step is check
        # for join extremes with adjacent segments
        self.JoinExtremes()

        # The connector position is only used as reference
        # when moving mores selected objects so this value
        # can change without special meaning. This method
        # seems a good place to reset it and ensure that
        # dont goes to infinity
        self._pos = wx.Point(0, 0)
        return True

    def SelectedPen(self):
        """Returns the selected pen"""
        return wx.RED_PEN

    def DefaultPen(self):
        """Returns the default pen for use when no selected"""
        return wx.BLACK_PEN

    def Draw(self, dc):
        """Draw class element"""
        dc.SetLogicalFunction(wx.COPY)
        if self._selected:
            pen = self.SelectedPen()
        else:
            pen = self.DefaultPen()
        dc.SetPen(pen)
        self.DrawLines(dc)
        if self._selected:
            self.DrawMarkers(dc)

    def Erase(self, dc):
        """Draw class element"""
        dc.SetLogicalFunction(wx.COPY)
        pen = wx.Pen(wx.WHITE)
        pen.SetWidth(2)
        dc.SetPen(pen)
        self.DrawLines(dc)
        self.DrawMarkers(dc)

    def HitTest(self, pos):
        """Check about element near pos"""
        for p in self.segments:
            (a, where) = p.HitTest(pos, self._selected)
            if where is not NO_WHERE:
                return ((self, p), where)
            #if p._orientation == wx.HORIZONTAL:
            #    if (p._start.x - pos.x) * (p._end.x - pos.x) < 0:
            #        if abs(p._start.y - pos.y) < 2:
            #            return (self, IN_LINE)
            #else:
            #    if (p._start.y - pos.y) * (p._end.y - pos.y) < 0:
            #        if abs(p._start.x - pos.x) < 2:
            #            return (self, IN_LINE)
        return (None, NO_WHERE)

    def Shift(self, shift):
        """Displaces elements"""
        super(ConectorElement, self).Shift(shift)
        for segment in self.segments:
            segment.Shift(shift)


class RelationElement(ConectorElement):
    """Represents a relationship in diagram"""
    def __init__(self, obj, fromShape, toShape):
        """Initialization"""
        super(RelationElement, self).__init__(obj, fromShape, toShape)
        self.Initialize()

    def EndSegment(self, p0, p1):
        """Get end segment"""
        return ArrowEndSegment(p0, p1)

    def StartSegment(self, p0, p1):
        """Get initial segment"""
        if self._obj._FROM._minCardinal is None:
            return super(RelationElement, self).StartSegment(p0, p1)
        if self._obj._FROM._minCardinal == 0:
            return super(RelationElement, self).StartSegment(p0, p1)
        return DiamondStartSegment(p0, p1)

    def GetStartConnectorSize(self):
        """Return the connector size"""
        return wx.Size(20, 20)

    def Remove(self, diag):
        """Remove element from diagram"""
        self._FROM._toRelation.remove(self)
        self._TO._fromRelation.remove(self)

    def Draw(self, dc):
        """Do draw"""
        super(RelationElement, self).Draw(dc)

    def SelectedPen(self):
        """return the selected pen"""
        pen = wx.Pen(wx.RED)
        if self._obj._global:
            pen.SetWidth(2)
        else:
            pen.SetWidth(1)
        return pen

    def DefaultPen(self):
        """return the default pen"""
        if self._obj._critical:
            pen = wx.Pen(wx.RED)
        else:
            pen = wx.Pen(wx.BLACK)
        if self._obj._global:
            pen.SetWidth(2)
        else:
            pen.SetWidth(1)
        return pen


class InheritanceElement(ConectorElement):
    """Represents a inheritance in diagram"""
    def __init__(self, obj, fromShape, toShape):
        """Initialization"""
        super(InheritanceElement, self).__init__(obj, fromShape, toShape)
        self.Initialize()

    def StartSegment(self, p0, p1):
        """Initialize segment"""
        return LanceStartSegment(p0, p1)

    def GetStartConnectorSize(self):
        """Return the connector size"""
        return wx.Size(20, 20)

    def Remove(self, diag):
        """Remove element from diagram"""
        self._FROM._derivatives.remove(self)
        self._TO._ancestors.remove(self)

    def Shift(self, shift):
        """Displaces elements"""
        super(InheritanceElement, self).Shift(shift)

    def DefaultPen(self):
        """Return default pen"""
        return wx.Pen(wx.BLUE)


class ClassDiagram(model.TComponent):
    """Implements a class diagram. This is the descriptor for the
    shapes and placements of the diagram."""

    @tran.TransactionalMethod('move class diagram {}')
    def drop(self, to):
        """Drops class diagram inside project, class or folder """
        target = to.inner_diagram_container
        if not target or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        self._elements = kwargs.get('elements', [])
        self._zoom = kwargs.get('zoom', 1.0)
        # A4 300 dpi default size
        self._width = kwargs.get('width', 2480)
        self._height = kwargs.get('height', 3508)
        self._pane = None
        super(ClassDiagram, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['elements'] = self._elements
        kwargs['zoom'] = self._zoom
        kwargs['width'] = self._width
        kwargs['height'] = self._height
        kwargs.update(super(ClassDiagram, self).get_kwargs())
        return kwargs

    def AddClass(self, cls, pos):
        """Add class element"""
        nwelem = ClassElement(cls, pos)
        # add inheritance and derivative links
        self_cls = lambda x: x.inner_class == cls
        inherits = cls(model.cc.Inheritance, filter=self_cls, cut=True)
        for inh in inherits:
            elem = self.FindElement(inh._ancestor)
            if elem is not None:
                self.AddInheritance(inh, elem, nwelem)
        for elem in self._elements:
            if type(elem) is ClassElement:
                inherits = elem._obj(model.cc.Inheritance)
                for inh in inherits:
                    if inh._ancestor == cls:
                        self.AddInheritance(inh, nwelem, elem)
                        break
        # add relation links
        fromRelation = cls(model.cc.RelationFrom, filter=self_cls, cut=True)
        toRelation = cls(model.cc.RelationTo, filter=self_cls, cut=True)
        for rel in fromRelation:
            elem = self.FindElement(rel.GetFrom())
            if elem is not None:
                self.AddRelation(rel._key, elem, nwelem)
        for rel in toRelation:
            elem = self.FindElement(rel.GetTo())
            if elem is not None:
                self.AddRelation(rel._key, nwelem, elem)
        self._elements.append(nwelem)
        return nwelem

    def AddNote(self, obj, pos):
        """Add note element"""
        nwelem = NoteElement(obj, pos)
        self._elements.append(nwelem)
        return nwelem

    def AddInheritance(self, obj, fromShape, toShape):
        """Add inheritance element"""
        elem = InheritanceElement(obj, fromShape, toShape)
        fromShape._derivatives.append(elem)
        toShape._ancestors.append(elem)
        self._elements.append(elem)
        return elem

    def AddRelation(self, obj, fromShape, toShape):
        """Add relationship element"""
        elem = RelationElement(obj, fromShape, toShape)
        fromShape._toRelation.append(elem)
        toShape._fromRelation.append(elem)
        self._elements.append(elem)
        return elem

    def MoveElement(self, element, pos):
        """Move a element"""
        shift = pos - element._pos
        element._pos = pos

        if type(element) is ClassElement:
            for e in element._ancestors:
                e.Shift(shift)
                e.Initialize()
            for e in element._derivatives:
                e.Shift(shift)
                e.Initialize()
            for e in element._fromRelation:
                e.Shift(shift)
                e.Initialize()
            for e in element._toRelation:
                e.Shift(shift)
                e.Initialize()

    def BringToFront(self, element):
        """Move element to front"""
        if element in self._elements:
            self._elements.remove(element)
        self._elements.append(element)

    def RemoveElement(self, element):
        """Remove element from class diagram"""
        element.Remove(self)
        if element in self._elements:
            self._elements.remove(element)

    @property
    def selected_elements(self):
        """Return the list of selected elements"""
        return [x for x in self._elements if x._selected]

    def EraseSelected(self, dc):
        """Clear selected elements draws"""
        for element in self._elements:
            if element._selected:
                element.Erase(dc)
        # Erase inheritances
        for element in self._elements:
            if isinstance(element, ConectorElement):
                if not element._FROM._selected or not element._TO._selected:
                    element.Erase(dc)
                elif not element._selected:
                    element.Erase(dc)

    def ShiftSelected(self, shift):
        """Displace selected elements"""
        # Select inheritances with both extremes selected
        for element in self._elements:
            if isinstance(element, ConectorElement):
                element.SelectFromClients()
        #do shift
        for element in self._elements:
            if element._selected:
                element.Shift(shift)
                if type(element) is ClassElement:
                    for e in element._ancestors:
                        if not e._selected:
                            e.segments[-1].Shift(shift)
                            e.Initialize()
                    for e in element._derivatives:
                        if not e._selected:
                            e.segments[0].Shift(shift)
                            e.Initialize()
                    for e in element._fromRelation:
                        if not e._selected:
                            e.segments[-1].Shift(shift)
                            e.Initialize()
                    for e in element._toRelation:
                        if not e._selected:
                            e.segments[0].Shift(shift)
                            e.Initialize()
        # Update affected connectos
        # for element in self._elements:
        #    if isinstance(element, ConectorElement):
        #        if not element._selected:
        #            element.Initialize()

    def OnUndoRedoChanged(self):
        """Update from app"""
        if hasattr(self, '_pane'):
            # some bug happens here when we undo open project with open panes
            # and redo open
            from activity.models.ui import pane
            if type(self._pane) is not pane.DiagramPane:
                delattr(self, '_pane')
            else:
                book = context.frame.docBook
                index = book.GetPageIndex(self._pane)
                book.SetPageText(index, self.tab_label)
                book.SetPageBitmap(index, self.GetTabBitmap())
                self._pane.Refresh()
        #refresh relations
        for element in self._elements:
            if type(element) is InheritanceElement:
                felem = element._FROM
                telem = element._TO
                if felem not in self._elements or telem not in self._elements:
                    print('detected orphan inheritance in diagram')
                if element not in felem._derivatives:
                    felem._derivatives.append(element)
                if element not in telem._ancestors:
                    telem._ancestors.append(element)
            elif type(element) is RelationElement:
                felem = element._FROM
                telem = element._TO
                if felem not in self._elements or telem not in self._elements:
                    print('detected orphan relationship in diagram')
                if element not in felem._toRelation:
                    felem._toRelation.append(element)
                if element not in telem._fromRelation:
                    telem._fromRelation.append(element)
        super(ClassDiagram, self).OnUndoRedoChanged()

    def OnUndoRedoRemoving(self, root=True):
        """Prepare for delete"""
        if hasattr(self, '_pane') and not self._pane is None:
            book = context.frame.docBook
            page = self._pane
            delattr(self, '_pane')
            page.Commit()
            self._paneIndex = book.GetPageIndex(page)
            book.DeletePage(self._paneIndex)
        super(ClassDiagram, self).OnUndoRedoRemoving(root)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(ClassDiagram, self).OnUndoRedoAdd()
        if hasattr(self, '_paneIndex'):
            from activity.models.ui import pane
            book = context.frame.docBook
            page = pane.DiagramPane(book, self)
            self._pane = page
            book.InsertPage(self._paneIndex, page, self.tab_label,
                False, self.bitmap_index)
            delattr(self, '_paneIndex')

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        return rc.GetBitmap('classdiagram')
        #return GetBitmap(4)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('classdiagram')

    def UnselectAll(self):
        """Unselect all elements"""
        for element in self._elements:
            element.Select(False)

    def DrawClassDiagram(self, ctx, skip=None):
        """Draw class diagram"""
        for element in self._elements:
            if element._obj == skip:
                continue
            element.Draw(ctx)

    def __getstate__(self):
        """Set picke context"""
        state = dict(self.__dict__)
        if '_parentIndex' in state:
            del state['_parentIndex']
        if '_pane' in state:
            del state['_pane']
        if '_paneIndex' in state:
            del state['_paneIndex']
        return state

    def PositionClass(self, cls, pos):
        """Reposition a class element"""
        cls.project.SetModified(True)
        for element in self._elements:
            if element._obj == cls:
                element._pos = pos
                return element
        element = ClassElement(cls, pos)
        self._elements.append(element)
        return element

    def HitTest(self, pos):
        """Check about element near pos"""
        result = (None, NO_WHERE)
        for element in self._elements:
            (a, b) = element.HitTest(pos)
            if b is not NO_WHERE:
                if element._selected:
                    return a, b
                else:
                    result = (a, b)
        return result

    def FindElement(self, obj):
        """Finds a class diagram representation for obj"""
        for x in self._elements:
            if x._obj == obj:
                return x
        return None
