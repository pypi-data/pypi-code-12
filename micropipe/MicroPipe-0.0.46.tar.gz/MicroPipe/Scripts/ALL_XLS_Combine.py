#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/12/15
"""
from lpp import *
import pandas
usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-o", "--OUTPUT", action="store",
                  dest="OUTPUT",

                  help="OUTPPUT File")


parser.add_option("-i", "--INPUT", action="store",
                  dest="INPUT",

                  help="Input Path")
parser.add_option("-g", "--GFF", action="store",
                  dest="GFF",

                  help="GFF_XLS")
def combine_xls( data_list   ):
	out_frame = pd.read_table(data_list[0]).drop_duplicates()
	out_frame = out_frame.where((pd.notnull(out_frame)), None)
	new_list = []
	for each_data in data_list[1:]:
		if "07.Crispr" in each_data:
			new_list.append(each_data)
		else:
			new_list.insert(0, each_data)

	for each_data in new_list:
		new_frame = pd.read_table(each_data).drop_duplicates()
		new_frame = new_frame.where((pd.notnull(new_frame)), None)
		on_need = list(out_frame.columns  & new_frame.columns)
		if "Kind" in on_need or "07.Crispr" in each_data:
			out_frame = pd.DataFrame.merge(out_frame, new_frame, on=on_need, how='outer')
			
		else:
			out_frame = pd.DataFrame.merge(out_frame, new_frame, on="Name", how='outer')
	return out_frame.drop_duplicates()

if __name__ == '__main__':
	(options, args) = parser.parse_args() 
	input_path = options.INPUT
	start_frame = os.path.abspath(options.GFF)
	result_list = [start_frame]
	already_name = os.path.basename(start_frame)
	for base_path,dir_name,file_list in os.walk(input_path):
		for e_f in file_list:
			if "04.OtherDatabase" in base_path:
				if e_f == "All_HasAnnotation.xlsx":
					print (e_f)
					result_list.append( base_path+'/'+e_f )
			elif "04.OtherDatabase" in os.path.abspath(base_path):
				continue
			elif e_f.endswith(".xls"):
				
				if e_f ==already_name:
					continue
				result_list.append( base_path+'/'+e_f )
	result_data = combine_xls(result_list)
	for i in xrange(0,len(result_data)):

		if not  pd.isnull(result_data.loc[i,"KEGG_Hit"]):
			result_data.loc[i,"Function"] = str(result_data.loc[i,"KEGG_Hit"]).split(' ',1)[1].strip()

	result_data =result_data.sort(["Ref_Source","Ref_Start"])
	check_path( os.path.dirname(options.OUTPUT)  )
	result_data.to_csv(options.OUTPUT,index=False,sep="\t")

	
	
