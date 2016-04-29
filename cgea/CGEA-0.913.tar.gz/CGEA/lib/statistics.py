#Generates scores, pvals, background models
import random, math, time
from copy import deepcopy
import numpy as np
from sklearn import mixture, preprocessing
from sklearn.externals import joblib
from statsmodels.sandbox.stats.multicomp import multipletests
from scipy.stats import hypergeom
from operator import itemgetter
from SimpleMapReduce import SimpleMapReduce
from errorHandling import printException
import itertools
import multiprocessing as mp   

def multiMap(mapFunc, inputs, numWorkers, chunksize, pool = None):
    if numWorkers > 1 and not pool:
        pool = mp.Pool(numWorkers)
    #print inputs
    #print mapFunc(inputs[0])
    #print chunksize
    if numWorkers > 1:
        results = pool.map(mapFunc, inputs, chunksize=chunksize)
    else:
#         results = []
#         for input in inputs:
#             results.append(mapFunc(input))
        results = map(mapFunc, inputs)
#     if results[0] == None: 
#         print inputs
#         print mapFunc(inputs[0])
#         print mapFunc(inputs[1])
#         print chunksize
#         print numWorkers
    if pool:
        pool.close()
        pool.join()
    return results

#geneLists, cmap
def scoreRankedLists(featureLists, rankedLists, status = None, numWorkers = mp.cpu_count(), pool = None):
    nameIndex = {}
    index = {}
    #startTime = time.time()
    scoreData = multiMap(scoreRankedList(featureLists, rankedLists, status),
                         rankedLists.keys(),
                         numWorkers,
                         chunksize=int(math.ceil(float(len(rankedLists.keys()))/numWorkers)),
                         pool = pool)
    for count, data in enumerate(scoreData):
        name = data[0]
        index[count] = name
        nameIndex[name] = count
    #print scoreData
    scores = map(lambda x: [x[1]], scoreData)
    #print scores
    return [nameIndex, scores, index]

class scoreRankedList():
    def __init__(self, featureLists, rankedLists, status):
        self.featureLists = featureLists
        self.rankedLists = rankedLists
        self.status = status
        self.countLists = len(rankedLists.keys())
    
    def __call__(self, name):
        if self.status:
            self.status[2] += 1.0/(self.countLists)*3.3/10.0
        cmapList = self.rankedLists[name]
        return [name, generateScore(self.featureLists, cmapList)[0]]

class genPval():
    def __init__(self, weights):
        self.weights = weights
    def __call__(self, x):
        return sum(map(lambda y: pow(10,math.log(x[1][y]/self.weights[y],10)+x[0]),range(0,len(self.weights))))

def generatePVals(backgroundModel, scores, setSizes = None, backgroundScores = None, scaler = None, alpha = .05, FDR = None, numWorkers = mp.cpu_count(), pool = None):
    if not isinstance(backgroundModel, dict):
        if not FDR: FDR = calcFDR(backgroundModel, backgroundScores, alpha = alpha)
        if scaler: scores = scaler.transform(scores)
        #print scores
        pvals = map(genPval(backgroundModel.weights_), zip(*backgroundModel.score_samples(scores)))
        scores = map(itemgetter(0), scores)
    else:
        pvals = []
        FDRs = []
        for index, score in enumerate(scores):
            setSize = setSizes[index]
            if not setSize in backgroundModel:
                setSize = max(backgroundModel.keys())
            model = backgroundModel[setSize]['model']
            FDRs.append(backgroundModel[setSize]['FDR'])
            scaler = backgroundModel[setSize]['scaler']
            pvals.append(map(genPval(model.weights_), 
                             zip(*model.score_samples(scaler.transform(np.array([score]).reshape(1, -1))))
                             )[0] #only one value
                         )
        FDR = np.mean(FDRs)
    adjpvals = multipletests(pvals, method='fdr_bh', alpha = FDR)[1]
    return [list(pvals), list(adjpvals), list(scores)]

def calcFDR(backgroundModel, backgroundScores, alpha = .05):
    backgroundPvals = map(genPval(backgroundModel.weights_), zip(*backgroundModel.score_samples(backgroundScores)))
    FDR = sorted(backgroundPvals)[int(math.floor(len(backgroundPvals)*alpha))]
    return FDR
    

#query takes the featureLists and queries it against randomized rankedLists.
#randomSubset takes a random subset of the featureList of size 'sizeOfSubset', and queries it against a randomized rankedList
backgroundModelScoringMethods = {'query':lambda x,y,z,w,s,nw,p: generateBackgroundScores(x,y,z,status=s,numWorkers = nw, pool = p),
                                 'randomSubset':lambda x,y,z,w,s,nw,p:
                                                        reduce(lambda a,b: a+b, #joins list of background scores
                                                            map(lambda placeholder: 
                                                                    generateBackgroundScores(random.sample(x,w),
                                                                                             sorted(y, key=lambda k: random.random()),
                                                                                             int(math.ceil(math.sqrt(z))),
                                                                                             numWorkers = nw,
                                                                                             pool = p),
                                                                range(0, int(math.ceil(math.sqrt(z)))) 
                                                            )#gens list of background scores based on subset of rankedList
                                                        )
                          }
