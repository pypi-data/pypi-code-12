#!/usr/bin/env python
import numpy as np
import os, time
from stat import *
from helpers import *
import calculator
from controller import *
from bokeh.plotting import figure, curdoc
from bokeh.client import push_session

class Tracker:
    def __init__(self, dE=1.0E-6,log='converge.log', controller='kpts', scheme='one'):
		'''
		:param dE:  Converge criteria
		:param log: test print out
		:param controller: the paramter /variable to test convergency. Default: 'kpts' to test KPOINTS
		:param scheme: the scheme how the "controller" will be updated. Default:  "one" for incremnet of 1 in each direction
		'''
		self.latest_mtime=time.time()
		self.dE= dE
		self.log = log
		self.controller = controller
		self.isConverged = False
		self.kpts=[1,1,1]
		self.E0=0.0
		self.E=0.0
		self.counter=0
		self.r= None
		self.scheme=scheme

	
    def initialize(self):
	    print "initializing"
	    self.E0=self.get_energy()
	    self.E=self.E0.copy()
	    E=self.E.copy()
	    
	    #initialize log file
	    openlog=open(self.log,'w')
	    string=str(self.counter)+'\t'+str(E-self.E0)+'\t'+str(E)+'\t'+str(self.kpts)
	    openlog.write(string+'\n')
	    openlog.close()
	    
	    self.counter += 1
	    
	    #initialize bokeh plot, please use bokeh serve before 
	    self.bokeh_local()
    	
    def controller_update(self): # controller is the parameter for testing convergency e.g. kpts
    	if self.controller=='kpts':
			Step=KptsController(self.kpts, scheme=self.scheme)
			self.kpts=Step.update()
    	
    def get_energy(self):
    	print "launching new calculation"
    	E=calculator.kfunc(self.kpts)
    	time.sleep(2)
    	return E   	

    def run(self):
    	print "running"
    	while not self.isConverged:
    		print "launching new calculation"
    		#kpts_update 
    		self.controller_update()
    		#get current energy
    		E=self.get_energy()
    		
    		#write to log file
    		openlog=open(self.log,'a')
    		string=str(self.counter)+'\t'+str(E-self.E0)+'\t'+str(E-self.E)+'\t'+str(self.kpts)
    		openlog.write(string+'\n')
    		openlog.close()
    		
    		#update figure 
    		self.bokeh_update()
    		
    		if abs(E-self.E) < self.dE:
    			self.isConverged = True

    		self.E = E
    		self.counter += 1
    
    def bokeh_local(self):
    	p=figure()
    	x,y=read_log()
    	print x,y
    	self.r=p.line(x,y,color='navy',line_width=3)
    	session = push_session(curdoc())
    	session.show()
    
    def bokeh_update(self):
        x,y=read_log()
        self.r.data_source.data["x"]=x
        self.r.data_source.data["y"]=y

