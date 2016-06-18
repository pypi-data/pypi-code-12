# -*- coding: utf-8 -*-
"""
Created on Fri May 06 13:41:36 2016

@author: Aamir
"""
import sys
sys.path.insert(0, '..\combinatorics')

import MySQLdb
from collections import defaultdict
import numpy as np
from datetime import datetime
import calendar
from calendar import monthrange
from time import strptime , strftime
from operator import sub
import csv
import json
from pkg_resources import resource_filename

import terraai_preprocessing.combinatorics.API_main_comb as combinator
#import terraai_preprocessing.preprocessing.config as x
#import API_main_comb as combinator

__NowDatestr = str(strftime("%Y-%m-%d"))
__initDate = datetime.strptime('1900-01-01' , '%Y-%m-%d')

Time_Trsh     = 2    # number of month the well should have been producing to be used for analysis
Diff_days     = 2    # tolerance on number of down days to be accepted as downevent



def establish_DBconn(schema="public_data"): 
    """
    Establish DB connection
    """
    s = str(resource_filename('terraai_preprocessing.preprocessing', 'config.json')).replace('\\','/')
    
    try:
        with open(s, 'r') as f:
            config = json.load(f)

    except:
        config = {"host": "navjot.c4lstuf6msdr.us-west-2.rds.amazonaws.com", 
          "password": password, 
          "user": user}
        
    #config = {"host": "navjot.c4lstuf6msdr.us-west-2.rds.amazonaws.com", "password": password, "user": user}
    cnx = { 'host': config["host"],'user':config["user"],'password': config["password"]}    
    conn = MySQLdb.connect(cnx['host'],cnx['user'],cnx['password'])
    
    cursor = conn.cursor() 
    return conn,cursor


def get_WellPids(cursor,StateAPI=33,schema="public_data",DB_ProdTable_name="big_prod_sum2",DB_MasterTable_name="big_master"):
    """
    Gets the well ids from the table data is being retrieved. 
    Also gets the well ids from the the table where results are being written to avoid duplicates.
    """
    try:
        cursor.execute("SELECT distinct(API_prod) FROM "+schema+"."+DB_ProdTable_name+" WHERE state="+str(StateAPI)+";")
    except:
        DB_ProdTable_name="big_prod_sum2"
        cursor.execute("SELECT distinct(API_prod) FROM "+schema+"."+DB_ProdTable_name+" WHERE state_API="+str(StateAPI)+";")
    row   = cursor.fetchall()
        
    unique_pids=set([int(v[0]) for v in row]) 
    unique_pids = filter(lambda x: x!=None, unique_pids) # remove None elements from list
    
    return sorted(list(unique_pids))
    

def get_WellData(cursor,API_prod,schema="public_data",DB_ProdTable_name="big_prod_sum2",DB_MasterTable_name="big_master",StartDate='1900-01-01',EndDate=__NowDatestr):
    
    """Getting the production data from DB"""
    
    Structure = "API_prod, state_API, report_date, pool_code, pool_name, well_status_prod, prod_days, oil, water, gas"
    
#    if type(API_prod) == list:
#        query = "SELECT "+Structure+" FROM "+schema+"."+DB_ProdTable_name+" WHERE API_prod in ( " + ",".join(map(str,API_prod)) + " ) \
#        and report_date>%s and report_date<=%s order by API_prod , report_date ASC limit 10;"
#        cursor.execute(query,[StartDate,EndDate])
#    else:
    query = "SELECT "+Structure+" FROM "+schema+"."+DB_ProdTable_name+" WHERE API_prod=%s\
    and report_date>%s and report_date<=%s order by API_prod , report_date ASC;"
    cursor.execute(query,[str(API_prod),StartDate,EndDate])
    
    row = cursor.fetchall()
    
    data = defaultdict(list)
    for (i, item) in enumerate(row):
        
        #currentDate = item[2].strftime("%Y-%m-%d")
        item = np.array(map(lambda x: np.nan if x==None else x, item))
        
        data['API'].append( int(float(item[0])) ) 
        
        data['state_API'].append( int(float(item[1])) )
        data['dates'].append( item[2].strftime("%Y-%m-%d") )
        data['pool_code'].append( item[3] )
        data['pool_name'].append( item[4] )
        data['wellstat'].append( item[5] )
        data['proddays'].append( item[6] )
        data['oil_mo'].append( float(item[7]) )
        data['water_mo'].append( float(item[8]) )
        data['gas_mo'].append( float(item[9]) )
            
    return data
    

