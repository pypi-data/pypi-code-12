from hatchlib.math import isprime
from random import randint
from fractions import gcd

def f(x): return x*x+1

def rho(n,a=2,b=2):
	if n%2==0: return 2
	i=0
	while 1:
		a=f(a)%n
		b=f(f(b))%n
		
		div=gcd(abs(a-b),n)
		i+=1
		
		if div!=1: break
		
		if i>500:
			a,b,i=randint(1,10),randint(1,10),1
	return div

def pollard_rho_rec(x,factors):
	if x==1: return

	if isprime(x):
		factors.append(x)
		return

	div=rho(int(x),randint(1,10),randint(1,10))
	pollard_rho_rec(int(div),factors)
	pollard_rho_rec(int(x/div),factors)