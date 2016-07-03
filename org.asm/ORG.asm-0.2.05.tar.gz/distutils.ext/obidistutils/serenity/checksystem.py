'''
Created on 24 mai 2015

@author: coissac
'''

from distutils import util

def is_mac_system():
    platform = util.get_platform().split('-')[0]
    
    return platform=='macosx'

def is_windows_system():
    platform = util.get_platform().split('-')[0]
    
    return platform=='Windows'
        