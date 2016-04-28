#!/usr/bin/env python
#coding:utf-8
# Author:  LPP --<lpp1985@hotmail.com>
# Purpose: 
# Created: 2011/5/27
import os,sys
from os.path import abspath
sys.path.append( os.path.split(abspath(__file__))[0]+'/../Lib/' )
from lpp import *

from GO_obo_parse import *

go_id = Ddict()
id_go = Ddict()
number_check = Ddict()
usage = '''usage: python2.7 %prog -i input_path -t [The type you want]'''
parser = OptionParser(usage =usage ) 
parser.add_option("-i", "--INPUT", action="store", 
                  dest="input",
                  default = './', 
                  help="Input File")

parser.add_option("-o", "--end", action="store", 
                  dest="output", 
                  help="OUTPUT Data")

def recall( leaf ):
	global root_static,need_check,go_id,number_check
	if   GO_ROOT.select( AND(GO_ROOT.q.Go==leaf,GO_ROOT.q.Rank==2)).count():
		root_static[ leaf ][ need_check ] = ''

		for each_id in go_id[leaf]:		
			number_check[ leaf ][ each_id ] = ''
	else:
		for each_son in  GO_SON.select(GO_SON.q.Son==leaf ):
			father = each_son.Father
			if not  GO_ROOT.select( AND(GO_ROOT.q.Go==father,GO_ROOT.q.Rank==2) ).count():

				recall( father )
			else:
				root_static[ father ][ need_check ] = ''

				for each_id in go_id[need_check]:
					number_check[ father ][ each_id ] = ''



if __name__ == '__main__':
	(options, args) = parser.parse_args() 
	RAW = open( options.input,'rU'  )
	
	RAW.next()
	geneid_id = Ddict()
	for line in RAW:
	
		line_l = line.split('\t')
		name = line_l[0].split()[0]
		gi = re.search( '(?:sp|tr)\|(\w+)' ,line_l[1] ).group(1)
		
		all_mapped_go = UNIPROT_GO.select(UNIPROT_GO.q.Uniprot==gi)
		for each_go in all_mapped_go:
			go_term = each_go.Go
	
			all_changed_go = GO_ALTER.select(GO_ALTER.q.Go_raw==go_term)
			if all_changed_go.count():
				for each_changed_go in all_changed_go:
					each_altered = each_changed_go.Change_to
					defination  = GO_DEF.select( GO_DEF.q.Go== each_altered )[0].Def
					
					go_id[ each_altered][ name ] ='-\t-\t->\t'+name+'\t'+gi+'\t'+each_altered+'\t'+defination
					id_go[ name ][ each_altered ] = ''	
			else:
				defination  = GO_DEF.select( GO_DEF.q.Go== go_term )[0].Def
				go_id[ go_term ][ name ] = '-\t-\t->\t'+name+'\t'+gi+'\t'+go_term+'\t'+defination
				id_go[ name ][ go_term ] = ''			
	
	root_static = Ddict()
	
	for each_go in go_id:
		need_check = each_go
		recall( each_go )
	
	
	END = open( options.output+'.GO-mapping.list','w'  )
	END.write( 'ROOT\tROOT_DEF\tNumber\tID\tUnirpotKB\tGO\tGO_DEF\n'  )
	for each_go in reversed( sorted(root_static,key= lambda x: len( number_check[ x  ]) ) ):
		defination =  GO_DEF.select( GO_DEF.q.Go== each_go )[0].Def
		END.write( each_go+'\t'+ defination +'\t%s\n'%( len( number_check[ each_go  ]  )  ) )
		for each_son in root_static[ each_go ]:
			for each_id in go_id[ each_son ]:
	
				END.write(  go_id[ each_son ][  each_id ]+'\n' )
	
	
	
	
	END_DETAIL = open( options.output+'.GO-mapping.detail','w'  )
	for each_id in id_go:
		END_DETAIL.write( each_id+'\t'+'\t'.join( id_go[ each_id ]  ) +'\n' )


