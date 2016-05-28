#!/usr/local/bin/python
'''
:py:mod:`obisubset`: extract a subset of samples 
================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

The :py:mod:`obisubset` command extracts a subset of samples from a sequence file
after its dereplication using :py:mod:`obiuniq` program.
'''
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
import re

def addSubsetOptions(optionManager):
    
    group = optionManager.add_option_group('obisubset specific options')
    group.add_option('-s','--sample',
                             action="store", dest="sample",
                             metavar="<TAGNAME>",
                             type="str",
                             default='merged_sample',
                             help="Tag containing sample descriptions, the default value is set to *merged_sample*")
     
    group.add_option('-o','--other-tag',
                     action="append", dest="taglist",
                     metavar="<TAGNAME>",
                     type="string",
                     default=[],
                     help="Another tag to clean according to the sample subset")

    group.add_option('-l','--sample-list',
                     action="store", dest="samplelist",
                     metavar="<FILENAME>",
                     type="string",
                     default=None,
                     help="File containing the samples names (one sample id per line)")
    
    group.add_option('-p','--sample-pattern',
                     action="store", dest="samplepattern",
                     metavar="<REGEX>",
                     type="string",
                     default=None,
                     help="A regular expression pattern matching the sample ids to extract")
    
    group.add_option('-n','--sample-name',
                     action="append", dest="samplename",
                     metavar="<SAMPLEIDS>",
                     type="string",
                     default=[],
                     help="A sample id to extract")
    
def sequenceSelectorGenerator(options):

    samplename = set(options.samplename)
    othertags  = set(options.taglist)
    
    if options.samplelist is not None:
        with open(options.samplelist) as lname :
            for name in lname:
                name = name.strip()
                samplename.add(name)
        
    if options.samplepattern is not None:
        samplepattern = re.compile(options.samplepattern)
    else:
        samplepattern = None
    
    def sequenceSelector(entries):
        for entry in entries:
            samples=entry[options.sample]

            slist = set(samples.keys())
            tokeep=slist & samplename
            
            if samplepattern is not None:
                for name in slist:
                    if samplepattern.match(name):
                        tokeep.add(name)
                        
            if tokeep:
                newsample={}
                newcount=0
                for name in tokeep:
                    c = samples[name]
                    newsample[name]= c 
                    newcount+=c 
                    
                entry['count']=newcount 
                entry[options.sample]=newsample
                
                for t in othertags:
                    if t in entry:
                        d = entry[t]
                        newd={}
                        for name in tokeep:
                            if name in d:
                                newd[name] = d[name]
                        entry[t]=newd
                
                yield entry
                
    return sequenceSelector
                    
if __name__=='__main__':
    
    optionParser = getOptionManager([addInOutputOption,addSubsetOptions],progdoc=__doc__)
    
    (options, entries) = optionParser()
    
    writer = sequenceWriterGenerator(options)
    
    good = sequenceSelectorGenerator(options)
    
    for seq in good(entries):
        writer(seq)
