import os as o
import sys as s
import subprocess as sub


def isFile(file):
    if(o.path.isfile(file)):
        return True
    return False

def isFolder(folder):
    if(o.path.isdir(folder)):
        return True
    return False

def checkFile(file):
    if( isFolder(file) ):
        return False
    elif(not isFile(file) ):
        return False
    return True

def getFileExtension(file):
    temp = ""
    i = len(file)-1
    while(file[i] is not '.'):
        if(file[i] is '/'):
            return ''
        temp += file[i]
        i -= 1
    return temp[::-1]

def getFileName(file):
    temp = ""
    i = len(file)-1
    while(file[i] is not '/'):
        temp += file[i]
        i-=1

    return temp[::-1]

def getFilenameWithoutExtension(file):
    return getFileName(file).split("."+getFileExtension(file))[0]

def getDirectoryList(file):

    fn = getFileName(file)
    lis = file.replace(fn, '').split('/')
    lis.remove('')
    lis.remove('')
    return lis

def getFileList(curDir):
    lis = list()

    if(not o.path.isdir(curDir)):
        return list()

    if(curDir[len(curDir)-1] != '/'):
        curDir += '/'

    fileList = str(sub.check_output(["ls", curDir]))
    if(len(fileList) <= 0):
        return list()
    if('3.5' in s.version):
        fileList = fileList[2:len(fileList)-1]
        fileList = fileList.split('\\n')
        fileList.remove('')
    elif('2.7' in s.version):
        fileList = fileList.split('\n')
        fileList.remove('')

    for i in fileList:

        if(o.path.isfile(curDir + i)):
            lis.append(curDir + i)
        elif(o.path.isdir(curDir+i)):
            recurLis = getFileList(curDir+i+'/')
            for j in recurLis:
                lis.append(j)
    return lis