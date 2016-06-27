
import math, os, shutil, sys, subprocess
from bf.file import File

DEBUG=False

class Image(File):

    def convert(self, outfn=None, img_args=[]):
        """convert the image to the outfn, with the given img args"""
        if outfn is None: outfn=self.fn
        if not os.path.exists(os.path.dirname(outfn)):
            os.makedirs(os.path.dirname(outfn))
        gm = self.gm or 'gm'
        args = [gm, 'convert'] + img_args + [self.fn, outfn]
        if DEBUG==True: self.log('Image.convert(): ', args)
        o = subprocess.check_output(args).decode('utf8')
        if o != '': self.log(o)
        return outfn

    def mogrify(self, outfn=None, overwrite=True, format=None, quality=80, jpg_matte=4, jpg_format=1, 
                width=None, height=None, maxwh=2048, maxw=None, maxh=None, maxpixels=3.2e6, scale=1, res=300, 
                resample_method=4, orient=None, alpha=None):
        """process the image and output a new file"""
            
        if overwrite==False and os.path.isfile(outfn): 
            return
        outfn = outfn or self.fn
        if outfn != self.fn:
            shutil.copy(self.fn, outfn)

        gm = self.config and self.config.Ark and self.config.Ark.gm or 'gm'
                
        args = [gm, 'mogrify']

        if alpha is not None:
            args += ['-alpha', alpha]
        if format is not None:
            args += ['-format', format]
        geom_arg = None
        if scale != 1:
            geom_arg = str(scale*100)+'%'
        elif width is not None and height is not None:
            geom_arg = "%dx%d!" % (width, height)
        elif width is not None:
            geom_arg = "%d" % width
        elif height is not None:
            geom_arg = 'x%d' % height
        elif maxwh is not None:
            geom_arg = "%dx%d>" % (maxwh, maxwh)
        elif maxw is not None and maxh is not None:
            geom_arg = "%dx%d>" % (maxw, maxh)
        elif maxw is not None:
            geom_arg = "%d>" % maxw
        elif maxh is not None:
            geom_arg = "x%d>" % maxh
        if geom_arg is not None:
            args += ['-resize', geom_arg]

        if orient is not None:
            if orient == 'vertical' and w > h and w > maxw:
                args += ['-rotate', '-90']
            elif orient == 'horizontal' and h > w and h > maxh:
                args += ['-rotate', '90']
        
        args += ['-quality', "%d" % quality]
        
        args += [outfn]
        
        if DEBUG==True: print('  ', args)
        
        o = subprocess.check_output(args).decode('utf8')
        if o != '': print(o)

        # check to make sure maxpixels is met, and downsize if not
        w,h=[int(i) for i in subprocess.check_output([gm, 'identify', '-format', '%w,%h', outfn]).decode('utf8').strip().split(',')]
        if maxpixels is not None and w*h > maxpixels:
            downratio = math.sqrt(float(maxpixels) / float(w*h))
            geom_arg = "%dx%d>" % (int(w*downratio), int(h*downratio))
            o = subprocess.check_output([gm, 'mogrify', '-resize', geom_arg, '-quality', "%d" % quality, outfn]).decode('utf8')
            if o!='': print(o)
            if DEBUG==True: print('\n', outfn, '\n  ', w, h, w*h, maxpixels, downratio, geom_arg)

