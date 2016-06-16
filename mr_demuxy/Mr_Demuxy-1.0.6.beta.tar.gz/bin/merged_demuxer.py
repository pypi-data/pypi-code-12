# -*- coding: utf-8 -*-
'''
Created on Fri Feb 12 19:00:29 2016

@author: Daniel Lefever
@email: lefeverd@uga.edu


'''
#!/usr/bin/python

from __future__ import division

from mr_demuxy import merged_demuxer_dist

def main():
    merged_class = merged_demuxer_dist.MergedDemuxer()
    merged_class.main_loop()
    
if __name__ == '__main__':
    main()

