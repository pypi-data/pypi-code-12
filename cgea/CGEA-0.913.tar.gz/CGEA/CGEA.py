from lib.file import write_JSON, read_file, dictionaryListToCSV
from lib.errorHandling import printException
import time, re, os, threading, getopt
from copy import deepcopy
from operator import itemgetter
from multiprocessing import cpu_count, Value as mpVal
from ctypes import c_double

from CGEA import __file__ as package_path
package_path = os.path.dirname(package_path)

def get_CGEA_data():
    import  urllib, zipfile
    from distutils.sysconfig import get_python_lib
    input = raw_input("Performing first time setup - is it ok to download CGEA data (135.4 MB)? y/n\n")
    while not (input == 'y' or input == 'n'):
        input = raw_input("Invalid input. Permission to download CGEA data (135.4 MB)? y/n\n")
    if input == 'y':
        urllib.urlretrieve("https://bitbucket.org/MaxTomlinson/cgea/downloads/data.zip", 
                           package_path+"/data.zip")
        zipfile.ZipFile(package_path+"/data.zip").extractall(package_path+"/")
        os.remove(package_path+"/data.zip")
        print "Loaded All CGEA Data"
        return True
    else:
        raise RuntimeError('CGEA data not available.')
    
if not os.path.isfile(package_path+'/data/cmap_1309_entrez.json'):
    data_loaded = get_CGEA_data()
    
from lib.featureBasedCGEA import featureBasedCGEA
from lib.fishersBasedCGEA import fishersBasedCGEA
    
class geneListCGEA():
    def __init__(self, upgenes, downgenes, *args, **kwargs):
        self.myCGEA = initCGEA(upgenes = upgenes, downgenes = downgenes, *args, **kwargs)
        #self.status = self.myCGEA.status
        self.results = self.myCGEA.results
        #self.filepaths = self.myCGEA.filepaths
        
    def run(self):
        self.myCGEA.run()

class drugListCGEA():
    def __init__(self, druglist, *args, **kwargs):
        self.myCGEA = initCGEA(druglist = druglist, *args, **kwargs)
        #self.status = self.myCGEA.status
        self.results = self.myCGEA.results
        #self.filepaths = self.myCGEA.filepaths
        
    def run(self):
        self.myCGEA.run()
    
def initCGEA(async = False, *args, **kwargs):
    if async:
        myCGEA = CGEA_async(*args, **kwargs)
    else:
        myCGEA = CGEA(*args, **kwargs)
    return myCGEA
    
