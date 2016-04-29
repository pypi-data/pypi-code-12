import re, os
from file import read_csv
from copy import deepcopy
base_path = os.path.abspath(os.path.dirname(__file__))

def parseSymbol2Entrez(filepath):
    data = read_csv(filepath)
    localdict = {}
    for row in data[1:]:
        row = row[0].split(" ")
        if row[1].startswith('"') and row[1].endswith('"'):
            row[1] = row[1][1:-1]
        localdict[row[1]] = row[0]
    return localdict

entrezLookup = parseSymbol2Entrez(base_path + '/../data/symbol2entrez.txt')
#formats file by modifying file
def formatFeatureFile(filepath):
    locallist = []
    f = open(filepath, 'r')
    for row in f:
        row = re.findall(r"[\w']+", row)
        for item in row:
            if item in entrezLookup:
                locallist.append(entrezLookup[item])
            elif item in entrezLookup.values():
                locallist.append(item)
            else:
                print item
    f.close()
    return locallist

#formats list by modifying it in place
def formatFeatureList(featureList):
    localList = []
    for row in featureList:
        if isinstance(row, basestring):
            row = re.findall(r"[\w']+", row)
            for item in row:
                if item in entrezLookup:
                    localList.append(entrezLookup[item])
                elif item in entrezLookup.values():
                    localList.append(item)
                else:
                    print item
        elif isinstance(row, int):
            if row in entrezLookup.values():
                localList.append(row)
            else:
                print row
    return localList

def formatFeatureString(featureString):
    featureList = []
    for item in re.findall(r"[\w']+", featureString):
        if item in entrezLookup:
            featureList.append(entrezLookup[item])
        elif item in entrezLookup.values():
            featureList.append(item)
        else:
            print item
    return featureList

#takes genelists as an array, modifies array
def formatGeneLists(geneLists):
    for index, genelist in enumerate(geneLists):
        if genelist:
            if isinstance(genelist, basestring):
                if os.path.isfile(genelist):
                    geneLists[index] = formatFeatureFile(genelist)
                else:
                    geneLists[index] = formatFeatureString(genelist)
            elif isinstance(geneList, list):
                geneLists[index] = formatFeatureList(genelist)
            else:
                print genelist
    geneLists = filter(lambda x: x, map(lambda x: map(int, x) if x else None, geneLists))
    return geneLists