import unum.units as u

#!##*Circle Area calculation*

#%img CircleArea_fig_1.png

#! For input data

r = 40* u.cm #!- circle radius

import math

pi = math.pi #! - pi value

#! from formula that everyone know

#%code
Area = pi * r**2
#%

#! we have

Area #! - circle area

#! ###So, the area of circle diameter %(r)s is %(Area)s .
