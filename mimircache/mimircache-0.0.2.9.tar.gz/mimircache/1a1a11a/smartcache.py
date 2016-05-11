from mimircache.cache.LRU import LRU
from mimircache.cacheReader.plainReader import plainCacheReader
from mimircache.cacheReader.csvReader import csvCacheReader
from mimircache.profiler.abstract.abstractLRUProfiler import abstractLRUProfiler
from mimircache.profiler.pardaProfiler import pardaProfiler, parda_mode


reader = plainCacheReader('../data/test')
p = pardaProfiler(5, reader, 1)
for i in p.get_reuse_distance():
    print(i)
