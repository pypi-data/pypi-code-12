from image import *

draw(Beside(Square(20, "solid", "red"), Square(20, "solid", "green")))
draw(Overlay(Above(Square(20, "solid", "blue"),
                   Square(20, "solid", "green")),
             Rectangle(400, 400, "solid", "white")))

print image_width(Beside(Square(20, "solid", "red"), Square(20, "solid", "green")))

a = Square(100, "solid", "red")
b = Square(100, "solid", "blue")

aa = Beside(Above(a,b),Above(b,a))
bb = Above(Beside(a,b),Beside(b,a))

draw(aa)
draw(bb)

print aa == bb
