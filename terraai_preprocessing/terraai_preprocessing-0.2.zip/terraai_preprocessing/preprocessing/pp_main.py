# -*- coding: utf-8 -*-
"""
Created on Fri May 06 13:41:37 2016
Pre-processing package
@author: Aamir
"""

from datetime import datetime
from time import strftime
import time
from multiprocessing import Pool

from pp_helpers import * 


"""Global parameters"""

schema = "public_data"
DB_ProdTable_name = "bigprod_ts"  #"big_prod_sum2" #"bigprod_ts"
DB_MasterTable_name = "big_master"

#NowDatestr = str(strftime("%Y-%m-%d"))
#initDate = datetime.strptime('1900-01-01','%Y-%m-%d')

__conn,__cursor = establish_DBconn(schema)

#Check if Timeseries table
__Timeseries_flag = False
if "_ts" in DB_ProdTable_name:
    __Timeseries_flag = True


def __preprocessor(well):
   
    #well = arg
    print "Reading well id -", well
    
    if __Timeseries_flag:
        data = get_WellData_unstr(__cursor,well,schema,DB_ProdTable_name,DB_MasterTable_name)
    else:
        data = get_WellData(__cursor,well,schema,DB_ProdTable_name,DB_MasterTable_name)
        
    
    data = get_static_data(data,__cursor,well,schema,DB_MasterTable_name)
    data = process_data(__cursor,data)
    #data = split_data(data,Tr_s,Tr_e,Te_s,Te_e)
    if data == 0:
        data = {"API":well}
    return data


def start_preprocess(StateAPI=33,return_format="L_of_D",wellIDs=[]):#Tr_s='1900-01-01',Tr_e='2008-12-31',Te_s='2009-01-31',Te_e='2015-12-31'):
    
    start_time=time.time()
    if len(wellIDs)==0:
        wellIDs = get_WellPids(__cursor,StateAPI,schema,DB_ProdTable_name,DB_MasterTable_name)
    
    #create_table(__conn,__cursor,"aamir","pp_test")

    not_worthy_API,worthy_API,results = [],[],[]
    
    args = tuple(API for API in wellIDs)
    
    """ Sequential """
#    for i,arg in enumerate(args):
#        data = preprocessor(arg)
#        results.append(data)  
        
    pool  = Pool()
    tasks = pool.map_async(__preprocessor, args)
    tasks.wait()
    results = tasks.get()
    
    for i,data in enumerate(results):
        if len(data) == 1:
            print "Well not worthy of analysis -",data["API"]
            not_worthy_API.append(data["API"])
            results.remove(data)
        else:
            worthy_API.append(data["API"])
    pool.close()
    pool.join()


    if return_format == "D_of_L":
        results = LDtoDL(results)
        
    #__write_data_csv(data)
    #__write_csv(map(str,worthy_API),map(str,not_worthy_API))
    #__write_DB(__conn,__cursor,"aamir","pp_test",results)
    
    print "-"*59
    print "Total number of wells -", len(wellIDs)
    print "Not worthy of analysis -", len(not_worthy_API)
    print "Total Time taken- "+ str(round((time.time()-start_time),2))+" secs" 
    #return worthy_API,not_worthy_API
    return results  
    

#if __name__=='__main__':
    #start_preprocess()
