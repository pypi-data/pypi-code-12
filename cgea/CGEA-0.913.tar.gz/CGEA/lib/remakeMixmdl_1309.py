from lib.featureBasedCGEA import CGEAdata
from lib.statistics import makeMixmdl

if __name__ == '__main__':  
    print 'Loading Data'
    data = CGEAdata()
    cmap = data.get('cmap')
    unifiedCompoundLevelSets = data.get("unifiedCompoundLevelSets")
    mixmdls = data.getModel('mixmdl')
    setSizes = reduce(lambda x,y: set.union(x,set(map(len,y.values()))), 
                      unifiedCompoundLevelSets.values(), 
                      set())
    print 'Generating mixmdls'
    makeMixmdl(cmap.keys(), data.getPath('mixmdl'), setSizes = setSizes, numIterations = 100000)
