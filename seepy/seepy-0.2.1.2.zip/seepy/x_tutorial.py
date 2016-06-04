#! #*Hallo this is SeePy tutorial*

#%img x_monty.png

#!
'''
Please look at SeePy report window and your tutorial *.py file editor
that has just run. It is easy to see how does it work. Please try change
this scrip in editor and use save<Ctrl+s> to see how report is changing.

Let's write some python script to calculate something.
'''

a = 12
b = 25
c = a + b
print a

#!
'''
You can run this script as normal *.py script - run it by <F5> in script editor.
You have seen the `a` value in shell output. But you can see it in your SeePy report ...
'''

a #! - here it is

#!
'''
Let's change the `a` value 
'''

a = 30 #! - here is changed value

#!
'''
You can call variable values in this comments.
So, we have %(a)s , %(b)s and %(c)s
Lets calculate something
'''

result = a + b *(c / a)

result #! - this is result

#!
'''
You can still run this script as
normal *.py script - run it by <F5> in script editor.
As you can guess python engine does't see the SeePy syntax.

SeePy comments use Markdown. Look ..

#Title

##Title

###Title

*some text*

**some text**

---

* Title
* Title2

More about Markdown you can see here
https://daringfireball.net/projects/markdown/

Here is Markdown tutorial
http://www.markdowntutorial.com/
'''
#!
'''
---

You can see python code from your script in SeePy report, pleas look at this syntax ..
'''

#%code
r = 120
import math
math.pi
area = math.pi * r ** 2
#%

area #!- here is what we get in `area` variable.

#! So the area of circle %(r)s diameter is %(area)s .

#!
'''
---
Lets show image in your report,
the image file must be in the same directory where you script is.
'''

#%img x_python.png

#! ... here our Python is.

#!
'''
---
What about plotting?? You can use Matplotlib pyplot - here is some example
'''

import matplotlib.pyplot as plt
import numpy as np
t = np.arange(-1.0, 2.0, 0.01)
s1 = np.cos(9*np.pi*t) + 3 * t ** 2
plt.plot(t, s1)
plt #%plt
plt.clf()

#! and other one:

s2 = np.cos(9*np.pi*t)
plt.plot(t, s2) #%plt
plt.clf()

#!
'''
---
If you need to publish some mathematical formula LaTex syntax can be used
'''

#%tex s(t) = \mathcal{A}\mathrm{sin}(2 \omega t)
#%tex y = x^2 + 2*x +3

#! or if the fomula is in you python code

pi = 3.14 #! - pi value
r = 40 #! - circle radius
#! from formula
Area = pi * r ** 2 #%tex
Area #! - what we get

#!
'''
---
You can change python variables in report, so finally you don't need to edit
script source to change input data. Please not that the new values will
be stored in the script source.
'''

a = 120 #! - this is not interactive variable in your report
b = 44 #<< - this is interactive variable in your report - click to change it
#! the values are %(a)s and %(b)s.

#! ---

#!
'''
What about drawing in report ??

You can create drawing using SVG syntax.

Python string with SVG syntax can be rendered.
'''

svgsyntax='''
<svg height="55" width="55">
    <circle cx="30" cy="30" r="20"
    stroke="black" stroke-width="1" fill="tan" /> 
</svg>
'''

svgsyntax #%svg

#! so this is the way to get parametric drawing

r = 50 #! - circle radius value
xs = 120 #! - center x
ys = 70 #! - center y

svgsyntax='''
<svg height="150" width="200">
    <circle cx="{1}" cy="{2}"
    r="{0}" stroke="black" stroke-width="1" fill="tan" />
    <text x="{1}" y="{2}" fill="black"
    font-size="15">circle {0} radius </text>  
</svg>
'''.format(r, xs, ys)

#! for this parameters we have

svgsyntax #%svg

#!To make parametrise easer you can use `svgwrite` package

import svgwrite

a = 60 #! - rec a dimension
b = 100 #! - rec b dimension

svg_document = svgwrite.Drawing(size = (200, 100))
svg_document.add(svg_document.rect(insert = (0, 0), size = (a, b),
                                   stroke_width = "1",stroke = "black",fill = "tan"))
svg_document.add(svg_document.text("Rectangle size" + str(a)+ 'x' +str(b) ,
                                   insert = (a/2-20, b/2)))

svg_document #%svg 





