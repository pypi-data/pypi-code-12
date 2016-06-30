#coding=utf-8
'''
Created on 2016年3月4日
'''
import sys
import traceback
__author__ = 'chenjian'

def trace_error():
    '''
    trace exception info, output in sys.stdout
    '''
    
    etype, evalue, tracebackObj = sys.exc_info()[:3]
    print("Type: " , etype)
    print("Value: " , evalue)
    traceback.print_tb(tracebackObj)