'''
Created on 2 oct. 2014

@author: coissac
'''

from distutils import util
from distutils import log

def is_mac_system():
    platform = util.get_platform().split('-')[0]
    if platform=='macosx':
        log.info('You are running on a Mac platform')
    return platform=='macosx'

def is_windows_system():
    platform = util.get_platform().split('-')[0]
    
    return platform=='Windows'
