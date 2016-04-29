#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/3/16
"""

#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/3/16
"""
import os,sys,redis
from os.path import abspath
sys.path.append( os.path.split(abspath(__file__))[0]+'/../Lib/' )
from lpp import *
from Dependcy import *

usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-d", "--Database", action="store",
                  dest="DB_FILE",

                  help="Database File")


parser.add_option("-n", "--n", action="store",
                  dest="db_num",
                  type='int',
                  help="database number")


parser.add_option("-o", "--OUTPUT", action="store",
                  dest="output",

                  help="TSV output")
if __name__ == '__main__':

    (options, args) = parser.parse_args()
    data_all = open( options.DB_FILE,'rU' ).read()
    data_all = re.sub("\r\n","\n",data_all)
    data_all = re.sub("\n","\r\n",data_all)
    CACHE = open("cache.redis",'w')
    CACHE.write(data_all)
    END = open(options.output,'w')
    out_title = ["Name","Kind","Function","Ref_Source","Ref_Start","Ref_Stop","Ref_Frame","Seq_Nucleotide","Seq_Nucl_Length","Seq_Protein","Seq_Protein_Length"]
    db_number = options.db_num
    
    r = redis.Redis(host='192.168.0.10',port=6379,db=int(db_number))
    r.flushall()
    os.system(" cat %s  | redis-cli  -n %s --pipe" %(  CACHE.name, db_number ))
    for key in sorted(r.hgetall("title")):
        if key not in out_title:
            out_title.append(key)
    END.write("\t".join(out_title)+'\n')
    cache_data = ""
    for key in sorted(r.keys()):
        
        if key =="title":
            continue
        cache_data +=key
    
        for key2 in out_title[1:]:
            if key2 in r.hgetall(key):
                cache_data +="\t"+r.hgetall(key)[key2]
    
            else:
                cache_data +="\t-"
    
        cache_data+="\n"
            
    END.write(cache_data)

    
	
