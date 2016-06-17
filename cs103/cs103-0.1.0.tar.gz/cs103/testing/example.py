# Testing example for testing utility wrapper

from testing import *

def area(width, height):
    """
    Real, Real -> Real

    Produces the area of a rectangle with the given
    width and height
    """
    return width * height

expect(area(0, 0), 0)
expect(area(2, 5), 10)
expect(area(1.2, 3.1), 3.72)

# Failing tests as examples
expect(area(1, 1), 2)
expect(area(1, 2), 1)

summary()
