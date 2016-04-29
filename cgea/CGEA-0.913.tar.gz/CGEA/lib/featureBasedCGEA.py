from file import read_JSON, read_file, write_csv, prettyPrint
import random, math, time, os, json
import multiprocessing as mp
from copy import deepcopy
import numpy as np, os
from sklearn import mixture, preprocessing
from sklearn.externals import joblib
from statsmodels.sandbox.stats.multicomp import multipletests
from operator import itemgetter
from statistics import generateBackgroundModel, generateScore, generatePVals, compoundSetGSEA, scoreRankedLists, makeMixmdl
from CGEAdata import CGEAdata
from featureListProcessing import formatGeneLists

def featureBasedCGEA(upgenes, downgenes, saveAs, outputDir, sortDir, data, status, alpha = .05, numWorkers = mp.cpu_count(), pool = None, verbose = True, numPermutations = 1000):
    #print 'Start - 0'
    status[1] = 'Started'
    status[2] = 0.01
    curTime = time.time()
    data = CGEAdata(data = data)
    status[1] = 'Loading cmap data'
    if verbose:
        print status[1]
    cmap = data.get('cmap')
    #print "Loaded cmap data - took " + str(time.time()-curTime) + ' seconds'
    status[1] = 'Loaded cmap data'
    if verbose:
        print status[1]
    status[2] = 0.03
    
    geneLists = formatGeneLists([upgenes, downgenes])
    
    status[1] = 'Generating Null Model'
    if verbose:
        print status[1]
    curTime = time.time()
    [backgroundModel, backgroundScores, scaler] = generateBackgroundModel(geneLists, cmap, status=status, numWorkers = numWorkers, numPermutations = numPermutations)
    
    #print "Generated Null Model - took " + str(time.time()-curTime) + ' seconds'
    status[1] = 'Generated Null Model'
    if verbose:
        print status[1]
    status[2] = 0.33
    curTime = time.time()
    
    status[1] = 'Scoring Compounds'
    if verbose:
        print status[1]
#     drugIndex = {}
#     scores = []
#     index = {}
#     countCMAP = len(cmap.keys())
#     for count, value in enumerate(cmap.items()):
#         if status:
#             status[2] += 1.0/(countCMAP)*3.3/10.0
#         name = value[0]
#         cmapList = value[1]
#         #if (count+1)%100 == 0: print str(count+1)+" cmap drugs scored"
#         score = generateScore(geneLists, cmapList)[0]
#         index[count] = name
#         drugIndex[name] = count
#         scores.append([score])
    
    [drugIndex, scores, index] = scoreRankedLists(geneLists, cmap, status=status, numWorkers = numWorkers, pool = pool)
    
    #TESTING
    #drugList = []
    #for drug in drugIndex.keys():
    #    index = drugIndex[drug]
    #    drugList.append([drug,scores[index][0]])
    #print sorted(drugList, key = itemgetter(1), reverse = False)[0:10]
    #TESTING
    
    #print sorted([[x, scores[drugIndex[x]]] for x in drugIndex.keys()], key = itemgetter(1))[0:10]
    #print "Generated Annotated Compound Scores - took " + str(time.time()-curTime) + ' seconds'
    curTime = time.time()
    [pvals, adjpvals, scores] = generatePVals(backgroundModel, scores, backgroundScores = backgroundScores, scaler = scaler, alpha = alpha, numWorkers = numWorkers, pool = pool)
    #print "Generated Annotated Compound Pvals - took " + str(time.time()-curTime) + ' seconds'
    
    
    #TESTING
    #drugList = []
    #for drug in drugIndex.keys():
    #    index = drugIndex[drug]
    #    drugList.append([drug,scores[index]])
    #print sorted(drugList, key = itemgetter(1), reverse = False)[0:10]
    #raise hell
    #TESTING
    
    
    status[1] = 'Compounds Scored and Annotated'
    if verbose:
        print status[1]
    status[2] = 0.66
    curTime = time.time()
    drugAnnotations = {}
    for drug in drugIndex.keys():
        index = drugIndex[drug]
        drugAnnotations[drug]={'Name':drug,
                               'Score':scores[index],
                               'P-Value':pvals[index],
                               'Adjusted P-Value':adjpvals[index]
                               }
    #print '\n'.join(map(lambda x: ' '.join([x['Name'], str(x['Adjusted P-Value']), str(x['Score'])]),sorted(drugAnnotations.values(), key = itemgetter('Score'))[0:10]))
    status[1] = 'Performing Gene Enrichment'
    if verbose:
        print status[1]
    [rankedAnnotatedDrugs, compoundSetResults] = geneEnrichment(drugAnnotations, data, status = status, numWorkers = numWorkers, pool = pool)
    results = {'Annotated Compounds':rankedAnnotatedDrugs, 'Combined Enrichment Results':compoundSetResults}
    #print "Performed Gene Enrichment - took " + str(time.time()-curTime) + ' seconds'
    status[1] = 'Performed Gene Enrichment'
    if verbose:
        print status[1]
    status[2] = 0.99
    curTime = time.time()
    return results
    
      
