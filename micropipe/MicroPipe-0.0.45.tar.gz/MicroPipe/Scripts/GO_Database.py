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
usage = '''usage: python2.7 %prog -i input_path -t [The type you want]'''
parser = OptionParser(usage =usage ) 
parser.add_option("-i", "--INPUT", action="store", 
                  dest="input",
                  default = './', 
                  help="Input File")

parser.add_option("-o", "--end", action="store", 
                  dest="output", 
                  help="OUTPUT Data")
if __name__ == '__main__':

	(options, args) = parser.parse_args() 
	DB_FILE = open(os.path.abspath(options.output)  ,'a')
	data_hash = Ddict()
	GO_ANNO_DETAIL = open(options.input,'rU')
	GO_ANNO_DETAIL.next()
	for line in GO_ANNO_DETAIL:
		line_l = line[:-1].split("\t")
		name = line_l[0].split()[0]
		data_hash[name]["GO_BiologicalProcess"]=line_l[1]
		data_hash[name]["GO_MolecularFunction"]=line_l[2]
		data_hash[name]["GO_CellularComponent"]=line_l[3]
	for data in data_hash[name]:
		data_hash["title"][data] = ""
	
	DB_FILE.write(Redis_trans(data_hash))