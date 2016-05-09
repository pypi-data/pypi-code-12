import pickle
import sys

from .indexer import Index

from .backtranslate.fasta import fasta
from . import samples
from orgasm.utils.dna import isDNA

import os
import os.path

def getOutput(config):
    '''
    @param config: a configuration object
    @return: the path for the output files
    '''
    logger = config['orgasm']['logger']
    
    dirname = "%s.oas" % config['orgasm']['outputfilename']
    if not os.path.exists(dirname):
        if os.path.exists('%s.oax' % config['orgasm']['outputfilename']):
            
            if config['buildgraph']['reformat']:
                #
                # Reformating outpout according to the new format
                #

                # Try to load the index to test its format
                index=getIndex(config)
                
                os.makedirs(dirname) 
                for extension in ['oax','omx','gml','stats',
                                  'intermediate.gml','.intermediate.oax',
                                  'path.gml',
                                  'path']:
                    if os.path.exists('%s.%s' % (config['orgasm']['outputfilename'],
                                                 extension)):
                        os.renames('%s.%s' % (config['orgasm']['outputfilename'],
                                              extension), 
                                   '%s.oas/assembling.%s' % (config['orgasm']['outputfilename'],
                                                             extension))

                # Try to load the seeds to test its format
                seeds=getSeeds(index, config)
               
                sys.exit(0)
               
            else:
                #
                # Exit with an error because the format is obsolete.
                #
                logger.error("The %s assembly is not stored according to new format" % config['orgasm']['outputfilename'])
                logger.error('Run the oa buildgraph command with the --reformat option')
                sys.exit(1)
        else:
            os.makedirs(dirname)
            
            
        
    return "%s/assembling" % dirname
    

def getIndex(config):
    '''
    
    @param config: a configuration object
    @return: an Indexer instance
    '''
    
    logger=config['orgasm']['logger']    
    output=config['orgasm']['indexfilename']
    dirname="%s.odx" % output
    
    if (   (not os.path.exists(dirname))       and
           (os.path.exists('%s.ofx' % output ) and
            os.path.exists('%s.ogx' % output ) and
            os.path.exists('%s.opx' % output ) and
            os.path.exists('%s.orx' % output )
       )):
        logger.error('Index %s uses the old format please run the command' % output)
        logger.error('    oa index --reformat %s' % output)
        sys.exit(1)
    
    return Index("%s/index" % dirname)

def getProbes(config):
    '''
    According to the configuration file and the --seeds option this function return the set
    of sequence probes to use
    
     
    @param config: a configuration object
    @return: a dictionary with gene name as key and the 
             nucleic or protein sequence as value
    @rtype: dict
    '''
    logger=config['orgasm']['logger']
    seeds =config['orgasm']['seeds']
    
    probes = {}
    
    if seeds is not None:
    
        for s in seeds:
            try:
                p = fasta(s)
                logger.info("Load probe sequences from file : %s" % s)
            except IOError:
                p = getattr(samples,s)
                logger.info("Load probe internal dataset : %s" % s)
                
            probes[s]=[p,{}]
            
    else:
        logger.info("No new probe set specified")
                            
    return probes

def getAdapters(config):
    '''
    According to the configuration file and the --seeds option this function return the set
    of sequence probes to use
    
     
    @param config: a configuration object
    @return: a dictionary with gene name as key and the 
             nucleic or protein sequence as value
    @rtype: dict
    '''
    logger=config['orgasm']['logger']
    adapt5 =config['orgasm']['adapt5']
    adapt3 =config['orgasm']['adapt3']
    
    try:
        p3 = fasta(adapt3).values()
        logger.info("Load 3' adapter sequences from file : %s" % adapt3)
    except IOError:
        p3 = getattr(samples,adapt3)
        logger.info("Load 3' adapter internal dataset : %s" % adapt3)
                    
    try:
        p5 = fasta(adapt5).values()
        logger.info("Load 5' adapter sequences from file : %s" % adapt5)
    except IOError:
        p5 = getattr(samples,adapt5)
        logger.info("Load 5' adapter internal dataset : %s" % adapt5)
                    
    return (p3,p5)


