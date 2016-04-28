#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/1/11
"""
import os,sys
from os.path import abspath
sys.path.append( os.path.split(abspath(__file__))[0]+'/../Lib/' )
from lpp import *
from Dependcy import *
usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-i", "--COG", action="store",
                  dest="COG",

                  help="COG Mapping File")


parser.add_option("-o", "--Cat", action="store",
                  dest="CAT",

                  help="CAT Category")
if __name__ == '__main__':
	(options, args) = parser.parse_args()
	
	cog_mapping =Ddict() 
	RAW = open(options.COG ,'rU')
	RAW.next()
	cog_detail = {}
	for line in RAW:
		line_l = line.split("\t")
		if not line_l[-2]:
			continue
	
		cog_annotation = line_l[-1].strip()
		cog_cate = line_l[-2]
		cog_detail[cog_cate] = cog_annotation
		cog_mapping[cog_cate][line_l[0]]
	
	END = open(options.CAT,'w')
	END.write("Category\tAnnotation\tGene Number\n")
	for key ,val in cog_detail.items():

		END.write(key+'\t'+val +'\t%s\n'%(   len(cog_mapping[key])))
