#! ##*Hallo this is SeePy tutorial*

#%img x_monty.png

#!
'''
Please look at SeePy report window and your tutorial *.py file editor
that has just ran. It is easy to see how does it work. Please try change
this scrip in editor and use save<Ctrl+s> to see how report is changing.

Let's write some python script to calculate something to mee.
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

You can see python code from your script in SeePy report, pleas look at this syntax ..
'''

#%code
r = 120
import math
math.pi
area = math.pi * r ** 2
#%

area #@- here is what we get in `area` variable.

#! So the area of circle %(r)s diameter is %(area)s .

#!
'''
Lets show image in your report,
the image file must be in the same directory where you script is.
'''

#%img x_python.png

#! ... here our Python is.

#!
'''
---
###*Please note that SeePy is still under construction, new features coming soon*...
'''















