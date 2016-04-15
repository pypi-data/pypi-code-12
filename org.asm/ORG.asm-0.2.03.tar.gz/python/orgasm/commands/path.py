'''
Created on 28 sept. 2014

@author: coissac
'''

import sys

from orgasm import getOutput,getIndex, getSeeds
from orgasm.tango import restoreGraph, estimateFragmentLength, genesincontig,\
     scaffold, path2fasta

__title__="Build a fasta file from a path across the assembling graph"

default_config = { 
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='<index>', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='<output>', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    
    parser.add_argument('--path',             dest='path:path', 
                                              action='store',
                                              metavar='<edgeid>',
                                              type=int, 
                                              nargs='+', 
                                              required=True,
                                              default=None, 
                        help='A list of edge id separated by space add -- at the end of the path')

    
    parser.add_argument('--back',             dest='orgasm:back', 
                                              metavar='<insert size>',
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')

    parser.add_argument('--set-tag','-S',     dest ='fasta:tags', 
                                              metavar='tag', 
                                              action='append',
                                              default=[], 
                                              type=str, 
                        help='Allows to add a tag in the OBITools format '
                             'to the header of the fasta sequences')



def run(config):

    logger=config['orgasm']['logger']
    output = getOutput(config)

    r = getIndex(config)
    ecoverage,x,newprobes = getSeeds(r,config)  
    
    asm = restoreGraph(output+'.oax',r,x)

    logger.info("Evaluate fragment length")
    
    meanlength,sdlength = estimateFragmentLength(asm)
    
    if meanlength is not None:
        logger.info("Fragment length estimated : %f pb (sd: %f)" % (meanlength,sdlength))

    if config['orgasm']['back'] is not None:
        back = config['orgasm']['back']
    elif config['orgasm']['back'] is None and meanlength is not None:
        back = int(meanlength + 4 * sdlength)
        if back > 500:
            back=500
    else:
        back = 300

    cg = asm.compactAssembling(verbose=False)
    
    genesincontig(cg,r,x)

    scaffold(asm,cg,minlink=config['orgasm']['minlink'],
             back=int(back),addConnectedLink=False)

#    fastaout = open(output+".fasta","w")
    fastaout = sys.stdout
    pathout  = open(output+".path","w")
        
    logger.info("Print the result as a fasta file")
    
    c=1
    seqid = config['orgasm']['outputfilename'].split('/')[-1]
    path = config['path']['path']
    
    logger.info('Built path : %s' % str(path))
                
    fa = path2fasta(asm,cg,path,
                    identifier="%s_%d" % (seqid,c),
                    back=back,
                    minlink=config['orgasm']['minlink'],
                    logger=logger,
                    tags=config['fasta']['tags'])
    
    print(fa,file=fastaout)
    print(" ".join([str(x) for x in path]),file=pathout)

    print(cg.gml(),file=open(output +'.path.gml','w'))
              
