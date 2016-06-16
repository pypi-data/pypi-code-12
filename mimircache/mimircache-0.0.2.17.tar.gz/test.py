#!/usr/bin/python3
import time
import sys


import c_cacheReader 
import c_LRUProfiler 
# cReader = c_cacheReader.setup_reader('test.dat', 'p')
# cReader = c_cacheReader.setup_reader('test2.dat', 'p')
cReader = c_cacheReader.setup_reader('mimircache/data/trace_CloudPhysics_bin', 'v')
# e = c_cacheReader.read_one_element(cReader)
# e2 = c_cacheReader.read_one_element(cReader2)
# for i in range(20):
# 	print(i)
# 	while (e):
# 		if (int(e) != int(e2)):
# 			print("ERROR, " + e + ':' +str(e2))
# 		e = c_cacheReader.read_one_element(cReader)
# 		e2 = c_cacheReader.read_one_element(cReader2)
# 	c_cacheReader.reset_reader(cReader)
# 	c_cacheReader.reset_reader(cReader2)
# 	e = c_cacheReader.read_one_element(cReader)
# 	e2 = c_cacheReader.read_one_element(cReader2)

# cReader = c_cacheReader.setup_reader('../../../../../data/trace_CloudPhysics_bin', 'v')
print(c_cacheReader.get_num_of_lines(cReader)) 
print(c_LRUProfiler.get_hit_count_seq(cReader, 8, begin=0, end=int(sys.argv[1])))
print(c_LRUProfiler.get_hit_rate_seq(cReader, 5))
print(c_LRUProfiler.get_miss_rate_seq(cReader, -1))
# print(c_LRUProfiler.get_reuse_dist_seq(cReader, begin=int(sys.argv[1]), end=int(sys.argv[2])))
for i in range(20):
	print(c_LRUProfiler.get_hit_count_seq(cReader, 0, int(sys.argv[1]), int(sys.argv[2])))
	# print(c_LRUProfiler.get_rd_distribution_seq(cReader, int(sys.argv[1]), int(sys.argv[2])))

# time.sleep(1)
c_cacheReader.close_reader(cReader)
# a = 1 