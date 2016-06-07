# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 08:53:53 2015

@author: pkiefer
Multiprocessing
Multiprocssing requires import of the multiprocessing function and cannot be executed via runfile

the concept of using the function run_parallel:
    assuming you have a sequential process like e.g
    def process(values, args, kwargs):
        result=[]
        for v in in values:
            result.append(fun(v, *args, **kwargs))
    return result

To perform multiprocessing:
    
(1) nest the function fun
    
(2) create parameter tuples for nested fun

(3) execute the nested function in a multicore process
        
"""
import sys
from multiprocessing import Pool, cpu_count, set_executable
import time
if sys.platform == "win32":
        # if subprocesses use python.exe a console window pops up for each
        # subprocess. this is quite ugly..
        import os.path
        set_executable(os.path.join(os.path.dirname(sys.executable), "pythonw.exe"))

def build_input(values, fun, args, kwargs):
    return [(fun, v,  args, kwargs) for v in values]


def nested(params):
    fun, v, args, kwargs = params
    return fun(v, *args, **kwargs)
    

def run_parallel(args, cpus=None):
    # all parameter arguments must have the same length
    cpus=num_cpus(args, cpus)
    start=time.time()
    if cpus>1:
        # only switch to multiprocessing if more than 1 cpu is used
        pool=Pool(processes=cpus)
        result=pool.map(nested, args)
        pool.close()
        pool.join()
    else:
        result=[nested(arg) for arg in args]
    print 'took %.3fs' %(time.time()-start)
    return result

def num_cpus(args, cpus):
    if not cpus:
        cpus=len(args)
    max_cpus=cpu_count()-1
    cpus=cpus if cpus<max_cpus else max_cpus
    print 'number of cores:', cpus    
    return cpus
 
   
def main_parallel(fun, values, args=list(), kwargs=dict(), cpus=None):
    """ fun, values: list or tuple
    """
    params = build_input(values, fun, args, kwargs)
    return run_parallel(params, cpus=cpus)    
    
#################################################
def process(values):
    v1,v2=values
    time.sleep(0.1)
    return v1*v2
    
def check():
    main_parallel(process, zip(range(10),range(10)))