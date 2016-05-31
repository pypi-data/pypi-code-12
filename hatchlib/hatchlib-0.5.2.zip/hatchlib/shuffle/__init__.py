from random import seed,randint

def knuth(seq):
	seed()

	for i in reversed(range(len(seq))):
		j=randint(0,i)
		seq[i],seq[j]=seq[j],seq[i]

	return seq