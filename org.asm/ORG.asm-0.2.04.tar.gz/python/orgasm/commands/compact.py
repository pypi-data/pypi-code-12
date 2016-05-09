'''
Created on 28 sept. 2014

@author: coissac
'''

import orgasm.samples

from orgasm import getIndex, getSeeds,getOutput
from orgasm.tango import cutLowCoverage, cutSNPs,\
    estimateDeadBrancheLength, estimateFragmentLength,\
    genesincontig, scaffold, fillGaps, dumpGraph, restoreGraph

import sys


__title__="Recompact the assembling graph"
 
default_config = { 'seeds' : None
                 }


def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='output', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    
    
    parser.add_argument('--back',             dest='orgasm:back', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')
    


def run(config):
    
    logger=config['orgasm']['logger']
    output = getOutput(config)
    
    r = getIndex(config)
    coverage,x,newprobes = getSeeds(r,config)  
    
    asm = restoreGraph(output+'.oax',r,x)
    meanlength,sdlength = estimateFragmentLength(asm)

    if config['orgasm']['back'] is not None:
        back = config['orgasm']['back']
    elif config['orgasm']['back'] is None and meanlength is not None:
        back = int(meanlength + 4 * sdlength)
        if back > 500:
            back=500
    else:
        back = 300
        
    if meanlength is not None:
        logger.info("Fragment length estimated : %f pb (sd: %f)" % (meanlength,sdlength))

        
    cg = asm.compactAssembling(verbose=False)
    logger.info("Scaffold the assembly")
    scaffold(asm,cg,minlink=5,back=int(back),addConnectedLink=False)
    genesincontig(cg,r,x)
    with open(output+'.gml','w') as gmlfile:
        print(cg.gml(),file=gmlfile)