typos={'X6.bromoindirubin.3..oxime':'6-bromoindirubin-3-oxime',
       'alpha.estradiol':'alpha-estradiol'}
# sorting = {'up':lambda x: sorted(list(x.values()), key = itemgetter('Score')),
#            'down': lambda x: sorted(list(x.values()), key = itemgetter('Score')),
#            'abs': lambda x: sorted(list(x.values()), key = lambda x: abs(x['Score']))
#            }
mySort = {'up':lambda x: x.sort(key = itemgetter('Score')),
          'down': lambda x: sort(key = itemgetter('Score'), reverse = True),
          'abs': lambda x: x.sort(key = lambda y: abs(y['Score']))
          }
def geneEnrichment(drugAnnotations, data, sortDir = 'up', status = None, numWorkers = mp.cpu_count(), pool = None):
    
    #######################
    # Annotated Compounds #
    #######################
    curTime = time.time()
    cmapDrugMetaData = data.get("cmapDrugMetaData")
    for drugData in cmapDrugMetaData:
        if drugData['name'] in drugAnnotations: 
            #print 'Rname'
            drugAnnotations[drugData['name']].update(drugData)
            del drugAnnotations[drugData['name']]['name']
        elif drugData['Rname'] in drugAnnotations: 
            #print 'name'
            drugAnnotations[drugData['Rname']].update(drugData)
            del drugAnnotations[drugData['Rname']]['name']
        elif drugData['name'] in typos:
            drugAnnotations[typos[drugData['name']]].update(drugData)
            del drugAnnotations[typos[drugData['name']]]['name']
        elif drugData['Rname'] in typos:
            drugAnnotations[typos[drugData['Rname']]].update(drugData)
            del drugAnnotations[typos[drugData['Rname']]]['name']
        else:
            print 'Missing from annotations: '+ drugData['name'] + '/' + drugData['Rname']
    del cmapDrugMetaData
    #print time.time() - curTime
    #curTime = time.time()
    
    rankedAnnotatedDrugs = drugAnnotations.values()
    mySort[sortDir](rankedAnnotatedDrugs)
    
    sizeThreshold = 5
    targetEnrSeedPAdj = .1
    minCompoundSetSizeThreshold = 5
    
    #######################
    # Combined Enrichment #
    #######################
    unifiedCompoundLevelSets = data.get("unifiedCompoundLevelSets")
    mixmdls = data.getModel('mixmdl')
    
    if not mixmdls:
        #If this has been reached, you are trying to run this without loading the data from bitbucket.
        print 'Gene Enrichment Mixture Models are not loaded. Computing Compound Set Mixmdls.'
        setSizes = reduce(lambda x,y: set.union(x,set(map(len,y.values()))), unifiedCompoundLevelSets.values(), set())
        #print maxSetSize
        makeMixmdl(data.get('cmap').keys(), data.getPath('mixmdl'), setSizes = setSizes, numIterations = 1000)
        mixmdls = data.getModel('mixmdl')
    #print time.time() - curTime
    #curTime = time.time()
    status[2]+=.03
    enrichmentData = data.getEnrichmentData()
    rankedDrugs = map(itemgetter('Name'),rankedAnnotatedDrugs)
    compoundSetResults = {}
    numSets = len(unifiedCompoundLevelSets.keys()+enrichmentData.keys())
    for setType, compoundSets in unifiedCompoundLevelSets.items()+enrichmentData.items():
        compoundSets = filter(lambda x: len(x[1])>minCompoundSetSizeThreshold, compoundSets.items())
        if len(compoundSets) > 0:
            compoundSetResults[setType] = compoundSetGSEA(rankedDrugs, mixmdls, compoundSets, numWorkers = numWorkers, pool = pool)
            #print 'Generated Results for ' + setType
        status[2] += 1.0/numSets*3.0/10.0
    
    #print time.time() - curTime
    #Generate Summary
    summaryResults = reduce(lambda x,y: x+map(lambda z: dict(zip(['Compound Set'] + z.keys(), [y[0]]+z.values()))
                                                        ,y[1])
                                      ,compoundSetResults.items(), [])
    mySort[sortDir](summaryResults)
    return [rankedAnnotatedDrugs, summaryResults]