def get_WellData_unstr(cursor,API_prod,schema,DB_ProdTable_name,DB_MasterTable_name,StartDate='1900-01-01', EndDate=__NowDatestr , oilprice_dict = None):
    """
    Get data from a table in time series format. Faster read
    """
    #==== get column names from table
    cursor.execute("describe %s.%s" % (schema , DB_ProdTable_name))
    allowed_keys = [row[0] for row in cursor.fetchall()]
    
    #==== Getting the production data from DB ====#
    Structure = ','.join(allowed_keys) # "*"
    
    query = "SELECT "+Structure+" FROM "+schema+"."+DB_ProdTable_name+" WHERE API_prod=%s;"
    cursor.execute(query,[str(API_prod)])    
    
    row   = list(cursor.fetchall())
    row[0] = list(row[0])
    data = defaultdict(list)
    
    data['dates'] = [x for x in row[0][2].split(',')]
    
    #====Handle cases when the column has a null value. Replace by a string of 0
    for i in range(3,7):
        if row[0][i]==None:
            row[0][i] = ['0']* len(data["dates"])
            row[0][i] = ','.join(row[0][i])
            
    data['oil_mo'] = [abs(float(x)) if x!=None else 0 for x in row[0][3].split(',')]
    data['water_mo'] = [abs(float(x)) if x!=None else 0 for x in row[0][4].split(',')]
    data['gas_mo'] = [abs(float(x)) if x!=None else 0 for x in row[0][5].split(',')]
    data['proddays'] = [int(x) if x!=None else 0 for x in row[0][6].split(',')]
    
    for i,v in enumerate(data["dates"]):
        v = datetime.strptime(v,'%Y-%m-%d')
        if datetime.strptime(StartDate,'%Y-%m-%d') > v or v > datetime.strptime(EndDate,'%Y-%m-%d'):
            for k in data.keys():
                data[k].pop(i)
    
    data['API'] = [row[0][0]]*len(data["dates"])
    data['state_API'] =  [row[0][1]]*len(data["dates"])
    data['pool_name'] = [row[0][7]]*len(data["dates"])

    return data


def get_static_data(data,cursor,API_prod,schema="public_data",DB_MasterTable_name="big_master"):
    
    """Getting the master (static) data from DB"""
    Structure = "API_master, state_API_master, well_status, well_type, lat, longi, pool_code_master, pool_name_master, spud_date"
    
    query = "SELECT "+Structure+" FROM "+schema+"."+DB_MasterTable_name+" WHERE API_master = %s;"
    cursor.execute(query,[str(API_prod)])
    row = cursor.fetchall()
    
    for (i, item) in enumerate(row):
        
        data['well_type'].append( item[3] )
        
        data['lat'].append( float(item[4]) if item[4]!=None else None )
        data['longi'].append( float(item[5]) if item[5]!=None else None )
        
        data['pool_code_master'].append( item[6] )
        data['pool_name_master'].append( item[7] )
        if bool(item[8]):
            data['spud_date'].append( item[8].strftime("%Y-%m-%d") )
        else:
            data['spud_date'].append( " " )
    
    return data
    

