#!/usr/local/bin/python
"""
:py:mod:`obiselect` : selects representative sequence records
=============================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiselect` command allows to select a subset of sequences records from a sequence
file by describing sequence record groups and defining how many and which sequence records
from each group must be retrieved.

"""
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.ecopcr.options import addTaxonomyDBOptions, loadTaxonomyDatabase
from random import random
from obitools.utils import progressBar
import math
import sys
from obitools.utils.bioseq import mergeTaxonomyClassification

def minimum(seqs):
    return min(s['select'] for s in seqs)

def maximum(seqs):
    try:
        return max(s['select'] for s in seqs)
    except TypeError, e:
        print >>sys.stderr, seqs
        raise e
def mean(seqs):
    ss= reduce(lambda x,y: x + y,(s['select'] for s in seqs),0)
    return float(ss) / len(seqs)

def median(seqs):
    ss = [s['select'] for s in seqs]
    ss.sort()
    return ss[len(ss)/2]

    

def addSelectOptions(optionManager):
    
    group = optionManager.add_option_group('obiselect specific options')

    
    group.add_option('-c','--category-attribute',
                             action="append", dest="categories",
                             metavar="<Attribute Name>",
                             default=[],
                             help="Add one attribute to the list of"
                                  " attribute used for categorizing sequence records")

    group.add_option('-n','--number',
                             action="store", dest="number",
                             metavar="",
                             type="int",
                             default=1,
                             help="number of sequence records to keep in each category")

    group.add_option('-f','--function',
                             action="store", dest="function",
                             metavar="",
                             default="random",
                             help="python code evaluated for each sequence record [default: random value]")

   
    group.add_option('-m','--min',
                             action="store_const", dest="method",
                             metavar="",
                             default=maximum,
                             const=minimum,
                             help="select sequence record in each group minimizing the function"
                                  " (exclusive with -M, -a, --median)")
    
    group.add_option('-M','--max',
                             action="store_const", dest="method",
                             metavar="",
                             default=maximum,
                             const=maximum,
                             help="select sequence record in each group maximizing the function"
                                  " (exclusive with -m, -a, --median)")

    group.add_option('-a','--mean',
                             action="store_const", dest="method",
                             metavar="",
                             default=maximum,
                             const=mean,
                             help="select sequence record in each group closest to the mean of the function"
                                  " (exclusive with -m, -M, --median)")

    group.add_option('--median',
                             action="store_const", dest="method",
                             metavar="<Attribute Name>",
                             default=maximum,
                             const=median,
                             help="select sequence record in each group closest to the median of the function"
                                  " (exclusive with -m, -M, -a)")

    group.add_option('--merge',
                             action="append", dest="merge",
                             metavar="<TAG NAME>",
                             type="string",
                             default=[],
                             help="attributes to merge within each group")

    group.add_option('-s','--sample',
                             action="store", dest="sample",
                             metavar="<TAGNAME>",
                             type="str",
                             default=None,
                             help="Tag containing sample descriptions, the default value is set to *merged_sample*")

    group.add_option('--merge-ids',
                             action="store_true", dest="mergeids",
                             default=False,
                             help="add the merged id data to output")
    


def sortclass(seqs,options):
    cible = float(options.method(seqs))
    for s in seqs:
        s['distance']=math.sqrt((float(s['select'])-cible)**2)
    seqs.sort(lambda s1,s2 : cmp(s1['distance'],s2['distance']))
                                                


if __name__ == '__main__':
    
    optionParser = getOptionManager([addSelectOptions,addInOutputOption,addTaxonomyDBOptions])
    
    (options, entries) = optionParser()
    
    taxonomy=loadTaxonomyDatabase(options)

    writer = sequenceWriterGenerator(options)
    
    classes = {}
    
    print >>sys.stderr,"\nLoading sequences...\n"
    
    with_taxonomy=hasattr(options, 'taxonomy') and options.taxonomy is not None

    nbseq=0
    
    for s in entries:
        nbseq+=1
        category = []

        if with_taxonomy:
            environ = {'taxonomy' : options.taxonomy,'sequence':s,'random':random()}
        else:
            environ = {'sequence':s,'random':random()}

        for c in options.categories:
            try:
                v = eval(c,environ,s)
                category.append(v)
            except:
                category.append(None)

        category=tuple(category)
        group = classes.get(category,[])
        group.append(s)
        classes[category]= group
            
        try:    
            select =  eval(options.function,environ,s)
            s['select']=select
        except:
            s['select']=None
 
    mergedKey = options.merge
    mergeIds = options.mergeids 
          
    if mergedKey is not None:
        mergedKey=set(mergedKey)
    else:
        mergedKey=set() 
    
    if taxonomy is not None:
        mergedKey.add('taxid')
                
    
    print >>sys.stderr,"\nSelecting sequences...\n"
    
    lclasses=len(classes)
    progressBar(1,lclasses,True,'Selecting')
    i=0
    for c in classes:
        i+=1
        progressBar(i,lclasses,False,"%15s" % ("/".join(map(str,c)),))
        seqs = classes[c]
        if options.sample is not None:
            subsets = {}
            for s in seqs:
                for sid in s[options.sample]:
                    ss = subsets.get(sid,[])
                    ss.append(s)
                    subsets[sid]=ss
        else:
            subsets={"all":seqs}
            
        for seqs in subsets.values():
            sortclass(seqs, options)
            
            if len(c)==1:
                c=c[0]
                
            if options.number==1 and options.sample is None:
                s = seqs[0]
                
                for key in mergedKey:
                    if key=='taxid' and mergeIds:
                        if 'taxid_dist' not in s:
                            s["taxid_dist"]={}
                        if 'taxid' in s:
                            s["taxid_dist"][s.id]=s['taxid']
                    mkey = "merged_%s" % key 
                    if mkey not in s:
                        if key in s:
                            s[mkey]={s[key]:1}
                        else:
                            s[mkey]={}
    
                if 'count' not in s:
                    s['count']=1
                if mergeIds:        
                    s['merged']=[s.id]
    
                for seq in seqs[1:]:
                    
                    if 'count' in seq:
                        s['count']+=seq['count']
                    else:
                        s['count']+=1
                        
                    for key in mergedKey:
                        if key=='taxid' and mergeIds:
                            if 'taxid_dist' in seq:
                                s["taxid_dist"].update(seq["taxid_dist"])
                            if 'taxid' in seq:
                                s["taxid_dist"][seq.id]=seq['taxid']
                                
                        mkey = "merged_%s" % key 
                        if mkey in seq:
                            m = seq[mkey]
                        else:
                            if key in seq:
                                m={seq[key]:1}
                                
                        allmkey = set(m.keys()) | set(s[mkey].keys())
                        s[mkey] = dict((k,m.get(k,0)+s[mkey].get(k,0)) for k in allmkey)
                                                    
                    if mergeIds:        
                        s['merged'].append(seq.id)
     
                if taxonomy is not None:
                    mergeTaxonomyClassification(seqs, taxonomy)
                        
            
            for s in seqs[0:options.number]:
                s['class']=c
                s['__@TOWRITE@__']=True
     
    print >>sys.stderr,"\Writing sequences...\n"
    progressBar(1,nbseq,True,'Writing')
           
    i=0
    for c in classes:
        seqs = classes[c]
        for s in seqs:
            i+=1
            progressBar(i,nbseq,False,"Writing")
            if '__@TOWRITE@__' in s:
                del s['__@TOWRITE@__']
                del s['select']
                writer(s)
        
    print >>sys.stderr
