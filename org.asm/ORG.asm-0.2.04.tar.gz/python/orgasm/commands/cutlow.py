'''
Created on 28 sept. 2014

@author: coissac
'''
from orgasm import getOutput,getIndex, getSeeds
from orgasm.tango import restoreGraph, estimateFragmentLength, genesincontig,\
    scaffold, cutLowCoverage, estimateDeadBrancheLength, dumpGraph

__title__="Cut low coverage edge in an assembling graph"

default_config = { 'coverage'      : None,
                   'smallbranches' : None
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='output', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    
    parser.add_argument('--coverage',         dest='cutlow:coverage', 
                                              required=True,
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='All edges with a coverage below this value will be deleted')
    
    parser.add_argument('--smallbranches',    dest='cutlow:smallbranches', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='maximum length of the branches to cut during '
                             'the cleaning process [default: <estimated>]')

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
    xxx,x,newprobes = getSeeds(r,config)  
    
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
        
    logger.info("Cut low coverage")

    cutLowCoverage(asm,config['cutlow']['coverage'],terminal=False)
    
    if config['cutlow']['smallbranches'] is not None:
        smallbranches = config['cutlow']['smallbranches']
    else:
        smallbranches = estimateDeadBrancheLength(asm)
        logger.info("Dead branch length setup to : %d bp" % smallbranches)
    
    asm.cleanDeadBranches(maxlength=smallbranches)
    
    cg = asm.compactAssembling(verbose=False)
    genesincontig(cg,r,x)

    scaffold(asm,cg,minlink=5,back=int(back),addConnectedLink=False)
     
    with open(output+'.gml','w') as gmlfile:
        print(cg.gml(),file=gmlfile)

    dumpGraph(output+'.oax',asm)

              
