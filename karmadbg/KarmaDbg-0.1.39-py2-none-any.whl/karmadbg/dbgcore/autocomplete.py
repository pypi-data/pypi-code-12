
import shlex
import glob
import re
import string
import os

def autoComplete(str):
    res = autoCompleteFilePath(str)
    if res: return res

    return None


def autoCompleteFilePath(competeStr):

    try:

        if not competeStr:
            return None

        for secondTime in (False, True):

            try:

                shl = shlex.shlex(competeStr, posix=True)
                shl.escape = []
                shl.wordchars = string.digits + string.ascii_letters + r"!#$%&()*+,-./:;<=>?@[\]^_`{|}~"
                token =list(shl)[-1]
                break

            except ValueError:
                competeStr += "\""

        pathLst = glob.glob(token + "*")
        if len(pathLst) == 0:
            return None

        commonPrefix = os.path.commonprefix(pathLst)[len(token):]

        if commonPrefix and os.path.isdir(token + commonPrefix):
            commonPrefix += "/"

        hintsLst = []
        for path in pathLst:
            if os.path.isfile(path):
                hintsLst.append( ("file", os.path.split(path)[1],) )
            else:
                hintsLst.append( ("dir", os.path.split(path)[1],) )

        return ( "filePath", commonPrefix, hintsLst)

    except:

        return None

