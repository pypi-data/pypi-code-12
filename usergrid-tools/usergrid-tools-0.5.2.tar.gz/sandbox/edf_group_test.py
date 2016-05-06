import json
from collections import defaultdict

from usergrid import UsergridQueryIterator

q = UsergridQueryIterator('https://api.usergrid.com/mshar180/sandbox/devices?limit=1000')

fields = defaultdict(int)
tokens = defaultdict(int)
counter = 0

for d in q:
    counter += 1
    if counter % 1000 == 1:
        print json.dumps(fields)
        print json.dumps(tokens)

    for f in d:
        if f == 'androidEDFENews.notifier.id':
            tokens[d[f]] += 1
            print '%s / %s' % (d['uuid'], d[f])

        if f not in fields:
            print 'New Field: %s' % f

        fields[f] += 1

print json.dumps(fields)
print json.dumps(tokens)