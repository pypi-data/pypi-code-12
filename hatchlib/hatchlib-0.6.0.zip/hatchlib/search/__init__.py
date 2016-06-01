from hashlib import md5

def binary(seq,key):
	l,h=0,len(seq)-1

	while h>=l:
		m=l+(h-l)//2

		if seq[m]<key: l=m+1
		elif seq[m]>key: h=m-1
		else: return m
	return False

def rabin_karp(s,sub):
	if len(sub)>len(s): return []
	hsub_digest,offsets=md5(sub.encode('utf-8')).digest(),[]

	for i in range(len(s)-len(sub)+1):
		if md5(s[i:i+len(sub)].encode('utf-8')).digest()==hsub_digest:
			if s[i:i+len(sub)]==sub: offsets.append(i)

	return offsets