def process_data(cursor,data):
    
    if bool(data):  
        data = imputeMissingData(data) # impute new data if some months are missing and add the corresponding dates
    
    #Check if it is a valid producer for forecasting
    accptflag,lastProdIndx,firstProdIndx = Check_Valid_Producer(data,Time_Trsh,Diff_days)

    data,lastProdIndx,firstProfIndx = Trim_Dictionary(data,lastProdIndx,firstProdIndx) 
    
    accptflag,lastProdIndx,firstProdIndx = Check_Valid_Producer(data,Time_Trsh,Diff_days) #to check on trim data
    if accptflag == 0:
        return 0     
    data["accptflag"] = accptflag #data["status_flags"]["accept"]
    
    #Remove outliers in oil water gas data
    #data = moving_avg_outlier(data)
    
    #---------------------------------------
    # get extra data needed
    # get extra dimensions and data needed
    OilPrice_Dict       = get_oilprices(cursor , schema="public_data" , tablename="oil_price_monthly" , RefDates=data['dates']) # oil price monthly
    data.update(oilprice=np.array(OilPrice_Dict['oilprice_value']))
    
    if np.shape(data['dates'])[0] != 0 :
        
        tempDict  = combinator.encoder(data['API'],data['dates'],data['proddays'],data['oil_mo'],data['water_mo'],['wor','time'],['linear','linear'])
        data.update(wor=np.array(tempDict['arg1']))
        del tempDict
        
        tempDict = combinator.encoder(data['API'],data['dates'],data['proddays'],data['oil_mo'],data['water_mo'],['cumoil','time'],['linear','linear'])
        data.update(cumoil=np.array(tempDict['arg1']))
        del tempDict
        
        tempDict = combinator.encoder(data['API'],data['dates'],data['proddays'],data['oil_mo'],data['water_mo'],['cumwat','time'],['linear','linear'])
        data.update(cumwater=np.array(tempDict['arg1']))
        del tempDict
        
    #Calculate per day values and also set 0's  
    data = calc_pd(data)
    
    return data
    

def Trim_Dictionary(Dict, LastProdIndx, FirstProdIndx):
    for i,key in enumerate(Dict):
        if type(Dict[key])==int:
            continue
        length    = len(Dict[key])
        Dict[key] = Dict[key][np.nanmax(FirstProdIndx,0):np.nanmin([LastProdIndx,length])]
    
    FirstProdIndx = 0 # update the first index of production
    LastProdIndx  = len(Dict['oil_mo']) # updat ethe last index of production

    return Dict , LastProdIndx , FirstProdIndx
    

def moving_avg_outlier(data):
    """
    Calculate moving window average 
    """
    x = ["oil_mo","water_mo","gas_mo"]
    
    for m in x:
        o = list(data[m]) #create a new list
        
        for i in xrange(2,len(o)-2):
            
            if o[i]>10:
                o_temp = [o[i-2],o[i-1],o[i+1],o[i+2]]
                o_mean,o_std = np.mean(o_temp),np.std(o_temp) 
                if o[i] > (o_mean+(3*o_std)) or o[i] < (o_mean-(3*o_std)):
                    o[i] = o_mean
            
        data[m+"_mod"] = o
    
    return data
        
       
def calc_pd(data):
    """
    Calculate per day values
    """
    oil_pd,water_pd = [],[]
    
    for i in xrange(len(data["proddays"])):
        
        #check non-zero
        if data["proddays"][i] == 0:
            data["oil_mo"][i],data["water_mo"][i] = 0,0
        
        if data["oil_mo"][i] == 0:
            data["proddays"][i] == 0
        
        a,b = 0,0
        if data["proddays"][i] != 0:
            a = data["oil_mo"][i]/data["proddays"][i]
            b = data["water_mo"][i]/data["proddays"][i]
            
        oil_pd.append(a),water_pd.append(b)
    
    data["oil_pd"],data["water_pd"] = oil_pd,water_pd
    
    return data
    
    
