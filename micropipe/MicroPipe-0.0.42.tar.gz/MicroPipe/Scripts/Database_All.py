#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/10/29
"""

from lpp import *
PATH= sys.argv[1]

for e_path in glob.glob(PATH+'/Prediction/*/'):
    os.system("/home/lpp/Project//MicroBiologyPipeline/Scripts/create_database.py -n %(paths)s/*.ffn -p %(paths)s/*.faa -g %(paths)s/*.gff -d database.db"%(
            {
                "paths":e_path
    
            }
        
    
    )
            )
    
for e_path in glob.glob(PATH+'/Annotation/*/'):
    os.system(
        
        "/home/lpp/Project//MicroBiologyPipeline/Scripts/COG_Database.py -d database.db -n %(paths)s/*.cog"%(
            {
                "paths":e_path+'/COG/'
    
            }
        
    
        )
    )
    os.system(
    
        "/home/lpp/Project//MicroBiologyPipeline/Scripts/KEGG_Database.py -d database.db -a %(paths)s/*.top1 -p  %(paths)s/*_detail.tsv"%(
            {
                "paths":e_path+'/Pathway/'
    
            }
    
    
        )
    )    
    
    os.system(
    
        "/home/lpp/Project//MicroBiologyPipeline/Scripts/Swiss_Database.py -d database.db -a %(paths)s/*.top1 "%(
            {
                "paths":e_path+'/GO/'
    
            }
    
    
        )
    )    
    
    os.system(
        
            "/home/lpp/Project/MicroBiologyPipeline/Scripts/GO_Database.py -o database.db -i %(paths)s/*.annotaion_detail "%(
                {
                    "paths":e_path+'/GO/'
        
                }
        
        
            )
        )   
    os.system(

    "/home/lpp/Project/MicroBiologyPipeline/Scripts/Nr_Database.py -d database.db -n %(paths)s/*.top1 "%(
        {
            "paths":e_path+'/nr/'

        }


    )
)
    
os.system("/home/lpp/Project//MicroBiologyPipeline/Scripts/Total_Out.py -d database.db -n 49 -o annotation.xls")