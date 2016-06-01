def cocktail(seq):
	lb,ub,swap=-1,len(seq)-1,True

	while swap:
		swap=False
		lb+=1

		for i in range(lb,ub):
			if seq[i]>seq[i+1]:
				seq[i],seq[i+1]=seq[i+1],seq[i]
				swap=True

		if not swap: break

		swap=False
		ub-=1

		for i in range(ub,lb,-1):
			if seq[i]<seq[i-1]:
				seq[i],seq[i-1]=seq[i-1],seq[i]
				swap=True

		return seq

def gnome(seq):
	i,l=1,0

	while i<len(seq):
		if seq[i]<seq[i-1]:
			seq[i],seq[i-1]=seq[i-1],seq[i]
			if i>1:
				if l==0: l=1
				i-=1
			else:
				i+=1
		else:
			if l!=0:
				i,l=l,0
			i+=1

	return seq

def insertion(seq):
	for n in range(1,len(seq)):
		item,hole=seq[n],n

		while hole>0 and seq[hole-1]>item:
			seq[hole]=seq[hole-1]
			hole-=1
		seq[hole]=item

	return seq

def quicksort(seq):
	if len(seq)<=1: return seq
	
	pivot=seq[0]
	l,r=[],[]
	for i in seq[1:]:
		if i<pivot: l.append(i)
		else: r.append(i)

	return quicksort(l)+[pivot]+quicksort(r)

def selection(seq):
	for i in range(0,len(seq)):
		m=i
		for j in range(i+1,len(seq)):
			if seq[m]>seq[j]: m=j

	if i!=m: seq[i],seq[m]=seq[m],seq[i]

	return seq