n_components = {'query': 3,
                'randomSubset': 2
                }
def generateBackgroundModel(featureLists, rankedList, numPermutations = 1000, sizeOfSubset = None, method = 'query', status = None, numWorkers = mp.cpu_count(), pool = None):
    scores = backgroundModelScoringMethods[method](featureLists, rankedList, numPermutations, sizeOfSubset, status, numWorkers, pool)
    scaler = preprocessing.StandardScaler().fit(scores)
    scores = scaler.transform(scores)
    model = mixture.GMM(n_components=n_components[method], covariance_type = 'diag', min_covar = .001, tol= 1e-05, n_iter = 10000, n_init = 200) #tol is convergence threshold
    model.fit(scores)
    return [model,list(scores), scaler]

def generateBackgroundScores(featureLists, rankedList, numPermutations, status = None, numWorkers = mp.cpu_count(), pool = None):
    
    generateBackgroundScoreFunction = generateBackgroundScore(featureLists, rankedList, numPermutations, status)
    #mapper = SimpleMapReduce(generateBackgroundScoreFunction, lambda x: list(itertools.chain.from_iterable(x)), num_workers = numWorkers)
    #startTime = time.time()
    scores = multiMap(generateBackgroundScoreFunction,
                      range(numPermutations), 
                      numWorkers,
                      chunksize=int(math.ceil(float(numPermutations)/numWorkers)),
                      pool = pool)
    #scores = mapper(range(numPermutations),chunksize=int(math.ceil(numPermutations/numWorkers)))
    return scores

class generateBackgroundScore():
    def __init__(self, featureLists, rankedList, numPermutations, status):
        self.featureLists = featureLists
        self.rankedList = rankedList
        self.numPermutations = numPermutations
        self.status = status
    
    def __call__(self, runNumber):
        if self.status:
            self.status[2] += 1.0/(self.numPermutations)*3.0/10.0
        
        
        if isinstance(self.rankedList,dict):
            unrankedList = sorted(self.rankedList[random.choice(self.rankedList.keys())], key=lambda k: random.random())
        elif isinstance(self.rankedList, list):
            unrankedList = sorted(self.rankedList, key=lambda k: random.random())
        else:
            #print self.rankedList
            unrankedList = sorted(self.rankedList, key=lambda k: random.random())
        #if (i+1)%100 == 0:print str(i+1) + ' permutations.'
        #print str(unrankedList[0:10])
        return [generateScore(self.featureLists, unrankedList)[0]]
        
    

#For a list of genes, generates a score for each drug in cmap. 19 lines.
def generateScore(featureLists, rankedList):
    if not isinstance(featureLists[0], list): featureLists = [featureLists]
    unrankedSet = set(rankedList)
    lenRankedList = len(rankedList)
    #for each up/down in featureList
    peakValues = []
    peakValueIndices = []
    hitPositions = []
    for featureList in featureLists:
        featureSet = set(featureList)
        #Remove values in the featureList not in rankedList
        featureSet = set.intersection(featureSet, unrankedSet)
        numHits = len(featureSet)
        if numHits > 0:
            numMisses = lenRankedList - numHits
            #print "numGenes is: "+ str(len(featureList)) +", numRankedGenes is: "+ str(len(cmapSet))+" numHits is: " + str(numHits) + ", numMisses is: " + str(numMisses)
            #hits is a cumulative probability distribution for the likelihood that a gene will appear in the list.
            #ie, if rankedList was [1,2,3,4,5,6,7,8,9], and featureList was [2,5,8,9], 
            #hits would be [0,.25,.25,.25,.5,.5,.5,.75,1]
            #misses would be [.2,.2,.4,.6,.6,.8,1,1,1]
            #difference would be [.2,.05,.15,.35,.1,.3,.5,.25,0]
            hits = map(lambda x: int(x in featureSet), rankedList)
            hitPositions.append(deepcopy(hits))
            hits = np.cumsum(hits)
            hits = map(lambda x: float(x)/numHits, hits)
            
            misses = np.cumsum(map(lambda x: int(not x in featureSet), rankedList))
            misses = map(lambda x: float(x)/numMisses, misses)
            
            difference = map(lambda x: abs(hits[x] - misses[x]), range(lenRankedList))
            
            #find the value that represent the greatest difference between ranked list and gene set.
            peakValue = max(difference)
            peakIndex = difference.index(peakValue)
            peakValueIndices.append(peakIndex)
            peakValues.append(hits[peakIndex]-misses[peakIndex])
    if len(peakValues) == 1:
        score = peakValues[0]
        peakValueIndices = peakValueIndices[0]
        hitPositions = hitPositions[0]
    elif len(featureLists) ==2:
        score = (peakValues[0] - peakValues[1])/2 #assume featureList[1] is down signature
    else:
        raise ValueError
    return [score, peakValueIndices, hitPositions]

