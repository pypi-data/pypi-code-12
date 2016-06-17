import matplotlib.pyplot as plt
import matplotlib.patches as patches
from functools import reduce

class shape(object):
    fill = "none"
    outline = "none"

    def __init__(self, width, height, mode, color):
        self.width = width
        self.height = height
        if mode == "solid":
            self.fill = color
        elif mode == "outline":
            self.outline = color
        else:
            raise ValueError("expected a mode, given %s" % mode)

    def draw(self, canvas, x, y):
        pass

    def check(self, canvas, x, y, z):
        pass

    def __eq__(self, other):
        if (not isinstance(other, shape)): return False

        c1 = []
        c2 = []
        self.check(c1, 0, 0, 0)
        other.check(c2, 0, 0, 0)

        c1.sort()
        c2.sort()

        return c1 == c2

class rectangle(shape):
    def draw(self, canvas, x, y):
        canvas.add_patch(patches.Rectangle((x,y),
            self.width, self.height,
            fc = self.fill,
            ec = self.outline))

    def check(self, canvas, x, y, z):
        canvas.append("r %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

    def check(self, canvas, x, y, z):
        canvas.append("r %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

class square(rectangle):
    def __init__(self, side, mode, color):
        super(square, self).__init__(side, side, mode, color)

class ellipse(shape):
    def draw(self, canvas, x, y):
        canvas.add_patch(patches.Ellipse((x + self.width / 2, y + self.height / 2),
            self.width, self.height,
            fc = self.fill,
            ec = self.outline))

    def check(self, canvas, x, y, z):
        canvas.append("e %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

    def check(self, canvas, x, y, z):
        canvas.append("e %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

class circle(ellipse):
    def __init__(self, radius, mode, color):
        super(ellipse, self).__init__(radius * 2, radius * 2, mode, color)

class triangle(shape):
    def draw(self, canvas, x, y):
        canvas.add_patch(patches.Polygon(((x + self.width / 2, y + self.height),
                (x, y),
                (x + self.width, y)),
                fc = self.fill,
                ec = self.outline))

    def check(self, canvas, x, y, z):
        canvas.append("t %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

    def check(self, canvas, x, y, z):
        canvas.append("t %d %d %d %d %d %s %s" % (x, y,
            self.width + x, self.height + y,
            z,
            self.fill,
            self.outline))

class glue(shape):
    shapes = []
    def __init__(self, *shapes):
        self.shapes = shapes
        self.width = self.calculate_width()
        self.height = self.calculate_height()

    def calculate_width():
        pass
    def calculate_height():
        pass

class beside(glue):
    def calculate_width(self):
        def add(a, b): return a + b.width
        return reduce(add, self.shapes, 0)

    def calculate_height(self):
        def m(a, b): return max(a, b.height)
        return reduce(m, self.shapes, 0)

    def draw(self, canvas, x, y):
        xc = x
        for s in self.shapes:
            s.draw(canvas, xc, y + (self.height - s.height) / 2)
            xc += s.width

    def check(self, canvas, x, y ,z):
        xc = x
        for s in self.shapes:
            s.check(canvas, xc, y, z)
            xc += s.width

    def check(self, canvas, x, y ,z):
        xc = x
        for s in self.shapes:
            s.check(canvas, xc, y, z)
            xc += s.width

class above(glue):
    def calculate_width(self):
        def m(a, b): return max(a, b.width)
        return reduce(m, self.shapes, 0)

    def calculate_height(self):
        def add(a, b): return a + b.height
        return reduce(add, self.shapes, 0)

    def draw(self, canvas, x, y):
        yc = y
        for s in reversed(self.shapes):
            s.draw(canvas, x + (self.width - s.width) / 2, yc)
            yc += s.height

    def check(self, canvas, x, y ,z):
        yc = y
        for s in self.shapes:
            s.check(canvas, x, yc, z)
            yc += s.height

    def check(self, canvas, x, y ,z):
        yc = y
        for s in self.shapes:
            s.check(canvas, x, yc, z)
            yc += s.height

class overlay(glue):
    def calculate_width(self):
        def m(a, b): return max(a, b.width)
        return reduce(m, self.shapes, 0)

    def calculate_height(self):
        def m(a, b): return max(a, b.height)
        return reduce(m, self.shapes, 0)

    def draw(self, canvas, x, y):
        for s in reversed(self.shapes):
            s.draw(canvas, x + (self.width - s.width) / 2, y + (self.height - s.height) / 2)

    def check(self, canvas, x, y, z):
        zc = z
        for s in reversed(self.shapes):
            s.check(canvas, x, y, zc)
            zc += 1

    def check(self, canvas, x, y, z):
        zc = z
        for s in reversed(self.shapes):
            s.check(canvas, x, y, zc)
            zc += 1

def draw(shape):
    fig = plt.figure(figsize=(shape.width/96, shape.height/96))
    ax = plt.Axes(fig,[0,0,1,1])
    ax.axis((-2, shape.width + 2, -2, shape.height + 2))
    ax.set_axis_off()
    fig.add_axes(ax)

    shape.draw(ax, 0, 0)

# Image primitives

def image_width(shape):
    return shape.width

def image_height(shape):
    return shape.height
