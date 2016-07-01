from PIL import Image
import numpy as np
from random import randrange

#==================================

from myonPNGcolors import mpc
from myonPNGexception import ColorNotDefined, EndingError


#===============================================================================
class G():
    def __init__(self,width=1,height=1):
        global glist
        w = width
        h = height
        
        gl = h*[w*[[255,255,255]]]

        garray = np.asarray(gl)
        glist = garray.tolist()
        

    def read_img(self,path):
        global glist
        img = Image.open(str(path))
        rarray = np.asarray(img)
        glist = rarray.tolist()
        

    
    def colorb(self,rgb):
        global glist
        c = 0
        col = rgb

        if rgb not in mpc and rgb[3] != '-':
            raise ColorNotDefined('Color not defined!')
        
        if rgb in mpc: rgb = mpc[col]

        glist = len(glist)*[ len(glist[0])*[[ int(rgb[0:3]),
                int(rgb[4:7]),int(rgb[8:11])]]]

    def save(self,path):
        img = Image.fromarray(np.asarray(glist).astype(np.uint8))
        if path[-3:] != 'png': raise EndingError('png data ending required!')
        img.save(path)

    def printarray(self):
        print(np.asarray(glist))

    def colorp(self,x,y,rgb):
        col = rgb
        if (rgb not in mpc) and (rgb[3] != '-'):
                raise ColorNotDefined('Color not defined!')
            
        if rgb in mpc: rgb = mpc[col]
        
        glist[y-1][x-1] = [int(rgb[0:3]),int(rgb[4:7]),int(rgb[8:11])]

    def colora(self,x1,y1,x2,y2,rgb):
        col = rgb
        if (rgb not in mpc) and (rgb[3] != '-'):
                raise ColorNotDefined('Color not defined!')
            
        if rgb in mpc: rgb = mpc[col]
        x3 = x1
        while y1 < y2:
            while x1 < x2:
                glist[y1-1][x1-1] = [int(rgb[0:3]),int(rgb[4:7]),int(rgb[8:11])]
                x1 += 1

            y1 += 1
            x1 = x3

    def blackwhite(self):
        c1 = c2 = 0
        while c1 < len(glist):
            while c2 < len(glist[0]):
                v = (glist[c1][c2][0]+glist[c1][c2][1]+
                                 glist[c1][c2][2])//3
                glist[c1][c2] = [v,v,v]
                c2 += 1

            c1 += 1
            c2 = 0
    
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

    G = G()
    G.read_img('testimg.png')

    G.blackwhite()

    G.save('testimg2.png')
    
