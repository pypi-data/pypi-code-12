import sys
import re
from os import listdir

def split(fp, nSplit=10):
    f = open(fp, 'r')
    n = 0
    for _ in f:
        n += 1
    f.close()

    f_i = open(fp, 'r')
    i = 0
    c = 0
    for line in f_i:
        i += 1
        if i > (n / nSplit + 1) * c:
            c += 1
            print c
        f_o = open('_'.join([fp.split('.')[0], str(c)]), 'a')
        f_o.write(line.strip() + '\n')
        f_o.close()

    f_i.close()


def merge(fp):
    file = fp.split('/')[-1]
    folder = re.sub(file, '', fp)
    o = open(fp, 'a')
    for f in listdir(folder):
        if f.startswith(file):
            i = open(folder + f, 'r')
            for line in i:
                o.write(line.strip() + '\n')
            i.close()
    o.close()

# merge('/Users/cchen224/Downloads/CustomerName_clean')


if __name__ == '__main__':
    argvs = sys.argv[1:]
    fp = argvs[0]
    try:
        nSplit = argvs[1]
        split(fp, int(nSplit))
    except:
        split(fp)


# from os import listdir
# folder = '/Users/cchen224/Downloads/followers/'
# files = listdir(folder)
# o = open(folder + 'server1', 'a')
# list = []
# for file in files:
#     f = open(folder + file, 'r')
#     for line in f:
#         line = line.strip()
#         if line not in list:
#             list.append(line)
#             o.write(line + '\n')
#     f.close()
# len(list)
# o.close()