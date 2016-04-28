#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2015/3/3
"""
from parse import *
usage = '''usage: python2.7 %prog [options]
			    '''
parser = OptionParser(usage =usage )    
parser.add_option("-d", "--Database", action="store",
                                       dest="database",
                                       help="Database Name")
parser.add_option("-o", "--OUTPUT", action="store",
                                          dest="output",
                                          help="output File Name")  
parser.add_option("-t", "--Total", action="store_true",
                  default=False,
                  dest="both",
                  help="both directon?")  
(options, args) = parser.parse_args()	
Dbname = options.database
output = options.output
both =  options.both
Ddatabase_engine = create_engine(  "sqlite:///%s/%s"%(base_dir,Dbname) )
Ddatabase_engine.connect()
Base = declarative_base()
Session = sessionmaker( bind = Ddatabase_engine  )
session = Session()	
all_data = session.query(Mapping_Property_Table).filter(Mapping_Property_Table.Id==2).order_by(Mapping_Property_Table.Id)
if both :
	total_genes = [ session.query(Gene_Ko_Table).filter(Gene_Ko_Table.Property_Id==2),session.query(Gene_Ko_Table).filter(Gene_Ko_Table.Property_Id==3)]
else:
	total_genes = [session.query(Gene_Ko_Table).filter(Gene_Ko_Table.Property_Id==2)]
END = open(output+"_detail.tsv",'w')
END.write("Name\tKO\tPathway\tSituation\n")
# END2 = open(output+"_Pathway.tsv","w")
# END2.write("Name\tPathwayID\tPathwayName\tSituation")
for all_genes in total_genes:
	for each_gene in all_genes.group_by(Gene_Ko_Table.Gene_id):
		all_ko = all_genes.filter(Gene_Ko_Table.Gene_id == each_gene.Gene_id).group_by(Gene_Ko_Table.Ko_id)
		ko_sub = all_ko.subquery()
		need_pathway = session.query(Association_Table).join(ko_sub,Association_Table.KO_Id==ko_sub.c.Ko_id).group_by(Association_Table.Pathway_Id)
		END.write(each_gene.Gene.Name)
		output_ko_list = [i.Ko.Name+': '+i.Ko.Description for i in all_ko    ]
		output_ko = "||".join(output_ko_list)
		# for i in need_pathway:
			# END2.write(each_gene.Gene.Name +'\t'+i.Pathway.Name+'\t'+i.Pathway.Description+"\t"+each_gene.Property.Property+'\n')
		output_pathway = "||".join([i.Pathway.Name+': '+i.Pathway.Description for i in need_pathway    ])
		END.write("\t"+output_ko+'\t'+output_pathway+'\t'+each_gene.Property.Property+'\n')
		
		
