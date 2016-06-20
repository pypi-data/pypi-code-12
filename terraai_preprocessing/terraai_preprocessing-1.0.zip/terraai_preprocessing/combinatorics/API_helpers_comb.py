# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 16:03:16 2015
Combinatorics helper 
Reading from the database
@author: Administrator
"""
import MySQLdb
import numpy as np
from datetime import datetime
import calendar

def establish_DBconn(user,password,schema="public_data",): 
    """
    Establish connection with the database using the given parameters.
    """
    cnx = { 'host': 'navjot.c4lstuf6msdr.us-west-2.rds.amazonaws.com','user':user,'password': password,'db': schema}
    conn = MySQLdb.connect(cnx['host'],cnx['user'],cnx['password'], cnx['db'])
    cursor = conn.cursor() 
    return cursor

def get_WellPids(cursor,table_name,schema="public_data",):
    """
    Gets the well ids from the table data is being retrieved. 
    """
    #start=time.time()
    print("Reading well IDs")
    query = "SELECT distinct(API_prod) FROM "+schema+"."+table_name+";"
    cursor.execute(query)
    row   = cursor.fetchall()
    unique_pids=[v[0] for v in row]
    
    return sorted(unique_pids)
    
def get_WellData(cursor,wellID,table_name,schema="public_data"):
     """
     Reads the data from the the MySql DB table.
     """
     #start=time.time()
     query="SELECT oil,water,prod_days,report_date \
             FROM "+schema+"."+table_name+" WHERE API_prod=%s ORDER BY report_date ASC ;"
     cursor.execute(query,[wellID])
     row = cursor.fetchall()
    
     Welldates,proddays,qoil,qwat=[],[],[],[]
     """
     Make single lists for each column they are bound by index.
     """
     
     for value in row:
        qoil.append(value[0])
        qwat.append(value[1])
        proddays.append(int(value[2]))  
        Welldates.append(value[3].strftime("%Y-%m-%d")) # extract operating dates for this well
     #print("Time Taken : "+str(round(((time.time()-start)),2))+" secs")
     #print 
    
     return Welldates,proddays,qoil,qwat
     


def diff_month(d1str,d2str):
	#find difference between two dates in months
    d1 = datetime.strptime(d1str , '%Y-%m-%d')
    d2 = datetime.strptime(d2str , '%Y-%m-%d')
    try:
        return (d2.year - d1.year)*12 + (d2.month - d1.month)
    except:
        import pdb; pdb.set_trace()
        print "Exception.  The argument was {}.".format(d2)
        return 0 #np.NaN
        
def add_months(sourcedatestr,months):
    sourcedate = datetime.strptime(sourcedatestr , '%Y-%m-%d')    
    
    month = [ sourcedate.month - 1 + months[i] for i in xrange(len(months)) ]
    year  = [int(sourcedate.year + x / 12 ) for x in month]
    month = [ month[i] % 12 + 1 for i in xrange(len(month)) ]
    day   = [min(sourcedate.day , calendar.monthrange(year[i],month[i])[1]) for i in xrange(len(year)) ]
    
    datestring = [(str(year[i])+"-"+str(month[i])+"-"+str(day[i])) for i in xrange(len(year))]   
    dates      = [datetime.strptime(datestring[i] , '%Y-%m-%d') for i in xrange(len(datestring))]    
    return datestring , dates
    
def imputeMissingData(dataIn):
    """finds missing months in the Welldates and inserts 0 for qoil, qwat at the corresponding indexes"""
    
    # determine the number of month between first and last dates given in data
    WellStartDate = dataIn['dates'][0] 
    monthnumsIndx = np.array([diff_month(WellStartDate,x) for x in dataIn['dates']])
    
    # generate the continuous month dates strings for the new data
    allindx       = range(max(monthnumsIndx)+1)
    datesstr,_    = add_months(WellStartDate,allindx)
    
    # imput nans for missing data
    dataOut = dataIn.copy()
    for (i , key) in enumerate(dataIn):
        # Update the measured values series by imputing NaNs when data is missing
        dataOut[key] = np.empty(shape=len(datesstr) , dtype=type(dataIn[key]))#np.array(dataIn[key],dtype=type(dataIn[key][0]),ndmin=len(datesstr))
        dataOut[key].fill(0.0) # can change into zero if want 0
        dataOut[key][monthnumsIndx] = dataIn[key]

    
    # get linear time index of months and the continuous dates strings
    dataOut['MonthIndx'] = np.asarray(range(np.nanmax(monthnumsIndx)+1))  #range(monthnumsIndx[-1])
    dataOut['dates']     = np.asarray(datesstr)
    
    return dataOut
	

def inverse_cumsum(cumulative):
	#given a cumulative find the original values
    output = [0] * len(cumulative)
    
    for i in xrange(len(cumulative)-1):
        output[i+1] = cumulative[i+1] - cumulative[i]
    output[0]=cumulative[0]
    
    return output

def matches(a,b):
    """function to objectively test how similar the decoded values are of qoil and qwat"""
    c = [i for i,j in zip(a,b) if i==j]
    return round((float(len(c))/len(a))*100,2)