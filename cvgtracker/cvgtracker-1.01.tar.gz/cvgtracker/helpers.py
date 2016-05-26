import os, time

def read_log(log='converge.log', n1=0, n2=1):  #read the "converge.log"file to plot trend
	
	try:
		openlog = open(log,"r")
	except IOError:
		print " %s is missing ", log_file
			
	data= openlog.read().split('\n')
	openlog.close()
	xar =[]
	yar =[]
	for line in data:
		if len(line) > 1:
			a= line.split('\t')
			x=a[n1]
			y=a[n2]
			xar.append(float(x))
			yar.append(float(y))
	return xar, yar
    
        

