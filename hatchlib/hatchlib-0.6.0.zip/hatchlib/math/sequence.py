def hailstone(n):
	seq=[n]

	while n>1:
		n=3*n+1 if n&1 else n//2
		seq.append(n)

	return seq

def nth_fib(n):
	if n==0: return 0

	a,b,c=1,1,0
	for rec in bin(n)[3:]:
		calc=b*b
		a,b,c=a*a+calc,(a+c)*b,calc+c*c
		if rec=='1':a,b,c=a+b,a,b

	return b

def fibonacci(n):
	fibs=[1,1]
	for i in range(2,n):
		fibs.append(fibs[-1]+fibs[-2])
	return fibs