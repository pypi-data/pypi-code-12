# make_codes.py

import os, time
from glob import glob
from bl.id import random_id

path = os.path.dirname(os.path.abspath(__file__))
codesfns = glob(os.path.join(path, "codes", "*-codes.txt"))
allcodes = []
for fn in codesfns:
    t = Text(fn)
    allcodes += t.text.split('\n')
    assert len(allcodes) == len(list(set(allcodes)))

inp = input("Number of codes to make: ")
batch = input("Batch label: ") 
if inp.strip()!='':
    num = int(inp)
    fn = os.path.join(path, time.strftime("%Y%m%d")+"_%d_%s.txt"%(num, batch.strip(),))
    try:
        assert not os.path.exists(fn)
    except:
        print("ALREADY EXISTS --", fn)
        exit(1)
    print(fn)
    codes = []
    for i in range(num):
        c=random_id(12)
        code = c[:4]+'-'+c[4:8]+'-'+c[8:]
        codes.append(code)
    assert len(allcodes+codes) == len(list(set(allcodes+codes)))
    t = Text(fn)
    t.text = '\n'.join(codes)
    t.write()
