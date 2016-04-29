#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/12/15
"""
from lpp import *
import numpy as np
from ALL_XLS_Combine import combine_xls
usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-o", "--OUTPUT", action="store",
                  dest="OUTPUT",

                  help="OUTPPUT File")


parser.add_option("-i", "--INPUT", action="store",
                  dest="INPUT",

                  help="Input Path")



if __name__ == '__main__':
	(options, args) = parser.parse_args() 
	input_path = options.INPUT
	result_list = []
	stat_hash = Ddict()
	for base_path,dir_name,file_list in os.walk(input_path):
		for e_f in file_list:
			if e_f.endswith(".xlsx"):
				result_list.append( base_path+'/'+e_f )
			elif e_f.endswith(".txt"):
				if 'phage_finder_info' in e_f:
					continue
				DATA= open(base_path+'/'+e_f)
				DATA.next()
				name = os.path.basename(e_f).rsplit('.',1)[0]
				for line in DATA:
					line_l = line.strip().split(": ")
					stat_hash[name][line_l[0]] = int(line_l[1] )
					
			elif e_f.endswith(".fna"):
				RAW= fasta_check(  open(base_path+'/'+e_f) )
				for t,s in RAW:
					name = t[1:].split()[0]
					name = name.split('|')[-1]

					
					s1 = re.sub("\s+", "", s)
					s1 = s1.upper()
					stat_hash[name]['gc_base'] = s1.count("G")+s1.count("C")
			elif e_f.endswith(".ffn"):
				RAW= fasta_check(  open(base_path+'/'+e_f,'rU') )
				name = e_f.rsplit(".",1)[0]
				gc_coding_all = 0
				conding_all = 0
				num = 0
				for t,s in RAW:
					num+=1


					s1 = re.sub("\s+", "", s)
					s1 = s1.upper()
					gc_coding_all += s1.count("G")+s1.count("C")
					conding_all+=len(s1)
				stat_hash[name]["coding_all"] = conding_all

				stat_hash[name]["coding_gc"] = gc_coding_all
				
					
	data = pd.DataFrame.from_dict( stat_hash )				
	data.fillna(0)
	data["total"] = data.sum(1)
	data2 = data.T
	data2["Intergenetic Region%"] = 100.0* (data2["bases"] - data2["coding_all"] )/data2["bases"]
	data2["GC%"] = 100.0* data2["gc_base"] /  data2["bases"]
	data2["Gene GC%"] = 100.0* data2["coding_gc"] /  data2["coding_all"] 
	data2["Intergenetic GC%"] =   100.0*(data2["gc_base"] - data2["coding_gc"]) / (data2["bases"] - data2["coding_all"]) 
	data2["Gene Avg Length"] =  data2["coding_all"]/data2["gene"] 
	data2["Intergenetic Avg Length"] =  (data2["bases"] - data2["coding_all"] )/data2["gene"] 
	
	del data2["gc_base"]
	del data2["coding_gc"]
	del data2["coding_all"]
	data2 = data2.fillna(0)

	for key in data2.columns:
		if "%" not in key:
			data2[key] =data2[key].astype(int)
		else:
			data2[key] = data2[key]

	STAT = os.path.dirname(options.OUTPUT)+'/stats.tsv'
	data2.to_csv(STAT,sep='\t')
	if result_list:
		result_data = combine_xls(result_list)
	
		result_data.to_csv(options.OUTPUT,index=False,sep="\t")