def imputeMissingData(dataIn):
    ''' Accepts a list of dictionaries and analyzes them one by one '''

    #LD_dataOut = LD_dataIn
    #for lnum,dataIn in enumerate(LD_dataIn): 
    
    # determine the number of month between first and last dates given in data
    WellStartDate = dataIn['dates'][0] 
    monthnumsIndx = np.array([diff_month(WellStartDate,x) for x in dataIn['dates']])
    
    # generate the continuse month dates strings for the new data
    allindx       = range(max(monthnumsIndx)+1)
    datesstr,_    = add_months(WellStartDate,allindx)
    
    # imput zeros for missing data
    dataOut = dataIn.copy()
    impute_keys = ["dates","oil_mo","water_mo","gas_mo","proddays"]
    for (j , key) in enumerate(impute_keys):
        # Update the measured values series by imputing NaNs when data is missing
        dataOut[key] = np.empty(shape=len(datesstr),dtype=type(dataIn[key])) #np.array(dataIn[key],dtype=type(dataIn[key][0]),ndmin=len(datesstr))
        dataOut[key].fill(0.0) # can change into zero if want 0
        if np.size(dataIn[key])==1:
            dataOut[key] = np.nan_to_num ( [dataIn[key] for i in range(len(dataOut[key]))] )
        else:
            dataOut[key][monthnumsIndx] = np.nan_to_num (dataIn[key])
        
        #==== replace nans with zeros
        dataOut[key] = np.nan_to_num(dataOut[key]) 
        
        # get linear time index of months and the continuous dates strings
        dataOut['MonthIndx'] = np.asarray(range(max(monthnumsIndx)+1))  #range(monthnumsIndx[-1])
        dataOut['dates']     = np.asarray(datesstr)
        
    for key in dataOut.keys():
        
        m,n = len(dataOut[key]),len(dataOut["dates"])
        
        if m!=n:
            dataOut[key] = [dataOut[key][-1]]*n
#        else:
#            while  m != n:
#                    dataOut[key].append(dataOut[key][-1])
#                    m +=1
                
        #dataOut['API_prod']  = [np.asarray(dataOut['API_prod'][0]) for i in range(len(dataOut['API_prod']))]
        
    return dataOut


def diff_month(d1str,d2str):
    d1 = datetime.strptime(d1str , '%Y-%m-%d')
    d2 = datetime.strptime(d2str , '%Y-%m-%d')
    try:
        return (d2.year - d1.year)*12 + d2.month - d1.month
    except:
        import pdb; pdb.set_trace()
        print "Exception.  The aregument was {}.".format(d2)
        return np.NaN


def add_months(sourcedatestr,months):
    sourcedate = datetime.strptime(sourcedatestr , '%Y-%m-%d')    
    
    month = [ sourcedate.month - 1 + months[i] for i in xrange(len(months)) ]
    year  = [int(sourcedate.year + x / 12 ) for x in month]
    month = [ month[i] % 12 + 1 for i in xrange(len(month)) ]
    day   = [min(sourcedate.day , calendar.monthrange(year[i],month[i])[1]) for i in xrange(len(year)) ]
    
    
    day        = [calendar.monthrange(year[i],month[i])[1] for i in range(len(year))] # get the end of month day number date
    datestring = [(str(year[i])+"-"+str(month[i])+"-"+str(day[i])) for i in range(len(year))]   
    dates      = [datetime.strptime(datestring[i] , '%Y-%m-%d') for i in range(len(datestring))]    
    return datestring , dates


