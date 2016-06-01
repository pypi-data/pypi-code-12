from random import randint
from math import pi,e,sqrt

def lcm(a,b):
	t=a
	while t%b!=0: t+=a
	return t

def euclid(a,b):
	while b!=0: a,b=b,a%b
	return a

def coprime(*n):
	if len(n)==2: return euclid(n[0],n[1])==1
	l=1

	for i in range(0,len(n)-1,2):
		c=euclid(n[i],n[i+1])
		if c!=1 or euclid(l,c)!=1: return False
		l=c

	return True

def isprime(n):
	if n==1: return False

	for i in range(3):
		rn=randint(2,n)-1
		if pow(rn,n-1,n)!=1: return False

	return True