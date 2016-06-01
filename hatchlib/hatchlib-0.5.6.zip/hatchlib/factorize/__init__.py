from hatchlib.math.sieve import erat
from hatchlib.factorize.pr import *
from math import sqrt

def fermat(n):
	if n&1==0: return [n>>1,2]
	x=int(sqrt(n))
	
	if x*x==n: return [x,x]
	x+=1

	while 1:
		a=x*x-n
		b=int(sqrt(a))

		if b*b==a: break

	return [x-b,x+b]

def pollard_rho(x):
	if x in [0,1]: return [x]
	factors=[]
	pollard_rho_rec(x,factors)
	return factors

def trial_div(n):
	pfactors=[]
	if n<2: return pfactors
	
	for p in erat(int(sqrt(n))+1):
		if p*p>n: break
		while n%p==0:
			pfactors.append(p)
			n//=p

	if n>1:
		pfactors.append(n)
	return pfactors