class CGEA_async(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = True
        self.myCGEA = CGEA(*args, **kwargs)
        self.status = self.myCGEA.status
        self.results = self.myCGEA.results
        self.filepaths = self.myCGEA.filepaths
        
    def run(self):
        self.myCGEA.run()


class CGEA():
    def __init__(self, upgenes = None, downgenes = None, druglist = None, saveAs = "json", sort = 'up', outputDir = None, 
                 prefix = 'CGEAResults', data = {}, numWorkers = cpu_count(), verbose = False, numPermutations = 1000):
        self.upgenes = upgenes
        self.downgenes = downgenes
        self.druglist = druglist
        self.status = ['PENDING','Initialized', 0.0]
        self.saveAs = saveAs
        self.outputDir = outputDir
        self.sort = sort
        self.prefix = str(prefix)
        self.data = data
        self.filepaths = []
        self.results = {}
        self.numWorkers = numWorkers
        self.verbose = verbose
        self.numPermutations = numPermutations
        self.saveFunction = {'json': lambda: self.writeSingleSheet('.json', write_JSON),
                             #'json': lambda: self.writeMultipleSheets('.json', write_JSON),
                             #'csv':lambda: self.writeSingleSheet('.csv', lambda x,y: write_csv(x,y, delimiter = ',')),
                             #'tsv':lambda: self.writeSingleSheet('.tsv', lambda x,y: write_csv(x,y, delimiter = '\t')),
                             'csv':lambda: self.writeMultipleSheets('.csv', lambda x,y: dictionaryListToCSV(x,y, delimiter = ',', encode = 'utf8')),
                             'tsv':lambda: self.writeMultipleSheets('.tsv', lambda x,y: dictionaryListToCSV(x,y, delimiter = '\t', encode = 'utf8'))
                             }
    
    def writeResults(self):
        self.saveFunction[self.saveAs]()
    
    def writeSingleSheet(self, suffix, writeFxn):
        filepath = self.outputDir+self.prefix+suffix
        writeFxn(filepath, self.results)
        self.filepaths.append(filepath)
    
    def writeMultipleSheets(self, suffix, writeFxn):
        for name, result in self.results.items():
            if len(self.prefix) > 0: filepath = self.outputDir+re.sub('\s+', '_', '_'.join([self.prefix,name])+suffix)
            else: filepath = self.outputDir+re.sub('\s+', '_', name+suffix)
            self.filepaths.append(filepath)
            writeFxn(filepath, result)
#         
#     def writeEnrichmentsToJSONs(self):
#         filepaths = []
#         for name, result in self.results.items():
#             if len(self.prefix) > 0: filepath = self.outputDir+re.sub('\s+', '_', '_'.join([self.prefix,name])+'.json')
#             else: filepath = self.outputDir+re.sub('\s+', '_', name+'.json')
#             self.filepaths.append(filepath)
#             write_JSON(self.outputDir+re.sub('\s+', '_', ' '.join(self.prefix,name)+'.json'), result)
# 
#     def writeEnrichmentsToJSON(self):
#         filepath = self.outputDir+self.prefix+'.json'
#         write_JSON(filepath, self.results)
#         self.filepaths.append(filepath)
    
    def run(self):
        self.status[0] = 'RUNNING'
        if self.verbose:
            print 'Started CGEA'
        try:
            if self.upgenes == None and self.downgenes == None and self.druglist == None:
                raise RuntimeError("No input given to CGEA.")
            elif not (self.upgenes == None and self.downgenes == None):
                self.results.update(featureBasedCGEA(self.upgenes, self.downgenes, self.saveAs, self.outputDir, self.sort, 
                                                     self.data, self.status, numWorkers = self.numWorkers, verbose = self.verbose,
                                                     numPermutations = self.numPermutations))
            else:
                self.results.update(fishersBasedCGEA(self.druglist, self.outputDir, self.sort, self.data, 
                                                     self.status, numWorkers = self.numWorkers, verbose = self.verbose))
            if self.saveAs and os.path.isdir(self.outputDir):
                curTime = time.time()
                self.writeResults()
                if self.verbose:
                    print 'Wrote Results'
            self.status[0] = 'SUCCESS'
            self.status[1] = 'Finished'
            self.status[2] = 1.0
            if self.verbose:
                print 'Finished CGEA'
        except Exception as e:
            printException()
            print e
            self.status[0] = 'ERROR'
            self.status[1] = e
            self.status[2] = 1.0

def testGeneListCGEA(outputDir = package_path+"/data/sampledata/sampleout/", **kwargs):
    upgenes = package_path+"/data/sampledata/up_genes.txt"
    downgenes = package_path+"/data/sampledata/down_genes.txt"
    curTime = time.time()
    myCGEA = geneListCGEA(upgenes = upgenes, downgenes = downgenes, prefix = 'sampleGeneListOutput', outputDir = outputDir, verbose = True, **kwargs)
    myCGEA.run()
    print 'Total time: ' + str(time.time()-curTime)
    return myCGEA

def testDrugListCGEA(outputDir = package_path+"/data/sampledata/sampleout/", **kwargs):
    druglist = package_path+"/data/sampledata/drug_list.txt"
    curTime = time.time()
    myCGEA = drugListCGEA(druglist = druglist, prefix = 'sampleDrugListOutput', outputDir = outputDir, verbose = True, **kwargs)
    myCGEA.run()
    print 'Total time: ' + str(time.time()-curTime)
    return myCGEA