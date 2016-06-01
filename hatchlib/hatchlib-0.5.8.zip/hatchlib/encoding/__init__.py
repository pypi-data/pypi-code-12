from heapq import heappush,heappop,heapify
from sys import version_info

if version_info[0]==2: from collections import defaultdict
else: from collections import Counter

def huffman(s):
	if version_info[0]==2:
		stf=defaultdict(int)
		for c in s: stf[c]+=1
	else:
		stf=Counter(s)

	heap=[[w,[sym,'']] for sym,w in stf.items()]
	heapify(heap)

	while len(heap)>1:
		l=heappop(heap)
		h=heappop(heap)

		for pair in l[1:]: pair[1]='0'+pair[1]
		for pair in h[1:]: pair[1]='1'+pair[1]

		heappush(heap,[l[0]+h[0]]+l[1:]+h[1:])

	tree={}
	for pair in sorted(heappop(heap)[1:],key=lambda p:(len(p[-1]),p)):
		tree[pair[0]]=pair[1]

	return tree	