def get_oilprices(cursor , schema="public_data" , tablename="oil_price_monthly" , RefDates = None , InputOilPrice_Dict = None):
    
    if InputOilPrice_Dict is None:
        cursor.execute("SELECT * FROM "+schema+"."+tablename+";")
        row = cursor.fetchall()
        oil_prices     = [row[i][1] for i in xrange(len(row))]
        oilprice_dates = [datetime.strftime(row[i][0],'%Y-%m-%d') for i in xrange(len(row))]    # ?????
        
    else:
        oil_prices     = InputOilPrice_Dict['oilprice_value']
        oilprice_dates = InputOilPrice_Dict['oilprice_date']
    del InputOilPrice_Dict
    
    
    if RefDates is not None: # given set of dates for which oil priuce is needed
        RefDates_obj = RefDates
    else:
        RefDates_obj = oilprice_dates
        
    #==== get the inedex of requested dates compared to ref dates in database   
    istart = diff_month(oilprice_dates[0],RefDates_obj[0])
    Indx   = range(istart,istart+len(RefDates_obj))
                
    price_date=[]
    price_val = []
    for s in Indx:
        
        try:
            price_date.append(oilprice_dates[s])
            price_val.append(oil_prices[s])
        except:
            print "Price length error"
          
    oilprice_dict = defaultdict(list) 
    oilprice_dict['oilprice_value'] = price_val    
    oilprice_dict['oilprice_date']  = price_date

    return oilprice_dict
    
    
'''-------------------------------------------------
This function calculates the number of days well has been down in each month

---------------------------------------------------'''    

def DownTime(ProdEndDates,ProdDays):
     
    A=[]
    DaysInMonth=[]
    
    for i in xrange(len(ProdEndDates)):
        #array of Dates extract Month and Year from the string and find the number of days in that month
    
        x=strptime(ProdEndDates[i],"%Y-%m-%d")
        A.append(x)
        DaysInMonth.append(monthrange(x.tm_year,x.tm_mon)[1])          
    
    #DaysDown= (a-b for a,b zip(DaysInMonth,ProdDays))
    DaysDown=map(sub, DaysInMonth,ProdDays)
    return DaysDown , DaysInMonth



def Check_Valid_Producer(data,Time_Trsh,Diff_days):
    
    # this function checks whether the well is a valid producer for forecasting and gives
    # the index of when the well gone offline by checking the catastrophic failure criterias
    flag= 1;
    lastProdindx=0
    
    # Diff_days=3 # total days its okey for the well not to be producing in a month
      
    if bool(data)==False:
        flag=0
        return flag,lastProdindx,0
        
    """%------------------------------------------------------------
    % Check the days down for given data
    %------------------------------------------------------------"""
    oil      = np.array(data['oil_mo'],float)
    water    = np.array(data['water_mo'],float)
    Welldates= data['dates']
    proddays = np.array(data['proddays'],float)
    DaysDown,DaysInMonth = DownTime(Welldates,proddays)    
        
    """%------------------------------------------------------------
    % get the index of last producing day: the logic is
    % that the last fully producing month is just before the CF
    %------------------------------------------------------------"""
    
    if np.sum(np.abs(oil))==0: # never produced
        flag = 0
        return flag,lastProdindx,0
        
    if np.sum(np.abs(oil))==0 and np.sum(np.abs(water))!=0 : # its and injector
        flag = 0
        return flag,lastProdindx,0
    
    indx=[y for y in xrange(len(proddays)) if DaysInMonth[y]-proddays[y]<=Diff_days]
    
    indx.sort() #array has to be sorted in descending order. This will sort in ascending the mirror command next arranges in desc
    indx=indx[::-1]
    
    if len(indx)==0 :#and indx.size==0:    # OR if indx is a list => if not indx:
        if sum(proddays)!=0: 
            """zero production but non zero proddays -> strange well"""
            print ("Never produced a full month !!")        
        else:
            """no production what so ever"""
            print ("This well is an injector !!!")
        flag=0
        return flag,lastProdindx,0
    else: 
        """its a producer
        %----------------------------------------------------
        % get the temporary active situations after CF
        %----------------------------------------------------"""
        indxset1=[x for x in xrange(len(oil)) if oil[x]!=0]
        indxset1.sort()
        indxset1=indxset1[::-1]
        """index of start of CF with proddays<=Daysinmonth"""
        indx1=0
        if bool(indxset1):
            indx1=indxset1[0] 
        
        
        """indexes where qoil is zero"""
        indxtemp2=[z for z in xrange(len(oil)) if oil[z]==0]
        indxtemp2.sort()
        indxtemp2=indxtemp2[::-1]
        
        """----- need to find the first zero before the CF time happening"""
        indxset2=[indxtemp2[a] for a in xrange(len(indxtemp2)) if indxtemp2[a]>indx1]
        if len(indxset2)<1:
            indx2=0
        else:
            indx2=max(indxset2)
        
        #find index of last 0 before indxset2 
        temp=indxset2[0:indx2+1] #.tolist()
        temp=temp[::-1]
        if len(temp)<1:
            """the zero prod day before indx2"""
            indx3=0        
        else:
            indx3= min(temp) #temp.index(0)
        
        """if the production time between the CF and the last 0 point is smaller than 4 month
        % and the produced volume is less than 2500 bbl"""
        
        if((indx1-indx2)<=4) and (sum(oil[indx2:indx1]))<=2500  and ((indx2 - indx3) >= 4) and indx3==None: #and (~len(indx3)==0)
            indx=[indx[b] for b in xrange(len(indx)) if indx[b]<indx3]
            """update the indx since the temporary situation of active has happened"""
        
        """End of Temp situation"""
        a=indx[0]
        lastProdindx=a-int(proddays[a]<DaysInMonth[a]);
        
        # get the first nonzero production day
        # get the first non-zero production 
        try:
            firstProdindx = np.where(oil>0.0)[0][0]
        except:
            firstProdindx = 0
        
    """%-----------------------------------------------
        % check on whether changed to injector too soon
        %-----------------------------------------------"""
    
    if lastProdindx-firstProdindx<Time_Trsh: 
        """if well has been a producer less this number of months only"""
        print ("Changed to injector Too Soon !!")
        flag=0
    
    return flag,lastProdindx,firstProdindx
    

