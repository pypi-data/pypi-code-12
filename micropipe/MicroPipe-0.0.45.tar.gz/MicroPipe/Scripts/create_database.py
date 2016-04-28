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


parser.add_option("-n", "--Nul", action="store",
                  dest="NUL",

                  help="Nucleotide Sequence")

parser.add_option("-g", "--GFF", action="store",
                  dest="GFF",

                  help="Gff File")

parser.add_option("-p", "--Pro", action="store",
                  dest="PRO",

                  help="Protein File")

parser.add_option("-f", "--Genome", action="store",
                  dest="Genome",

                  help="Genome File")



if __name__ == '__main__':
	db_hash = Ddict()
	(options, args) = parser.parse_args()
	GBK_FILE = open(options.Genome.rsplit(".",1)[0]+'.gbk','rU')
	GBKTMP = open(GBK_FILE.name+'_1','w')
	title_line = GBK_FILE.next()
	title_line = title_line.replace("_","")
	GBKTMP.write(title_line)
	
	for line in GBK_FILE:
		
		GBKTMP.write(line)
	GBKTMP.close()
	shutil.move(GBKTMP.name,GBK_FILE.name)
	DB_FILE = open(abspath(options.DB_FILE),'w')
	GENOME= fasta_check(open(options.Genome,'rU'))
	NEW_NAME = open(os.path.dirname(options.Genome)+'/tmp.fna','w')
	for t,s in GENOME:
		new_name = re.sub( "_$","", t[1:-1].split('|')[-1])
		NEW_NAME.write('>'+new_name+'\n')
		NEW_NAME.write(s)
	shutil.move(NEW_NAME.name,options.Genome )
	
	NUL = fasta_check(   open(   abspath(  options.NUL ),'rU'   )    )
	NUL_OUT =  open(   abspath(  options.NUL+'.out' ),'w'   )
	crispr_id =1
	for t,s in NUL:

		t = t[1:].strip()
		name = t.split()[0]
		if "SinobioCore" in  name:
			continue
			function = "CrispR Sequence%s"%(crispr_id)
			t = ">CrispRSeq%s\n"%(crispr_id)
			name = "CrispRSeq%s"%(crispr_id)
			NUL_OUT.write( t+s )
			crispr_id+=1
		else:
			NUL_OUT.write('>'+t+"\n"+s)
			try:
				function = re.search("^\S+\s+(.+)", t).group(1)
			except:
				continue

		db_hash[name]["Seq_Nucleotide"] = re.sub("\s+","",s)
		db_hash[name]["Seq_Nucl_Length"] = str(len(re.sub("\s+","",s)))
		db_hash[name]["Function"] = function
	shutil.move(NUL_OUT.name,options.NUL)

	GFF = open(abspath(options.GFF),'rU')
	GFF_NEW = open("/tmp/%s"%(os.getpid() ),'w')
	PHAGE   = open(os.path.split( GFF.name  )[0]+'/phage_finder_info.txt','w')


	for line in GFF:
		if "gnl|" in line:
			line = re.sub("gnl\|[^\|]+\|(\S+)","\\1",line)
			line = re.sub("_(\s+)","\\1",line)
			GFF_NEW.write(line)
		else:
			GFF_NEW.write(line)
		if line.startswith("##sequence"):
			
			all_seq_length = re.search("(\d+)\n", line).group(1)
			all_seq_name = line.split()[1]

		if "product=" not in line:
			continue
		name = re.search("\tID\=([^;]+)", line).group(1)
		source =  name.rsplit("_",1)[0]
		line_l = line.split("\t")
		kind,start,stop,frame =line_l[2], line_l[3],line_l[4],line_l[6]
		db_hash[name]["Ref_Source"] = source
		db_hash[name]["Kind"] = kind
		db_hash[name]["Ref_Start"] = start
		db_hash[name]["Ref_Stop"] = stop
		db_hash[name]["Ref_Frame"] = frame

		product = re.search("product\=([^\;]+)",line).group(1)
		if frame=='-':
			start,stop = stop,start
		PHAGE.write(   "\t".join( [all_seq_name,all_seq_length,name,start,stop,product]  )+'\n'      )
	GFF_NEW.close()
	shutil.move(GFF_NEW.name,GFF.name)
	PRO = fasta_check(open(abspath(options.PRO),'rU'))
	for t,s in PRO:
		try:
			t = t[1:].strip()
			name,anno = t.split(" ",1)
		except:
			continue
		db_hash[name]["Seq_Protein"] = re.sub("\s+","",s)
		db_hash[name]["Seq_Protein_Length"] = str(  len( re.sub("\s+","",s) )  )
	DB_FILE.write("\t".join(  ["Name","Kind","Function","Ref_Source",	"Ref_Start","Ref_Stop","Ref_Frame",	"Seq_Nucleotide","Seq_Nucl_Length",	"Seq_Protein","Seq_Protein_Length"]
	                          )+'\n'
	              
	              
	              )
	title_list = [ "Kind","Function","Ref_Source",	"Ref_Start","Ref_Stop","Ref_Frame",	"Seq_Nucleotide","Seq_Nucl_Length",	"Seq_Protein","Seq_Protein_Length"]
	for key in db_hash :
		DB_FILE.write(key)
		for key2 in title_list:
			if key2 not in db_hash[key]:
				db_hash[key][key2]=""
				
			DB_FILE.write('\t'+db_hash[key][key2])
		DB_FILE.write('\n')
	DB_FILE.close()
	data_frame = pd.read_table(DB_FILE.name)
	data_frame = data_frame.sort(columns=["Ref_Source","Ref_Start"   ],axis=0)
	data_frame.to_csv( DB_FILE.name,sep="\t",index=False  )