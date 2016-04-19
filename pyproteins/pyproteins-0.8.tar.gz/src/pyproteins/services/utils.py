import sys
import os
import errno
import StringIO
import re
import os.path
from types import ModuleType
import stat



def getAvailableTagFile(fPath, nLim=100):
    if os.path.isfile(fPath):
        backUpFileRoot = fPath + '.old'
        backUpFile = backUpFileRoot
        if os.path.isfile(backUpFile):
            for i in range(1, nLim):
                if os.path.isfile(backUpFileRoot + '_' + str(i)):
                    continue
                else:
                    backUpFile = backUpFileRoot + '_' + str(i)
                    break
                raise ValueError, 'Tag number limit exceeded for ' + fPath

        print 'moving previous ' + fPath + ' to ' + backUpFile
        os.rename(fPath, backUpFile)
    return fPath



# inject carriage returns in long string to obtain mutliline fixed width lines
def lFormat(string, nCol=60):
    return ''.join([x+'\n' if (i+1)%nCol == 0 else x for i,x in enumerate(string) ])


# from http://stackoverflow.com/questions/12791997/how-do-you-do-a-simple-chmod-x-from-within-python
def chmodX(filePath):
    st = os.stat(filePath)
    os.chmod(filePath, st.st_mode | stat.S_IEXEC)

def checkEnv(keyList):
    for key in keyList:
        if not os.environ.get(key):
            raise ValueError("Environment variable " + key + " not defined")
    return True


# emulates find unix command
def find(sType='file', **kwargs):

    patt = kwargs['name'].replace("*", ".*")
    if 'path' not in kwargs and 'name' not in kwargs:
        raise ValueError
    if sType == 'file':
        result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(kwargs['path']) for f in filenames if re.match(patt, f)]

    if sType == 'dir':
        result = [os.path.join(dp, d) for dp, dn, filenames in os.walk(kwargs['path']) for d in dn if re.match(patt, d)]

    return result


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def toInStream(inputData):
    if hasattr(inputData, 'read'):
        return inputData
    if os.path.isfile(inputData):
        f = open(inputData, 'r')
        return f

    return StringIO.StringIO(inputData)

def hasMethod(obj, askedMethod):
    l = [method for method in dir(obj) if callable(getattr(obj, method))]
    if askedMethod in l:
        return True
    return False

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise





def rreload(module):
    """Recursively reload modules."""
    reload(module)
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if type(attribute) is ModuleType:
            rreload(attribute)

'''
    parse a tsv file into a list of dictionary, dictionary keys are extracted from the first line (aka column headers)
'''

def tsvToDictList(fileName):
    buffer = tabularFileToList(fileName, separator = "\t")
    print len(buffer)
    keymap = buffer.pop(0)
    print len(buffer)
    data = []
    for d in buffer:
        data.append({})
        for i,x in enumerate(d):
            data[-1][keymap[i]] = x

    return {'keymap' : keymap, 'data' : data}

def tabularFileToList(fileName, separator = ","):

    with open (fileName, "r") as f:
        data = [line.strip('\n').split(separator) for line in f]

    return data