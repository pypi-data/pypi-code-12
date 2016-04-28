#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/1/23
"""
import sys
from GO_obo_parse import *
RAW = open(sys.argv[1],'rU')
END = open(sys.argv[2],'w')
RAW.next()
END.write("Component\tFunction\tGeneNumber\n")
data_hash = Ddict()
for line in RAW:
	line_l = line.split("\t")
	if line.startswith("GO:"):
		function =line_l[1]
		component =  GO_COMPONENT.select(GO_COMPONENT.q.Go==line_l[0])[0].Compent
		component = component.capitalize().replace("_"," ")
	else:
		gene = line_l[3]
		data_hash[component][function][gene] = ""

for compe,func_hash in data_hash.items():
	for func ,gene_hash in func_hash.items():
		
		END.write(compe+'\t'+func+'\t%s\n'%(len(gene_hash)))

		
