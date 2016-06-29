import sys
import re
from os import listdir
from glob import glob

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


def merge(fp_in, fp_out):
    with open(fp_out, 'w') as o:
        for file in glob(fp_in):
            with open(file, 'r') as i:
                lines = [line for line in i]
            [o.write(line) for line in lines]


from glob import glob
import os
import csv
def merge_with_delete(fp, outname):
    files = glob(fp)
    with open(outname, 'a') as o:
        csvwriter = csv.writer(o, delimiter=',', quotechar='"')
        for file in files:
            with open(file, 'r') as i:
                csvreader = csv.reader(i, delimiter=',', quotechar='"')
                for row in csvreader:
                    csvwriter.writerow(row)
            os.remove(file)



def merge_followers(fp, outname):
    from os import listdir, path
    files = listdir(fp)
    o = open(path.join(fp,outname), 'a')
    for file in files:
        i = open(path.join(fp, file), 'r')
        for line in i:
            o.write(file.split('.')[0] + '\t' + line.strip() + '\n')
        i.close()
    o.close()
    print 'Done'

# merge_followers('/Users/cchen224/Downloads/f17/', 'followers17')

# merge('/Users/cchen224/Downloads/CustomerName_clean')


# if __name__ == '__main__':
#     argvs = sys.argv[1:]
#     fp = argvs[0]
#     try:
#         nSplit = argvs[1]
#         split(fp, int(nSplit))
#     except:
#         split(fp)

# split('/Users/cchen224/Downloads/followers/server1', 18)

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


from os import listdir, path
def merge1(fp, outname):
    out = dict()
    files = listdir(fp)

    for file in files:
        i = open(path.join(fp, file), 'r')
        for line in i:
            try:
                out[str(int(line.strip().split('\t')[1]))] = 1
            except:
                pass
            # o.write(line.strip().split('\t') + '\n')
        i.close()

    o = open(path.join(fp, outname), 'a')
    for item in out.keys():
        o.write(item + '\n')
    o.close()

# merge1('/Users/cchen224/Downloads/2/', '2')

# import random
# i = open('/Users/cchen224/Downloads/user_ids', 'r')
# nLine = 0
# for line in i:
#     if random.uniform(0,1) < 0.007 and nLine < 1000000:
#         nLine += 1
#         o = open('/Users/cchen224/Downloads/user_ids.sample', 'a')
#         o.write(line.strip() + '\n')
#         o.close()
# i.close()

# split('/Users/cchen224/Downloads/user_ids.sample', 20)

# with open('/Users/cchen224/Downloads/instagram_media_users.txt', 'a') as o:
#     with open('/Users/cchen224/Downloads/instagram_media.csv', 'r') as i:
#         csvreader = csv.reader(i)
#         test = dict()
#         for row in csvreader:
#             user_id = row[0]
#             if user_id not in test:
#                 test[user_id] = 1
#                 o.write(user_id + '\n')

# import random
# samples = dict()
# with open('/Users/cchen224/Downloads/user_ids_f/user_ids.sample', 'r') as s:
#     for row in s:
#         samples[row.strip()] = 1
#
# with open('/Users/cchen224/Downloads/user_ids_f/user_ids', 'r') as i:
#     total = [row.strip() for row in i]
#
# with open('/Users/cchen224/Downloads/user_ids_f/user_ids.sample2', 'a') as o:
#     counter = 0
#     for id in total:
#         if random.uniform(0,1) < 0.1:
#             counter += 1
#             o.write(id + '\n')
#         if counter >= 5000000:
#             break
