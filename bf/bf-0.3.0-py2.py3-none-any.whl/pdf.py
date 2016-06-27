
DEBUG=False

import os, sys, subprocess
from .file import File

class PDF(File):

    def gswrite(self, fn=None, device='jpeg', res=1200, alpha=2, quality=90, gs=None, **resources):
        "use ghostscript to create output file(s) from the PDF"
        if fn is None: 
            fn = os.path.splitext(self.fn)[0] + GS_DEVICE_EXTENSIONS[device]
        gs = (resources.get('gs') or self.gs or 'gs')
        callargs = [gs, '-dSAFER', '-dBATCH', '-dNOPAUSE',
                    '-sDEVICE=%s' % device,
                    '-r%d' % res]
        if device=='jpeg': callargs += ['-dJPEGQ=%d' % quality]
        if 'png' in device: callargs += [
            '-dTextAlphaBits=%d' % alpha,
            '-dGraphicsAlphaBits=%d' % alpha]
        callargs += ['-sOutputFile=%s' % fn,
                    self.fn]
        try:
            subprocess.check_output(callargs)
        except subprocess.CalledProcessError as e:
            self.log(' '.join(callargs))
            self.log(str(e.output, 'utf-8'), file=sys.stderr)
        return fn


GS_DEVICE_EXTENSIONS = {
    'png16m':'.png', 
    'png256':'.png', 
    'png16':'.png', 
    'pngmono':'.png', 
    'pngmonod':'.png', 
    'pngalpha':'.png',
    'jpeg':'.jpg', 
    'jpeggray':'.jpg',
    'tiffgray':'.tiff', 
    'tiff12nc':'.tiff', 
    'tiff24nc':'.tiff', 
    'tiff48nc':'.tiff', 
    'tiff32nc':'.tiff', 
    'tiff64nc':'.tiff', 
    'tiffsep':'.tiff', 
    'tiffsep1':'.tiff', 
    'tiffscaled':'.tiff', 
    'tiffscaled4':'.tiff', 
    'tiffscaled8':'.tiff', 
    'tiffscaled24':'.tiff', 
    'tiffscaled32':'.tiff', 
    'tiffcrle':'.tiff', 
    'tiffg3':'.tiff', 
    'tiffg32d':'.tiff', 
    'tiffg4':'.tiff', 
    'tifflzw':'.tiff', 
    'tiffpack':'.tiff', 
    'txtwrite':'.txt',
    'psdcmyk':'.psd', 
    'psdrgb':'.psd',
}

