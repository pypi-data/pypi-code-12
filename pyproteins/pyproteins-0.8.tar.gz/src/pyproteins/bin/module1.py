import sys, getopt
import json
import os
import pyproteins.services.utils as u
import pyproteins.homology.template as hT
import pyproteins.homology.query as hQ
import pyproteins.homology.threaders as thr
import re

'''
Read configuration file

HHSUITE --- executable check
template directory

'''
bGridEngine = False
bWriteMsa = False
bLoadTemplate = True
bTemplateView = False
bTemplateMsaRebuild = False
bHhThread = False
nModel = 0

beanConfig = {}
templateLib = {}
env = os.environ.copy()

templateShortList = []

def hhThread(queryObj, workDir):
    global templateLib
    global bGridEngine
    global nModel
    workDir=workDir + '/models'
    u.mkdir(workDir)

    thr.hhAlign(query=queryObj, template=[ templateLib[t]['obj'] for t in templateLib ], bSge=bGridEngine, workDir=workDir, nModel=nModel)

# Create working directory foreach template
# w/ subdirectories for query, hhalign, modeller
#

def loadQuery(queryInputFile, workDir):
    global bGridEngine

    if queryInputFile.endswith('fasta'):
        queryObj = hQ.Query(fastaFile=queryInputFile)
        queryObj.make(bSge=bGridEngine, workDir=workDir, blastDbRoot=beanConfig['BLASTDBROOT'], blastDb=beanConfig['blastDb'], psipredDbRoot=beanConfig['psipredDbRoot'] ,psipredScript=beanConfig['executable']['runpsipred'])
        queryObj.beanDump(filePath=workDir + '/queryBean.json')
    if queryInputFile.endswith('json'):
        queryObj=hQ.loadFromBean(queryInputFile)




    #print queryObj.mAli
    print '\t\t==>QUERY LOADED<=='
    print str(queryObj)
    #print queryObj.hhDump()
    return queryObj

# iterate over structure, get makecore folder
# Could be lazy instantied
# PDB file names must respect regexp /^pdb*ent$/
def loadTemplateLibrary():
    global bLoadTemplate
    global beanConfig
    global templateLib
    global templateShortList

    if not bLoadTemplate:
        print "Not loading any template ressources"
        return

    if "pdbDir" not in beanConfig:
        raise ValueError, 'not pdbDir in ' + str(beanConfig)

    for id in beanConfig["registeredTemplate"]:
        for pdbDir in beanConfig["pdbDir"]:
            for fPdb in u.find(name='^pdb*' + id + '*ent$', path=pdbDir):
                m = re.search("pdb([^\.]+)\.ent$", fPdb)
                if m:
                    tag = m.group(1)
                if templateShortList:
                    if tag not in templateShortList:
                        continue

                for pddDir in beanConfig["pddDir"]:
                    metaDataFolder = u.find(name='*' + tag + '*', path=pddDir, sType='dir')
                    if len(metaDataFolder) != 1:
                    #print metaDataFolder
                        continue
                    else:
                        templateObj = hT.Template(fPdb, id=id,folder=metaDataFolder[0])
                        templateLib[tag] = { 'pdb' : fPdb, 'data' : metaDataFolder[0], 'obj' : templateObj}
                        break


def reBuildTemplateLibrary(bMsa=False,workDir=os.getcwd()):
    global templateLib
    if bMsa:
        tList = [ templateLib[k]['obj'] for k in templateLib ]
        hT.makeAll(tList, bMsa=True, bSge=bGridEngine, workDir=workDir, blastDbRoot=beanConfig['BLASTDBROOT'], blastDb=beanConfig['blastDb'])

def readConfig(fPath):
    global beanConfig
    print "Reading configuration from " + fPath
    with open(fPath) as json_file:
        beanConfig = json.load(json_file)

    if "envVariables" in beanConfig:
        for nVar in beanConfig["envVariables"]:
            env[nVar] = beanConfig["envVariables"][nVar]

    if "appendPath" in beanConfig:
        env['PATH'] = ':'.join(beanConfig["appendPath"]) + ':' + env['PATH']

    #print beanConfig
    if "templateLib" not in beanConfig:
        loadTemplateLibrary()

    if bTemplateView:
        print str(templateLib)


# exitCode = subprocess.call(task, env=env, shell=True)


def main(argv):
    beanConfigPath = None
    global templateShortList
    global bWriteMsa
    global bTemplateView
    global bLoadTemplate
    global bGridEngine
    global bTemplateMsaRebuild
    global bHhThread
    global nModel
    workDir=os.getcwd()
    queryInputFile = None
    print os.getcwd()

    try:
        opts, args = getopt.getopt(argv,"hi:c:g:s:o:q:",["nModel=","noTemplate","sge","templateList","templateSelect=", "workDir=","templateMsaRebuild", "hhThread"])

    except getopt.GetoptError as e:
        print e
        print 'module -i <sequenceFile> -o <tag for outputfiles>'
        sys.exit(22)
    for opt, arg in opts:
        if opt == '-h':
            print 'runMsa.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt == "-o":
            outputTag = arg
        elif opt ==  "-c":
            beanConfigPath = arg
        elif opt == "--templateSelect":
            #bWriteMsa = True
            templateShortList =  arg.split(',')
        elif opt == "--sge":
            bGridEngine = True
        elif opt == "--workDir":
            workDir = arg if os.path.isabs(arg) else os.getcwd() + "/" + arg
            u.mkdir(workDir)
        elif opt == "--noTemplate":
            bLoadTemplate = False
        elif opt == "--templateMsaRebuild":
            bTemplateMsaRebuild = True
        elif opt == "--hhThread":
            bHhThread = True
        elif opt == "--templateList":
            bTemplateView = True
        elif opt == "--nModel":
            nModel = int(arg)
        elif opt == "-q":
            queryInputFile = arg
        else:
            print "Unkwnown argument " + opt
            sys.exit()

    if beanConfigPath:
        readConfig(beanConfigPath)

    #if bWriteMsa:
    #    for iTag in templateShortList:
    #        if iTag not in templateLib:
    #            raise ValueError, iTag + ' is not a registred template'
    #        templateLib[iTag]['obj'].msa().fastaDump(iTag + '.mfasta')


    if queryInputFile:
        queryObj = loadQuery(queryInputFile, workDir)

    if bTemplateMsaRebuild:
        reBuildTemplateLibrary(bMsa=True, workDir=workDir)

    if bHhThread:
        hhThread(queryObj, workDir)

#if bAlign:

if __name__ == "__main__":
    main(sys.argv[1:])


