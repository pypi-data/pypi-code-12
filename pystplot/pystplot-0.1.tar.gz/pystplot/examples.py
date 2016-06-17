import pystplot.pystplot as pl
import math

x_inds = range(-20,10)
x_vals = [xi/10.0 for xi in x_inds]
y_vals = [math.exp(-x*x) for x in x_vals]
sin_vals =  [math.sin(x) for x in x_vals]
x2 = [2*x for x in x_vals]

pl.subplot(2,2,1)
pl.plot(x_vals, y_vals, '-og')
pl.plot(x_vals, x_vals, '-o')

pl.subplot(2,2,2)
pl.plot(x_vals, x2,'-r')
pl.plot(x_vals, sin_vals,'ro')

pl.subplot(2,2,3)
pl.plot(x_vals, x2,'-r')
pl.plot(x_vals, sin_vals,'ro')

pl.subplot(2,2,4)
pl.plot(x_vals, y_vals, '-o')
pl.plot(x_vals, x_vals, '-o')

pl.show()
