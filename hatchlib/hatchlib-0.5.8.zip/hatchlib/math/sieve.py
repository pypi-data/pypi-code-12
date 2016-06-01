from math import sqrt

def erat(lim):
	base=[2,3]
	base.extend(range(5,lim+1,2))

	for i in range(1,len(base)-1):
		if base[i]==0: continue
		
		for j in range(i+base[i],len(base)-1,base[i]):
			base[j]=0

	return [i for i in base if i!=0]

def atkin(lim):
	if lim<6: return erat(lim)
	primes=[2,3,5]
	isprime,s_lim=[False]*(lim+1),int(sqrt(lim))+1

	for a in range(1,s_lim):
		for b in range(1,s_lim):
			n=4*a**2+b**2
			if n<=lim and (n%12==1 or n%12==5): isprime[n]=not isprime[n]
			
			n=3*a**2+b**2
			if n<=lim and n%12==7: isprime[n]=not isprime[n]
			
			n=3*a**2-b**2
			if a>b and n<=lim and n%12==11: isprime[n]=not isprime[n]

	for i in range(5,s_lim):
		for c in range(i*i,lim,i*i):
			isprime[c]=False

	for i in range(7,lim):
		if isprime[i]: primes.append(i)

	return primes