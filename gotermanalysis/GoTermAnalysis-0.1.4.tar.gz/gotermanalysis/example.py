
import sys
import os
sys.path.append("package/lib/python" )

# from gotermanalysis import *

print dir()

def test():

	# #enrichment
	# tool = enrichment.Enrichment("localhost", "fanyu", "hellowork", "assocdb", "MLL2-MLL3.targetgenes.v9.csv", "", 0.01)
	# tool.enrich_csv()

	# #update
	# #DROP DATABASE IF EXISTS ASSOCDB
	# #CREATE DATABASE ASSOCDB
	# #mysql -h host -u user -p assocdb <"newestData.sql"
	# mydb = updateDB.UpdateDB("localhost", "fanyu", "hellowork", "assocdb", "gene_ontology/util/originalData/Homo_sapiens.gene_info.gene_info.txt")
	# mydb.update()

	# #downloadPubMed
	# print dir()
	# tool = downloadPubMed.DownloadPubMed("localhost", "fanyu", "hellowork", "assocdb")
	# tool.parse()

	# #create weighted goGraph structure
	# g=goStructure.GoStructure("localhost", "fanyu", "hellowork", "assocdb", "files.xml", "")
	# g.updateWeights()

	# #merge
	# gograph = merge.GoGraph("weightedGraph.xml", "MLL2-MLL3.targetgenes.v9.csv", "", 0.01, 3, "localhost", "fanyu", "hellowork", "assocdb")
	# gograph.gotermSummarization()

	os.system("java -cp .:abner.jar Tagging /Users/YUFAN/Desktop/parsedPubMeds /Users/YUFAN/Desktop/files.xml")



test()