def compoundSetGSEA(rankedDrugs, mixmdls, compoundSets, alpha = .05, numWorkers = mp.cpu_count(), pool = None):
    scores = []
    peakPositions = []
    hitPositionLists = []
    setSizes = []
    #print compoundSets
    #print scoreCompoundSet(compoundSets, rankedDrugs)(0)
    scoreData = multiMap(scoreCompoundSet(compoundSets, rankedDrugs),
                         range(len(compoundSets)), 
                         min(numWorkers,len(compoundSets)),
                         chunksize=int(math.ceil(float(len(compoundSets))/numWorkers)),
                         pool = pool)
    [scores, peakPositions, hitPositionLists, setSizes] = zip(*scoreData)
    [pvals, adjpvals, scores] = generatePVals(mixmdls, scores, setSizes = setSizes, alpha = alpha)
    output = []
    for index, [compoundName, _] in enumerate(compoundSets):
        output.append({'Name': compoundName,
                       'P-Value': pvals[index], 
                       'Adjusted P-Value':adjpvals[index], 
                       'Score':scores[index], 
                       'Peak Position':peakPositions[index], 
                       'Hit Positions':hitPositionLists[index]})
    return output
#looking for DC_PATHWAY_UP and [u'flunisolide', u'beta-escin', u'medrysone', u'DL-thiorphan', u'sitosterol', u'phenoxybenzamine']
class scoreCompoundSet():
    def __init__(self, compoundSets, rankedDrugs):
        self.compoundSets = compoundSets
        self.rankedDrugs = rankedDrugs
        
    def __call__(self, index):
        [compoundName, compoundSet] = self.compoundSets[index]
        [score, peakPosition, hitPositions] = generateScore(compoundSet, self.rankedDrugs)
        hitPositions = map(itemgetter(0), filter(lambda x: x[1], enumerate(hitPositions)))
        hitPositions = ';'.join(map(lambda x: self.rankedDrugs[x] + ':' + str(x), hitPositions))
        setSize = len(compoundSet)
        return [score, peakPosition, hitPositions, setSize]

def compoundSetHypergeometricEnrichment(querySet, compoundSets, universeSize, numWorkers, pool = None):
    compoundSetPvals = multiMap(setHypergeometricEnrichmentClass(querySet, universeSize),
                         compoundSets, 
                         min(numWorkers,len(compoundSets)),
                         chunksize=int(math.ceil(float(len(compoundSets))/numWorkers)),
                         pool = pool)
    compoundSetAdjPvals = multipletests(compoundSetPvals, method='fdr_bh', alpha = .05)[1]
    return zip(*[compoundSetPvals, compoundSetAdjPvals])

class setHypergeometricEnrichmentClass():
    def __init__(self, querySet, universeSize):
        self.querySet, self.universeSize = querySet, universeSize
        
    def __call__(self, popB):
        return setHypergeometricEnrichmentScore(self.querySet, popB, self.universeSize)

def setHypergeometricEnrichmentScore(popA, popB, popSize):
    if not (isinstance(popA, set) and isinstance(popB, set)):
        print 'inputs should be sets in compoundSetHypergeometricEnrichment'
        return False
    
    popASize = len(popA)
    popBSize = len(popB)
    popAB = set.intersection(popA, popB)
    popABSize = len(popAB)
    #sanity check
    if not (len(set.union(popA,popB)) + popABSize == popASize + popBSize ):
        print 'popA: '+str(popA)
        print 'popB: '+str(popB)
        print 'popAB: '+str(popAB)
        print 'something is rotten in the state of setHypergeometricEnrichment function.'
        
    return hypergeom.sf(*[popABSize-1, popSize, popASize, popBSize])#P(X >= popABSize)

def makeMixmdl(featureList, filepath, maxSetSize = 50, numIterations = 100, alpha = .05, setSizes = None):
    models = {}
    if not setSizes:
        setSizes = set(range(1,maxSetSize+1))
    for i in setSizes:
        print 'Iteration#'+str(i)
        [model, scores, scaler] = generateBackgroundModel(featureList, featureList, numPermutations = numIterations, sizeOfSubset = i, method = 'randomSubset')
        models[i] = {'model':model,
                     'scaler':scaler,
                     'FDR': calcFDR(model, scores, alpha = alpha)}
        print np.histogram(scores)
        print "Background weights:" +str(model.weights_)
        print "Background means:" +str(map(itemgetter(0),model.means_))
        print "Background covars:" +str(map(itemgetter(0),model.covars_))
    joblib.dump(models, filepath) 