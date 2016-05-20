from sumrnaseq.readconfig import readconfig
from sumrnaseq.runrnaseqbash import runrnaseqbash
from sumrnaseq.makesummary import makesummary

import os.path
import os
import sys
from time import time, ctime
import datetime


def main(configfile):
    config_settings=readconfig.ConfigFile(configfile).readConfig()[0]
    config_groups=readconfig.ConfigFile(configfile).readConfig()[1]
#     print config_settings,config_groups
    if not os.path.exists(config_settings['summarydir']):
            os.mkdir(config_settings['summarydir'])
    fh=open(os.path.join(config_settings['summarydir'],'main.login'),'wa')
    fh.write("----------- %s Starting rnaseq program -----------" %ctime(time())+'\n' )
    timeStart = datetime.datetime.now()
    rnaseq_bash=runrnaseqbash.Bashrnaseq(config_settings)
    rnaseq_bash.writeBash()
    rnaseq_bash.runBash()
    timeEnd = datetime.datetime.now()
    fh.write("----------- %s - Finished rnaseq program -----------" %ctime(time())+'\n' )
    timeDiff = (timeEnd - timeStart)
    fh.write( "----------- rnaseq program duration %f hours. -----------" %(((timeDiff.microseconds + (timeDiff.seconds + timeDiff.days * 24. * 3600.) * 10**6)/ 10**6)/3600 )+'\n')
 
    fh.write("----------- %s Starting summary program -----------" %ctime(time())+'\n' )
    timeStart = datetime.datetime.now()    
    t=makesummary.Summary(config_settings,config_groups)
    t.summaryQC()
    t.summaryDataCleaning()
    t.summaryAlignment()
    t.summaryCoverage()
    t.createAssembly()
    timeEnd = datetime.datetime.now()
    fh.write("----------- %s - Finished summary program -----------" %ctime(time())+'\n' )
    timeDiff = (timeEnd - timeStart)
    fh.write( "----------- summary program duration %f hours. -----------" %(((timeDiff.microseconds + (timeDiff.seconds + timeDiff.days * 24. * 3600.) * 10**6)/ 10**6)/3600 )+'\n')
    fh.close()
 
if __name__=='__main__':
    if len(sys.argv)>1:
        main(sys.argv[1])
    else:
        print 'python %s <CONFIGFILE.INI>'%sys.argv[0]
        sys.exit()
    