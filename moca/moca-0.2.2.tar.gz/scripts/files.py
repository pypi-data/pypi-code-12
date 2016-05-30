import os
__root_dir__ = '/media/data1/encode_analysis'

for d in os.listdir(__root_dir__):

    bedfiles = []
    for f in os.listdir(os.path.join(__root_dir__, d)):
        if os.path.splitext(f)[1] == '.sorted':
            bedfiles.append(f)

    if len(bedfiles) != 1:
        print d, bedfiles