def getSeeds(index,config):
    # looks if the internal blast was already run            
    output = config['orgasm']['outputfilename'] 
    logger=config['orgasm']['logger']
    kup=-1 if config['orgasm']['kup'] is None else config['orgasm']['kup']
    clean=config['buildgraph']['clean']
    forceseeds=config['buildgraph']['forceseeds']
    

    filename="%s.oas/assembling.omx" % output
    
    #
    # Check if the seeds are not correctly placed in the oas directory
    #

    oldfilename=output+'.omx'
    
    if (not os.path.exists(filename) and 
        os.path.exists(oldfilename)):
        if config['seeds']['reformat']:
            os.renames(oldfilename, filename)
        else:
            logger.error('Seed matches are not stored following the new format')
            logger.error('Run the oa seeds command with the --reformat option')
            sys.exit(1)
    
    
    #
    # Look for seeds with the new probe sets
    #

    newprobes = getProbes(config)
    
    # 
    # Load already run probe sets
    #
    reformated=[]
    if not clean or not newprobes:
        try:
            with open(filename,'rb') as fseeds:
                probes = pickle.load(fseeds)
            logger.info("Load matches from previous run : %d probe sets restored" % len(probes))
    
            if not isinstance(list(probes.values())[0][0], dict):
                logger.error("Too old version of probes matches that cannot be reformated")
                logger.error("Generate a new probe match set using the command oa seeds --seeds command")
                logger.error("The old unsuable seed match has been erased")
                os.remove(filename)
                sys.exit(1)
                
            oldversion=False
            for probename in probes:
                s = probes[probename][1]
                if len(s[list(s.keys())[0]][0]) != 6:
                    if config['seeds']['reformat']:
                        oldversion=True
        
                        logger.warning("Old probe version save on the disk. Recomputes probes %s" % probename)
                        
                        p = probes[probename][0]
                        logger.info("    -> probe set: %s" % probename)
             
                        seeds = index.lookForSeeds(p,
                                                   mincov=config['orgasm']['seedmincov'],
                                                   kup=kup,
                                                   identity=config['orgasm']['identity'],
                                                   logger=logger)
                        
                        probes[probename][1]=seeds
                        
                        reformated.append(probename)
                    
                        logger.info("==> %d matches" % sum(len(seeds[i]) for i in seeds))
                    else:
                        logger.error('Seed matches are not stored following the new format')
                        logger.error('Run the oa seeds command with the --reformat option')
                        sys.exit(1)
            
            if oldversion:
                with open(filename,"wb") as fseeds:
                    pickle.dump(probes,fseeds)
    
            nm=0
            for k in probes:
                for m in probes[k][1].values():
                    nm+=len(m)
            logger.info("   ==> A total of : %d" % nm)
        except FileNotFoundError: 
            logger.info("No previous matches loaded")
            probes={}
    else:
        if os.path.exists(filename):
            logger.info("Cleaning previous matches")
            os.remove(filename)
        probes={}

    
    if newprobes:
        # --seeds option on the command line -> look for these seeds
        logger.info("Running probes matching against reads...")
        
        for probename in newprobes:
            p = newprobes[probename][0]
            logger.info("    -> probe set: %s" % probename)
 
            seeds = index.lookForSeeds(p,
                                        mincov=config['orgasm']['seedmincov'],
                                        kup=kup,
                                        identity=config['orgasm']['identity'],
                                        logger=logger)
            
            nmatches = sum(len(seeds[i]) for i in seeds)
                        
            logger.info("==> %d matches" % nmatches)
            
            if nmatches:            
                probes[probename]=[p,seeds]
    
    newprobes = list(newprobes.keys()) 
     
    if not probes:
        logger.info("No --seeds option specified and not previous matches stored")
        sys.exit(1)
        
        
    if newprobes:
        with open(filename,"wb") as fseeds:
            pickle.dump(probes,fseeds)

    logger.info("Match list :") 

    covmax=0

    for probename in probes:
        p = probes[probename][0]
        s = probes[probename][1]
        nuc = all([isDNA(k) for k in p.values()])
        #print(s[list(s.keys())[0]])
        nbmatch = [(k,
                    sum(x[2] for x in s[k]),
                    sum(x[2] for x in s[k])*index.getReadSize() / len(p[k]) / (1 if nuc else 3)) for k in s]
                 
        nbmatch.sort(key=lambda x:-x[2])
        
        for gene, nb, cov in nbmatch:
            logger.info("     %-10s : %5d (%5.1fx)" % (gene,nb,cov))
        coverage=nbmatch[0][2]
        if coverage > covmax:
            covmax=coverage
        
    if forceseeds:
        newprobes=None

    return covmax,probes,newprobes

#def reloadAssembling