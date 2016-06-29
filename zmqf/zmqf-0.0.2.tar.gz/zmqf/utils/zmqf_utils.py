#coding=utf-8
'''
Created on 2016年3月4日
'''
import sys
import traceback
import re
__author__ = 'chenjian'

def trace_error():
    '''
    trace exception info, output in sys.stdout
    '''
    
    etype, evalue, tracebackObj = sys.exc_info()[:3]
    print("Type: " , etype)
    print("Value: " , evalue)
    traceback.print_tb(tracebackObj)
    
def parse_url(url):
    '''
    :param url: [protocol]://[host]:[port][uri]
    :return protocol, host, port, uri
    '''
    
    reg = r'(?P<protocol>\w+)://(?P<host>[\w\.]+)((:(?P<port>\d+))?(/(?P<uri>.*))?)?'
    m = re.match(reg, url)
    
    return m.group('protocol'), m.group('host'),  int(m.group('port') and m.group('port') or 80), '/' + (m.group('uri') and m.group('uri') or '')