def create_table(conn,cursor,schema,table_name):
    """
    Create a new table to push the results 
    """    
    query = "CREATE TABLE IF NOT EXISTS `"+schema+"`.`"+table_name+"` (\
    `API_prod` BIGINT(20) NOT NULL COMMENT '',`report_date_mo` DATE NOT NULL COMMENT '',\
    `oil_mo` DOUBLE NULL COMMENT '',`oil_mo_mod` DOUBLE NULL COMMENT '')";
  
    cursor.execute(query)
  

def write_DB(conn,cursor,schema,table_name,results):
    """
    Write the results to the database
    """
    
    query = "INSERT INTO `"+schema+"`.`"+table_name+"` (`API_prod`,`report_date_mo`,`oil_mo`,`oil_mo_mod`)\
    VALUES (%s,%s,%s,%s);"
    
    for r in results:
        for i in xrange(len(r[0])):
            cursor.execute(query,(r[0][i],r[1][i],r[2][i],r[3][i]))
        conn.commit()
    conn.close() 


def LDtoDL (LD) :  
    result=defaultdict(list)
    #LD["dates"]=list(LD["dates"])
    for d in LD:
        #print d
        for key,val in d.items():
          result[key].append(val)
    return result
    
"""Tertiary methods just used for testing purposes"""

def write_csv(a,b):
    
    resultFile = open("Worthy_APIs_new.csv",'wb')
    wr = csv.writer(resultFile)
    for j in a:
        wr.writerow([j])
    resultFile.close()
    
    resultFile = open("Not_Worthy_APIs_new.csv",'wb')
    wr = csv.writer(resultFile)
    for k in b:
        wr.writerow([k])
    resultFile.close()

    
def write_data_csv(data):
    
    resultFile = open(str(data["API"][0])+"_2.csv",'wb')
    wr = csv.writer(resultFile)
    
    for i in range(len(data["dates"])):
        
        wr.writerow([data["dates"][i],data["proddays"][i],data["oil_mo"][i],data["oil_mo_mod"][i]])
        
    resultFile.close()