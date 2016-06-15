import os
try:
    from Pillow import Image
except:
    from PIL import Image
import numpy

class Image2PyArray:
    def __init__(self, options = {}):
        self.grayscale = options['grayscale'] \
                if ('grayscale' in options) else True
        self.width = options['width'] \
                if ('width' in options) else 36
        self.height = options['height'] \
                if ('height' in options) else 36

    """
    dirname
     |
     |-train
     |  |
     |  |-classname_1
     |  |  |
     |  |  |-1.jpg
     |  |  |-2.jpg
     |  |  :
     |  |  `-l.jpg
     |  |
     |  |-classname_2
     |  |  |
     |  |  |-1.jpg
     |  |  |-2.jpg
     |  |  :
     |  |  `-m.jpg
     |  :
     |  `-classname_k
     |     |
     |     |-1.jpg
     |     |-2.jpg
     |     :
     |     `-n.jpg
     | 
     `-test
        |
        |-classname_1
        |  |
        |  |-1.jpg
        |  |-2.jpg
        |  :
        |  `-p.jpg
        |
        |-classname_2
        |  |
        |  |-1.jpg
        |  |-2.jpg
        |  :
        |  `-q.jpg
        :
        `-classname_k
           |
           |-1.jpg
           |-2.jpg
           :
           `-r.jpg
    
    
    (# of pics) x (# of pixels)
    X_train = [
        1: [0, 255, 255, ...],
        2: [255, 128, 255, ...],
        :
        (# pf pics): [64, 128, 1, ...]
    ]
    
    (# of pics) x (# of classes)
    Y_train = [
        1: [0,0,0,1,...],
        2: [0,1,0,0,...],
        :
        (# of pics): [0,0,1,0,...]
    ]
    
    (# of pics) x (# of pixels)
    X_test = [
        1: [0, 255, 255, ...],
        2: [255, 128, 255, ...],
        :
        (# pf pics): [64, 128, 1, ...]
    ]
    
    (# of pics) x (# of classes)
    Y_test = [
        1: [0,0,0,1,...],
        2: [0,1,0,0,...],
        :
        (# of pics): [0,0,1,0,...]
    ]
    
    return (X_train, Y_train), (X_test, Y_test)
    """
    def from_dir(self, dirname):
        self.check_dir_tree(dirname)
        train_XY = self.get_XY_tuple(os.path.join(dirname, "train")) 
        test_XY = self.get_XY_tuple(os.path.join(dirname, "test")) 
        return train_XY, test_XY

    def get_XY_tuple(self, dirname):
        X = []
        Y = []

        labels = self.getdirs(dirname)
        for label in labels:
            labeldir = os.path.join(dirname, label)
            for filename in self.getfiles(labeldir):
                filepath = os.path.join(labeldir, filename)
                X.append(self.pic2array(filepath))
                Y.append(self.label2array(label,labels))
        return (X, Y)

    def pic2array(self, filepath):
        if self.grayscale:
            return numpy.asarray(Image.open(filepath).convert('L').resize((self.width, self.height)))
        else:
            raise Exception("loading image except for grayscale not supported yet...")

    def label2array(self, label, labels):
        return map(lambda x: 1 if (x == label) else 0, labels)

    # check if dirname
    # - has /train and /test
    # - /train/* and /test/* has same names and numbers
    def check_dir_tree(self, dirname):
        if not os.path.isdir(dirname):
            raise Exception("Cannot access directory %s" % dirname)
        train = os.path.join(dirname,"train")
        if not os.path.isdir(train):
            raise Exception("Cannot access directory %s" % train)
        test = os.path.join(dirname,"test")
        if not os.path.isdir(test):
            raise Exception("Cannot access directory %s" % test)
        if set(self.getdirs(train)) != set(self.getdirs(test)):
            raise Exception("Directories under /train and /test should be same.")

    def getdirs(self, path):
        dirs=[]
        for item in os.listdir(path):
            if os.path.isdir(os.path.join(path,item)):
                dirs.append(item)
        return dirs
    def getfiles(self, path):
        files=[]
        for item in os.listdir(path):
            if not os.path.isdir(os.path.join(path,item)):
                files.append(item)
        return files


    def from_zip(self, zipfile):
        return

