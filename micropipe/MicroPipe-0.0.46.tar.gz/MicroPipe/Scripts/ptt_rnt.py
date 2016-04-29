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
import pandas as pd

usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-i", "--Database", action="store",
                  dest="CSV",

                  help="Table File")


parser.add_option("-o", "--O", action="store",
                  dest="output_path",
                  help="output_path")

if __name__ == '__main__':

    (options, args) = parser.parse_args()
    data_frame = pd.read_table(options.CSV)
    data_frame["Location" ]= data_frame["Ref_Start"].astype("string")+'..' +data_frame["Ref_Stop"].astype("string")
    data_frame["COG" ] = data_frame["COG"]+data_frame["COG_FunCat"]
    data_frame["Product"] = data_frame["Function"]
    data_frame["Strand"] = data_frame["Ref_Frame"]
    data_frame["PID"] = data_frame["Name"]

    data_frame["Code"] = '-'
    data_frame["Gene"] = data_frame["Name"]
    data_frame["Length"] = data_frame["Seq_Nucl_Length"]
    data_frame["Synonym"] = data_frame["Name"]
    data_frame = data_frame[   pd.notnull(data_frame["Kind"])  ]    
    
    
    all_source = set(data_frame["Ref_Source"])
    for e_source in all_source:
        need_data = data_frame[ data_frame["Ref_Source"]==e_source   ]
        need_data_cds = need_data[ need_data["Kind"]=="CDS"   ]
        need_data_rna = need_data[ need_data["Kind"].str.contains("RNA")   ]
        need_data =  pd.DataFrame(need_data, columns=["Kind",'Location',"Strand","Length","PID","Gene","Synonym","Code","COG","Product"])
        need_data_cds = pd.DataFrame(need_data_cds, columns=['Location',"Strand","Length","PID","Gene","Synonym","Code","COG","Product"])
        need_data_rna = pd.DataFrame(need_data_rna, columns=['Location',"Strand","Length","PID","Gene","Synonym","Code","COG","Product"])
        
        need_data_cds["COG"] = need_data_cds["COG"].replace( "--","-" )

        need_data_rna["COG"] = need_data_rna["COG"].replace( "--","-" )
        PTT= options.output_path+'/'+e_source+'/%s.ptt'%(e_source)
        DATA = open(PTT,'w')
        DATA.write("%s\n"%(e_source))
        DATA.write("%s Proteins\n"%( len(need_data_cds)  ))
        DATA.close()
        RNT= options.output_path+'/'+e_source+'/%s.rnt'%(e_source)
        DATA = open(RNT,'w')
        DATA.write("%s\n"%(e_source))
        DATA.write("%s RNAs\n"%( len(need_data_rna)  ))
        DATA.close()        
        
        
        need_data_cds.to_csv(PTT,sep="\t",index=False,mode='a')
        need_data_rna.to_csv(RNT,sep="\t",index=False,mode='a')
        
