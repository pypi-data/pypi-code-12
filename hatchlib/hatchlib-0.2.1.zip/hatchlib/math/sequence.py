def nth_fib(n):
	a,b,c=1,1,0
	for rec in bin(n)[3:]:
		calc=b*b
		a,b,c=a*a+calc,(a+c)*b,calc+c*c
		if rec=='1':a,b,c=a+b,a,b

	return b

def fibonacci(n):
	fibs=[0,1]
	for i in range(2,n+1):
		fibs.append(fibs[-1]+fibs[-2])
	return fibs