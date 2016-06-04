import numpy as np



def toFloatArray(img):
    '''
    transform an unsigned integer array into a
    float array of the right size
    '''
    _D = {1:np.float32,#uint8
      2:np.float32,#uint16
      4:np.float64,#uint32
      8:np.float64}#uint64
    return img.astype(_D[img.itemsize])
    