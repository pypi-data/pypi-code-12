#coding=utf-8
'''
Created on 2016年3月3日
'''
from zmqf.client import zmqf_client
from zmqf.core.base import ZmqfPattern
__author__ = 'chenjian'

def main(server_addr="tcp://localhost:5555"):
    
    print zmqf_client.request(server_addr, json={"a": 1}, pattern=ZmqfPattern.MRER)

if __name__ == '__main__':
    main()