'''
Created on 28 sept. 2014

@author: coissac
'''

import orgasm.samples

from orgasm import getOutput,getIndex, getSeeds, getAdapters
from orgasm.tango import matchtoseed, cutLowCoverage, cutSNPs,\
    estimateDeadBrancheLength, estimateFragmentLength,\
    genesincontig, scaffold, fillGaps, dumpGraph, restoreGraph

from orgasm.assembler import Assembler,tango
import sys
import shutil

__title__="copy an assembly"


default_config = { "source" : None,
                   "dest" : None
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:outputfilename',  metavar='outputfilename', 
                        help='name of the assembly to be copied')
    
    parser.add_argument(dest='clone:dest',     metavar='dest', 
                        help='name of the new copy of the assembly' )
    
    


def run(config):
    
    logger=config['orgasm']['logger']
    progress = config['orgasm']['progress']

    source = getOutput(config)
    
    logger.info("Copying the assembly %s to %s" % (config['orgasm']['outputfilename'],
                                                   config['clone']['dest'])) 
        
    shutil.copytree("%s.oas"  % config['orgasm']['outputfilename'], 
                    "%s.oas"  % config['clone']['dest'])
    
    
