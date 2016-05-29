from random import randint
from math import pi,e,sqrt

def lcm(a,b):
	t=a
	while t%b!=0: t+=a
	return t

def isprime(n):
	if n==1: return False

	for i in range(3):
		rn=randint(2,n)-1
		if pow(rn,n-1,n)!=1: return False

	return True

def nth_fib(n):
	a,b,c=1,1,0

	for r in bin(n)[3:]:
		calc=b*b
		a,b,c=a*a+calc,(a+c)*b,c*c+calc

		if r=='1': a,b,c=a+b,a,b

	return b