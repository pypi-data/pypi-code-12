from os import listdir
import re
from cutils import ProgressBar


# def unique(list):
#     out = dict()
#     for item in list:
#         out[item] = 1
#     return out.keys()

def get_unique_from_folder(fp, outname):

    fp = re.sub('//', '/', fp + '/')
    files = listdir(fp)
    bar = ProgressBar(total = len(files))
    out = dict()
    for file in files:
        i = open(fp + file, 'r')
        bar.move().log()
        for line in i:
            out[line.strip()] = 1
        i.close()
    bar.close()
    o = open(fp + outname, 'a')
    for item in out.keys():
        o.write(item + '\n')

# get_unique_from_folder('/Users/cchen224/Downloads/f12/', '_followers12')