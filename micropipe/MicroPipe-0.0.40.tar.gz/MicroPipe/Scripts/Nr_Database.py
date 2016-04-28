#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/3/16
"""
import os,sys
import pandas as pd
from os.path import abspath
sys.path.append( os.path.split(abspath(__file__))[0]+'/../Lib/' )
from lpp import *
from Dependcy import *
usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-d", "--Database", action="store",
                  dest="DB_FILE",

                  help="Database File")


parser.add_option("-n", "--Nr", action="store",
                  dest="NR",

                  help="Nr Ghostz Aligment Result")


if __name__ == '__main__':
	(options, args) = parser.parse_args()

	
	
	nr_data_frame  = pd.read_table(options.NR, header = None)
	nr_data_frame.columns = ["Nr","Nr_Hit","Nr_Identity","Nr_AlignmentLength","Nr_MismatchNumber","Nr_GapNumber","Nr_QueryStart" ,"Nr_QueryEnd","Nr_SubjStart","Nr_SubjEnd","Nr_Eval","Nr_Bit_Score"     ]
	nr_data_frame["Name"] = nr_data_frame["Nr"].str.split(' ',1,return_type='frame')[0]
	nr_data_frame["Function"] = nr_data_frame["Nr"].str.split(' ',1,return_type='frame')[1]
	column_name = list( nr_data_frame.columns[-2:] )
	column_n2 = list( nr_data_frame.columns[1:-2] )	
	column_name.extend(column_n2)
	nr_data_frame = pd.DataFrame(nr_data_frame,columns=column_name)
	nr_data_frame.to_csv(options.DB_FILE,sep="\t",index =False)
	writer = pd.ExcelWriter('simple.xlsx', engine='xlsxwriter')
	nr_data_frame.to_excel(writer, sheet_name='Sheet1',index =False)
