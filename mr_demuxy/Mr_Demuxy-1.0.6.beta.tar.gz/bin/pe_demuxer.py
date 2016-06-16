# -*- coding: utf-8 -*-
'''
Created on Fri Feb 12 19:00:29 2016

@author: Daniel Lefever
@email: lefeverd@uga.edu


'''
#!/usr/bin/python

from __future__ import division

from mr_demuxy import pe_demuxer_dist

def main():
    pe_class = pe_demuxer_dist.PEDemux()
    pe_class.main_loop()
if __name__ == '__main__':
    main()

