#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/3/16
"""
import os,sys
from os.path import abspath
sys.path.append( os.path.split(abspath(__file__))[0]+'/../Lib/' )
from lpp import *
from Dependcy import *
usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-d", "--Database", action="store",
                  dest="DB_FILE",

                  help="Database File")


parser.add_option("-n", "--COG", action="store",
                  dest="COG",

                  help="eggNOG Ghostz Aligment Result")
if __name__ == '__main__':
	(options, args) = parser.parse_args()

	DB_FILE = open( os.path.abspath(options.DB_FILE),'a')
	data_hash = Ddict()
	COG_ANNO_DETAIL = open(   os.path.abspath(  options.COG ),'rU'   ) 
	COG_ANNO_DETAIL.next()
	
	
	

	for line in COG_ANNO_DETAIL:
		line_l = line[:-1].split("\t")
		name = line_l[0].split()[0]
		data_hash[name]["EggNOG_Hit"] = line_l[1]
		data_hash[name]["EggNOG_Eval"] = line_l[10]
		data_hash[name]["EggNOG_Bit_Score"] = line_l[11]
		data_hash[name]["EggNOG_Identity"] = line_l[2]
		data_hash[name]["EggNOG_StartQuery"] = line_l[6]
		data_hash[name]["EggNOG_EndQuery"] = line_l[7]
		data_hash[name]["EggNOG_Mismatch"] = line_l[5]
		data_hash[name]["EggNOG_EndSubj"] = line_l[9]
		data_hash[name]["EggNOG_StartSubj"] = line_l[8]
		data_hash[name]["EggNOG_NOG"]=line_l[12]
		data_hash[name]["EggNOG_NOG_Anno"]=line_l[13]
		data_hash[name]["EggNOG_NOG_Cat"]=line_l[14]
		data_hash[name]["EggNOG_NOG_CatAnno"]=line_l[15]
	
	for key in data_hash[name]:
		data_hash["title"][key]  = ""
	DB_FILE.write(Redis_trans(data_hash))
