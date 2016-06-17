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
        if ('grayscale' in options):
            self.__grayscale = options['grayscale']
            self.__channel_num = 1
        else:
            self.__grayscale = True
            self.__channel_num = 1

        self.__width = options['width'] \
                if ('width' in options) else 36
        self.__height = options['height'] \
                if ('height' in options) else 36
        self.__type = options['type'] \
                if ('type' in options) else ''
        self.__archive = None
        self.__archivepath = None

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
        self.__type = 'directory'
        self.__check_dir_tree(dirname)
        train_XY = self.__get_XY_tuple(os.path.join(dirname, "train")) 
        test_XY = self.__get_XY_tuple(os.path.join(dirname, "test")) 
        return train_XY, test_XY

    """
        we do not want to extract images from zip,
        we just want to read as is in zip file...
        directory structure is same as from_dir()
    """ 
    def from_zip(self, zippath):
        zippath = os.path.abspath(zippath)
        self.__type = 'zip'
        self.__archivepath = zippath

        self.__check_dir_tree(zippath)
        train_XY = self.__get_XY_tuple(os.path.join(zippath, "train")) 
        test_XY = self.__get_XY_tuple(os.path.join(zippath, "test")) 
        return train_XY, test_XY

    def __get_XY_tuple(self, dirname):
        X = []
        Y = []

        labels = self.__getdirs(self.__relativepath(dirname))
        for label in labels:
            labeldir = os.path.join(dirname, label)
            for filename in self.__getfiles(self.__relativepath(labeldir)):
                filepath = os.path.join(labeldir, filename)
                x = self.__pic2array(filepath)
                X.append(x.reshape(self.__channel_num, self.__width, self.__height ))
                y = self.__label2array(label,labels)
                Y.append(y)
        return (numpy.array(X), numpy.array(Y))

    def __pic2array(self, filepath):
        if self.__type == 'directory':
            image = Image.open(filepath)
        elif self.__type == 'zip':
            __relativepath = self.__relativepath(filepath)
            image = Image.open(self.__archive.open(self.__archive.getinfo(__relativepath)))
        else:
            raise Exception("Unknown type")

        if self.__grayscale:
            return numpy.asarray(image.convert('L').resize((self.__width, self.__height)))
        else:
            raise Exception("loading image except for grayscale not supported yet...")

    def __label2array(self, label, labels):
        return labels.index(label)
        # return numpy.array(map(lambda x: 1 if (x == label) else 0, labels))

    """
        check if dirname
        - has /train and /test
        - /train/* and /test/* has same names and numbers
    """
    def __check_dir_tree(self, dirname):
        if self.__type == 'directory':
            if not os.path.isdir(dirname):
                raise Exception("Cannot access directory %s" % dirname)
            train = os.path.join(dirname,"train")
            if not os.path.isdir(train):
                raise Exception("Cannot access directory %s" % train)
            test = os.path.join(dirname,"test")
            if not os.path.isdir(test):
                raise Exception("Cannot access directory %s" % test)
            if set(self.__getdirs(train)) != set(self.__getdirs(test)):
                raise Exception("Directories under /train and /test should be same.")
        elif self.__type == 'zip':
            if not os.path.isfile(dirname):
                raise Exception("Cannot access zip file %s" % dirname)
            else:
                self.__archive = zipfile.ZipFile(dirname, 'r')
                self.__archive_namelist = self.__archive.namelist()
            try:
                self.__archive.getinfo('train/')
            except:
                raise Exception("Cannot access directory /train in %s" % dirname)
            try:
                self.__archive.getinfo('test/')
            except:
                raise Exception("Cannot access directory /test in %s" % dirname)
            train_cats = self.__getdirs('train/')
            test_cats = self.__getdirs('test/')
            if set(train_cats) != set(test_cats):
                raise Exception("Directories under /train and /test should be same.")
        else:
            raise Exception("Unknown type")

    def __getdirs(self, path):
        if self.__type == 'directory':
            dirs=[]
            for item in os.listdir(path):
                if os.path.isdir(os.path.join(path,item)):
                    dirs.append(item)
            return dirs
        elif self.__type == 'zip':
            if not path.endswith('/'):
                path = path+'/'
            return filter(lambda x: x != None,\
                    map(lambda x: re.match("^"+path+"([^/]+)/$", x).group(1) \
                    if re.match("^"+path+"([^/]+)/$", x) \
                    else None, self.__archive_namelist))

    def __getfiles(self, path):
        if self.__type == 'directory':
            files=[]
            for item in os.listdir(path):
                if not os.path.isdir(os.path.join(path,item)):
                    files.append(item)
            return files
        elif self.__type == 'zip':
            if not path.endswith('/'):
                path = path+'/'
            return filter(lambda x: x != None,\
                    map(lambda x: re.match("^"+path+"([^/]+)$", x).group(1) \
                    if re.match("^"+path+"([^/]+)$", x) \
                    else None, self.__archive_namelist))

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
    def __relativepath(self, filepath):
        if self.__type == 'directory':
            return filepath
        elif self.__type == 'zip':
            if filepath.startswith(self.__archivepath):
                filepath = filepath[len(self.__archivepath):]
            if filepath.startswith('/'):
                filepath = filepath[len('/'):]
            return filepath

        else:
            raise Exception("Unknown type")


