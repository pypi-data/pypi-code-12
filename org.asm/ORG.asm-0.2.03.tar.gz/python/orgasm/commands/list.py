'''
Created on 28 sept. 2014

@author: coissac
'''
from orgasm import getIndex

__title__="List information about a read index"

default_config = { 
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the oa index command)')
    


def run(config):

    r = getIndex(config)
    
    print(len(r),r.getReadSize())

              
