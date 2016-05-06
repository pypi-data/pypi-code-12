import json
from collections import defaultdict

from usergrid import UsergridQueryIterator

q = UsergridQueryIterator('https://api.usergrid.com/mshar180/sandbox/devices?limit=1000')

fields = defaultdict(int)
counter = 0

for d in q:
    counter += 1
    if counter % 1000 == 1:
        print json.dumps(fields)

    for f in d:
        if f not in fields:
            print 'New Field: %s' % f

        fields[f] += 1

print json.dumps(fields)