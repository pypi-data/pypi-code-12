from svg import xmlentities, Path, Graph


class LineAxes(object):
    """Bottom and left axes for a graph"""

    def __init__(self, color='black'):
        self.color = color

    def render(self, stream, x, y, w, h, interval):
        """Render the axes to the stream"""
        p = Path()
        p.to(x, y)
        p.to(x, y+h)
        p.to(x + w, y+h)
        p.setClosed(False)
        stream.write('<path d="%s" stroke="%s" stroke-width="1" fill="none"/>\n'% (p, self.color))


class ShadedAxes(LineAxes):
    def __init__(self, color='black', bgcolor='rgba(0,0,0,0.05)'):
        self.color = color
        self.bgcolor = bgcolor

    def render(self, stream, x, y, w, h, interval):
        super(ShadedAxes, self).render(stream, x, y, w, h, 0)

        cy = y + h - interval
        while cy > y:
            stream.write('<rect x="%f" y="%f" width="%f" height="%f"  fill="%s"/>\n' % (x, cy, w, interval, self.bgcolor))
            cy -= interval * 2
