from PIL import Image
import numpy as np
from random import randrange

#===============================================================================

class G():
    def __init__(self,width=1,height=1):
        global garray
        w = width
        h = height
        
        gl = h*[w*[[255,255,255]]]

        garray = np.asarray(gl)

    def read_img(self,path):
        global garray
        img = Image.open(str(path))
        garray = np.asarray(img)   

    
    def colorb(self,r,g,b):
        c = 0
        while c < len(garray):
            garray[c] = [r,g,b]
            c += 1

    def save(self,path):
        img = Image.fromarray(garray.astype(np.uint8))
        img.save(path)

    def printarray(self):
        print(garray)

def colorp(x,y,r,g,b):
    garray[y-1][x-1] = [r,g,b]

def colora(x1,y1,x2,y2,r,g,b):
    x3 = x1
    while y1 < y2:
        while x1 < x2:
            garray[y1-1][x1-1] = [r,g,b]
            x1 += 1

        y1 += 1
        x1 = x3
    
#===============================================================================  

def random_image(width,height,path):
    c2 = c1 = 0
    x = width
    y = height
    
    img = G(x,y)

    while c1 <= y:
        while c2 <= x:
            r = randrange(0,255)
            g = randrange(0,255)
            b = randrange(0,255)
            
            colorp(c2,c1,r,g,b)

            
            c2 += 1
        c1 += 1
        c2 = 1

    img.save(str(path))
    

#===============================================================================

if __name__ == '__main__':
    base = G(3,2)
    base.colorb(255,0,0)
    base.save('testimg2')
    base.printarray()
