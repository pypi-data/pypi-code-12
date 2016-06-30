from PIL import Image
import numpy as np
from random import randrange

#==================================

from myonPNGcolors import mpc
from myonPNGexception import ColorNotDefined, EndingError


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

    
    def colorb(self,rgb):
        c = 0
        col = rgb

        if rgb not in mpc and rgb[3] != '-':
            raise ColorNotDefined('Color not defined!')
        
        if rgb in mpc: rgb = mpc[col]

        while c < len(garray):
            garray[c] = [int(rgb[0:3]),int(rgb[4:7]),int(rgb[8:11])]
            c += 1

    def save(self,path):
        img = Image.fromarray(garray.astype(np.uint8))
        if path[-3:] != 'png': raise EndingError('png data ending required!')
        img.save(path)

    def printarray(self):
        print(garray)

def colorp(x,y,rgb):
    if (rgb not in mpc) and (rgb[3] != '-'):
            raise ColorNotDefined('Color not defined!')
        
    if rgb in mpc: rgb = mpc[col]
    
    garray[y-1][x-1] = [int(rgb[0:3]),int(rgb[4:7]),int(rgb[8:11])]

def colora(x1,y1,x2,y2,rgb):
    if (rgb not in mpc) and (rgb[3] != '-'):
            raise ColorNotDefined('Color not defined!')
        
    if rgb in mpc: rgb = mpc[col]
    x3 = x1
    while y1 < y2:
        while x1 < x2:
            garray[y1-1][x1-1] = [int(rgb[0:3]),int(rgb[4:7]),int(rgb[8:11])]
            x1 += 1

        y1 += 1
        x1 = x3
    
#===============================================================================  

def random_image(width,height,path,bw=None):
    c2 = c1 = 0
    x = width
    y = height
    
    img = G(x,y)

    while c1 <= y:
        while c2 <= x:
            r = randrange(0,255)
            g = randrange(0,255)
            b = randrange(0,255)
            if bw:
                r = (3-len(str(r)))*'0' + str(r)
                colorp(c2,c1,2*(str(r)+'-')+str(r))
                
            else:
                r = (3-len(str(r)))*'0' + str(r)
                g = (3-len(str(g)))*'0' + str(g)
                b = (3-len(str(b)))*'0' + str(b)
                colorp(c2,c1,r+'-'+g+'-'+b)

            
            c2 += 1
        c1 += 1
        c2 = 1

    img.save(str(path))
    

#===============================================================================

if __name__ == '__main__':

    random_image(1000,1000,'testimg.png',True)
