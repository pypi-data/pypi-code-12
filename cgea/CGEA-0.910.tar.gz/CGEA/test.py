from CGEA import drugListCGEA, testGeneListCGEA, testDrugListCGEA

if __name__ == '__main__' :
    testGeneListCGEA(numWorkers = 1, async = False, saveAs = 'csv', sort = 'abs')
    testDrugListCGEA(numWorkers = 1, async = False, saveAs = 'tsv')