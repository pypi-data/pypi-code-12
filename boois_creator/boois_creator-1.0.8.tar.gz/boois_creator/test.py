import json  
from collections import OrderedDict
text='''{
    "xx":"sdfs",
    "cxx1":"sdfs",
    "bxx2":"sdfs",
    "axx3":"sdfs"
}'''
arr=json.loads(text)
for k,v in arr.items():
    print k,v
print "-"*40
metadata = json.loads(text, object_pairs_hook=OrderedDict)
for k,v in metadata.items():
    print k,v