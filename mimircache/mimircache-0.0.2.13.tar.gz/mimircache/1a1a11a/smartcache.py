from pprint import pprint

from mimircache.cacheReader.plainReader import plainCacheReader
from mimircache.profiler.LRUProfiler import LRUProfiler

# reader = plainCacheReader('../data/test')
# p = pardaProfiler(5, reader, 1)
# for i in p.get_reuse_distance():
#     print(i)

reader2 = plainCacheReader('../data/trace.txt')
l = []
for e in reader2:
    l.append(e)

l.reverse()
l2 = []
removed_set = set()
for e in l:
    if e not in removed_set:
        removed_set.add(e)
    else:
        l2.append(e)

# print(l2)


with open('../data/trace.txt.reversed', 'w') as ofile:
    for e in l2:
        ofile.write(str(e) + '\n')

reader = plainCacheReader('../data/trace.txt.reversed')


p = LRUProfiler(2000, reader)
# p = pardaProfiler(2000, reader)
pprint(p.get_reuse_distance())
print(reader.get_num_total_lines())
print(len(p.get_reuse_distance()))
print(max(p.get_reuse_distance()))
print(min(p.get_reuse_distance()))
# with open("rd4.txt", 'w') as ofile:
#     for rd in p.get_reuse_distance():
#         print(rd)
#         ofile.write(str(rd) + '\n')