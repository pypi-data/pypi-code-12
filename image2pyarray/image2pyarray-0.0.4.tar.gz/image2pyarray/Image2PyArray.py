import os
import zipfile
try:
    from Pillow import Image
except:
    from PIL import Image
import numpy
import re

class Image2PyArray:
    def __init__(self, options = {}):
        self.grayscale = options['grayscale'] \
                if ('grayscale' in options) else True
        self.width = options['width'] \
                if ('width' in options) else 36
        self.height = options['height'] \
                if ('height' in options) else 36
        self.type = options['type'] \
                if ('type' in options) else ''
        self.archive = None
        self.archivepath = None

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
        self.type = 'directory'
        self.check_dir_tree(dirname)
        train_XY = self.get_XY_tuple(os.path.join(dirname, "train")) 
        test_XY = self.get_XY_tuple(os.path.join(dirname, "test")) 
        return train_XY, test_XY

    def get_XY_tuple(self, dirname):
        X = []
        Y = []

        labels = self.getdirs(self.relativepath(dirname))
        for label in labels:
            labeldir = os.path.join(dirname, label)
            for filename in self.getfiles(self.relativepath(labeldir)):
                filepath = os.path.join(labeldir, filename)
                X.append(self.pic2array(filepath))
                Y.append(self.label2array(label,labels))
        return (X, Y)

    def pic2array(self, filepath):
        if self.type == 'directory':
            image = Image.open(filepath)
        elif self.type == 'zip':
            relativepath = self.relativepath(filepath)
            image = Image.open(self.archive.open(self.archive.getinfo(relativepath)))
        else:
            raise Exception("Unknown type")

        if self.grayscale:
            return numpy.asarray(image.convert('L').resize((self.width, self.height)))
        else:
            raise Exception("loading image except for grayscale not supported yet...")

    def label2array(self, label, labels):
        return map(lambda x: 1 if (x == label) else 0, labels)

    # check if dirname
    # - has /train and /test
    # - /train/* and /test/* has same names and numbers
    def check_dir_tree(self, dirname):
        if self.type == 'directory':
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
        elif self.type == 'zip':
            if not os.path.isfile(dirname):
                raise Exception("Cannot access zip file %s" % dirname)
            else:
                self.archive = zipfile.ZipFile(dirname, 'r')
                self.archive_namelist = self.archive.namelist()
            try:
                self.archive.getinfo('train/')
            except:
                raise Exception("Cannot access directory /train in %s" % dirname)
            try:
                self.archive.getinfo('test/')
            except:
                raise Exception("Cannot access directory /test in %s" % dirname)
            train_cats = self.getdirs('train/')
            test_cats = self.getdirs('test/')
            if set(train_cats) != set(test_cats):
                raise Exception("Directories under /train and /test should be same.")
        else:
            raise Exception("Unknown type")

    def getdirs(self, path):
        if self.type == 'directory':
            dirs=[]
            for item in os.listdir(path):
                if os.path.isdir(os.path.join(path,item)):
                    dirs.append(item)
            return dirs
        elif self.type == 'zip':
            if not path.endswith('/'):
                path = path+'/'
            return filter(lambda x: x != None,\
                    map(lambda x: re.match("^"+path+"([^/]+)/$", x).group(1) \
                    if re.match("^"+path+"([^/]+)/$", x) \
                    else None, self.archive_namelist))

    def getfiles(self, path):
        if self.type == 'directory':
            files=[]
            for item in os.listdir(path):
                if not os.path.isdir(os.path.join(path,item)):
                    files.append(item)
            return files
        elif self.type == 'zip':
            if not path.endswith('/'):
                path = path+'/'
            return filter(lambda x: x != None,\
                    map(lambda x: re.match("^"+path+"([^/]+)$", x).group(1) \
                    if re.match("^"+path+"([^/]+)$", x) \
                    else None, self.archive_namelist))

    # we do not want to extract images from zip,
    # we just want to read as is in zip file...
    # 
    def from_zip(self, zippath):
        zippath = os.path.abspath(zippath)
        self.type = 'zip'
        self.archivepath = zippath

        self.check_dir_tree(zippath)
        train_XY = self.get_XY_tuple(os.path.join(zippath, "train")) 
        test_XY = self.get_XY_tuple(os.path.join(zippath, "test")) 
        return train_XY, test_XY

    """
    filepath will be such as
     - /home/hoge/work/train/class1/a.jpg
        ---> /home/hoge/work/train/class1/a.jpg
     - /home/hoge/work/train/class1/
        ---> /home/hoge/work/train/class1/
     - /home/fuga/archive.zip/train/class1/a.jpg
        ---> train/class1/a.jpg
     - /home/fuga/archive.zip/train/
        ---> train/
    """
    def relativepath(self, filepath):
        if self.type == 'directory':
            return filepath
        elif self.type == 'zip':
            if filepath.startswith(self.archivepath):
                filepath = filepath[len(self.archivepath):]
            if filepath.startswith('/'):
                filepath = filepath[len('/'):]
            return filepath

        else:
            raise Exception("Unknown type")


