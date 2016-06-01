from hashlib import md5

def binary(seq,key):
	l,h=0,len(seq)-1

	while h>=l:
		m=l+(h-l)//2

		if seq[m]<key: l=m+1
		elif seq[m]>key: h=m-1
		else: return m
	return False

def kmp(s,sub):
	from hatchlib.search.kmp_ext import prefix
	offsets=[]

	if len(sub)>len(s):
		return offsets

	pfx,q=prefix(word),0
	for i,c in enumerate(s):
		while q>0 and word[q]!=c: q=pfx[q-1]
		if word[q]==c: q+=1
		if q==len(sub):
			offsets.append(index-len(sub)+1)
			q=pfx[q-1]
			
	return offsets

def rabin_karp(s,sub):
	if len(sub)>len(s): return []
	hsub_digest,offsets=md5(sub.encode('utf-8')).digest(),[]

	for i in range(len(s)-len(sub)+1):
		if md5(s[i:i+len(sub)].encode('utf-8')).digest()==hsub_digest:
			if s[i:i+len(sub)]==sub: offsets.append(i)

	return offsets