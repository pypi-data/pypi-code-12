#! ##Working with SVG graphic


#! ###You can load SVG file ...

#%img python.svg

#! ###or render SVG python string

svgsyntax='''
<svg height="55" width="55">
    <circle cx="30" cy="30" r="20"
    stroke="black" stroke-width="1" fill="tan" /> 
</svg>
'''
svgsyntax #%svg

#! so this is the way to get parametric drawing

r = 67 #<< - circle radius value
xs = 122 #<< - center x
ys = 78 #<< - center y

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

#!
'''
###To make parameterise easer you can use `svgwrite` package
'''
import svgwrite

a = 90 #<< - rec a dimension
b = 67 #<< - rec b dimension

svg_document = svgwrite.Drawing(size = (200, 100))
svg_document.add(svg_document.rect(insert = (0, 0), size = (a, b),
                                   stroke_width = "1",stroke = "black",fill = "tan"))
svg_document.add(svg_document.text("Rectangle size" + str(a)+ 'x' +str(b) ,
                                   insert = (a/2-20, b/2)))

svg_document #%svg 
