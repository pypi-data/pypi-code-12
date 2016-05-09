import MySQLdb
import sys
import prettytable
from scipy.stats import hypergeom
import collections
import cPickle as pickle
import csv
import itertools
import os, csv, sys, math, time
import xml.dom.minidom
import networkx

'''
Parameters: 
a. weightGographData: a xml file which represents Gene Ontology structure, for example “weightedGoGraph.xml"
b. genelist: a csv file contains a genelist (Each input cvs file must contain only one genelist, which means it only has one row!!)
c. output: output_directory
d. p_value: minimum p-value required for go terms to be enriched
e. subGenelistNo: minimum number of genes required for go terms to be enriched

#Create a GoGraph object (Note: every time you use the gotermSummarization(), you need to create a new object)

gograph = merge.GoGraph(weightGographData, genelist, output, p_value, subGenelistNo, host, username, password, "assocdb")
gograph.gotermSummarization()

Result is in the output directory
'''


def checkDup(P_list):
	PTp = P_list
	PTp.sort()
	for i in (range(len(PTp)-1)):
		if PTp[i]==PTp[i+1]:
			return 1
	return 0

def Union(P_list1, P_list2):
	L_rets = []
	L_dic = {}
	for item in P_list1:
		L_rets.append(item)
		L_dic[item] = 1
	for item in P_list2:
		if not(L_dic.has_key(item)):
			L_rets.append(item)
	L_rets.sort()
	return L_rets

def Intersection(P_list1, P_list2):
	L_rets = []
	L_dic = {}
	for item in P_list1:
		L_dic[item] = 1
	for item in P_list2:
		if L_dic.has_key(item):
			L_rets.append(item)
	L_rets.sort()
	return L_rets

def Difference(P_list1, P_list2):
	#return P_list2 - P_list1
	L_rets = []
	L_dic = {}
	for item in P_list1:
		L_dic[item] = 1
	for item in P_list2:
		if not(L_dic.has_key(item)):
			L_rets.append(item)
	L_rets.sort()
	return L_rets

## hypergeometric function for probability value 
# @param white_balls_drawn -- associated gene in input genesubset
# @param population -- population (here use the offical home sapiens genes in NCBI)
# @param white_balls_in_population -- assoicated genes in population
# @param total_balls_drawn-- input genelist size
def hypergeom_function(white_balls_drawn, population, white_balls_in_population, total_balls_drawn):
	"""
	hypergeometric function for probability value 
	@param white_balls_drawn -- associated gene in input genesubset
	@param population -- population (here use the offical home sapiens genes in NCBI)
	@param white_balls_in_population -- assoicated genes in population
	@param total_balls_drawn -- input genelist size
	"""
	prob = 1-hypergeom.cdf(white_balls_drawn-1, population, white_balls_in_population, total_balls_drawn)
	return prob	
	
class GoGraph(networkx.DiGraph):

	#p_value_threshold is the threshold of P_Value of the Go term node in final result
	#subGeneListNo_threshold is the minimum number of genes in the Go term node in final result
	def __init__(self, weightGraph, genelist_csvfile, output_directory, p_value_threshold, subGeneListNo_threshold, host, user, password, dbname):
		networkx.DiGraph.__init__(self)		
		self.association = 'Association_proteins'
		self.association_acc = 'Association_Accumulation'
		self.mapping = 'mapping_protiens'
		self.PV = 'P_value'
		self.TotalLost = 0.0
		self.db = MySQLdb.connect(host, user, password, dbname)
		self.genelist = self.getGeneListsWithCSV(genelist_csvfile)
		self.result = output_directory
		self.p_value = p_value_threshold
		self.subGeneListNo = subGeneListNo_threshold
		self.gene_GOterm = self.geneToGOtermAssoc()
		# print self.gene_GOterm
		self.GOterm_gene = self.GOtermToGeneAssoc()
		# print self.GOterm_gene
		self.NumberOfAllProtein = len(self.gene_GOterm)
		self.createDiGraph(weightGraph)

	## Return list of list of genes in given input file
	def getGeneListsWithCSV(self, genelist_csvfile):
		"""
		Return list of list of genes in given input file
		"""
		genelist = []
		reader = csv.reader(open(genelist_csvfile,"rb")) 
		for line in reader:
			genelist = line
		return genelist

	def geneToGOtermAssoc(self):
		gene_GOterm = {}
		cursor = self.db.cursor()
		query = "select distinct(offsymbol) from final_symbol_term"
		cursor.execute(query)
		query_result = cursor.fetchall()
		for gene in query_result:
			query2 = "select acc from final_symbol_term where offsymbol='%s'"%(gene[0])
			cursor.execute(query2);
			query2_result = cursor.fetchall()
			assocTerms = []
			for term in query2_result:
				assocTerms.append(term[0])
			gene_GOterm[gene[0]] = assocTerms
		# print len(gene_GOterm)
		return gene_GOterm

	def GOtermToGeneAssoc(self):
		GOterm_gene = {}
		cursor = self.db.cursor()
		query = "select distinct(acc) from final_symbol_term"
		cursor.execute(query)
		query_result = cursor.fetchall()
		for term in query_result:
			query2 = "select offsymbol from final_symbol_term where acc='%s'"%(term[0])
			cursor.execute(query2);
			query2_result = cursor.fetchall()
			assocGenes = []
			for gene in query2_result:
				assocGenes.append(gene[0])
			GOterm_gene[term[0]] = assocGenes
		# print GOterm_gene
		# print len(GOterm_gene)
		return GOterm_gene

	##Read weightgraph, build a child to parent directed go term structure
	def readWeights(self, weightedGraph):
		xmldoc = xml.dom.minidom.parse(weightedGraph)
		xmlData = xmldoc.firstChild
		goTermList = xmlData.getElementsByTagName('term')

		goGraph = {}
		for term in goTermList:
				go = term.attributes['id']
				goGraph[go.value] = {}
				parentList = term.getElementsByTagName('parent')
				for parent in parentList:
					parGO = parent.attributes['id']
					goGraph[go.value][parGO.value] = {}
					edgeList = parent.getElementsByTagName('edge')
					for edge in edgeList:
						edgeType = edge.attributes['type']
						goGraph[go.value][parGO.value] = float(edge.firstChild.data)
						# print go.value, parGO.value, float(edge.firstChild.data)
		return goGraph

	##Construct a directed go term graph based on the go term structure returned from readweights function
	def createDiGraph(self, weightGraph):
		'''
		create edge-weighted Goterm structure
		'''
		GoStructure = self.readWeights(weightGraph)
		for child in GoStructure:
			for parent in GoStructure[child]:
				self.add_edge(child, parent)
				self.edge[child][parent]['weight'] = GoStructure[child][parent]
		self.node_AssociationProteinData()
		self.node_Depth()

	def propagate_AssociatedProteins(self):
		Top_sort_nodes = networkx.topological_sort(self)
		for node in Top_sort_nodes:
			Parents = self.successors(node)
			AssoSelf = self.node[node][self.association_acc]
			for nodeParent in Parents:
				AssoParent = self.node[nodeParent][self.association_acc]
				self.node[nodeParent][self.association_acc] = Union(AssoSelf,AssoParent)

	def node_AssociationProteinData(self):
		for goterm in self.nodes():
			self.node[goterm]['level'] = 1000000000
			if self.GOterm_gene.has_key(goterm):
				self.node[goterm][self.association] = self.GOterm_gene[goterm]
				self.node[goterm][self.association_acc] = self.GOterm_gene[goterm]
			else:
				self.node[goterm][self.association] = []
				self.node[goterm][self.association_acc] = []
			self.node[goterm][self.mapping] = []
		self.propagate_AssociatedProteins()

	def node_Depth(self):
		Top_sort_nodes = networkx.topological_sort(self, reverse = True)
		self.node[Top_sort_nodes[0]]['level'] = 1
		for node in Top_sort_nodes:
			children = self.predecessors(node)
			for child in children:
				if self.node[child]['level'] > self.node[node]['level']+1:
					self.node[child]['level'] = self.node[node]['level']+1
		
	##map gene list to Go Terms, use association_acc to calculate PV
	def node_Mapping_ProteinList_PV(self, genelist):
		Gene_List_Associated = []
		for gene in genelist:
			if self.gene_GOterm.has_key(gene):
				Gene_List_Associated.append(gene)
		self.NumberOfProtein_InList = len(Gene_List_Associated)
		# print self.NumberOfProtein_InList

		for nodeID in self.nodes():
			# genes directly associated with this term
			# print nodeID
			P_Association = self.node[nodeID][self.association]
			# print P_Association
			# all genes associated with this term, inlcuding genes propagating from children
			P_Association2 = self.node[nodeID][self.association_acc]
			# print P_Association2
			P_protein = Intersection(genelist, P_Association)
			# print P_protein_acc
			self.node[nodeID][self.mapping] = P_protein
				
			newPV = hypergeom_function(len(P_protein), self.NumberOfAllProtein, len(P_Association2), self.NumberOfProtein_InList)
			self.node[nodeID][self.PV] = newPV
	
	#remove irrelavant node	
	def simplify_Goterm_Structure(self):
		Top_Order = networkx.topological_sort(self)
		for node in Top_Order:
			if len(self.node[node][self.mapping])==0 and len(self.predecessors(node)) == 0:
				self.remove_node(node)

	def calculate_lost(self, source_node, target_node):
		edgeWeight = self.edge[source_node][target_node]['weight']
		lost = edgeWeight*len(self.node[source_node][self.mapping])
		#print 'edgeWeight=',edgeWeight, 'sizeOfSource=',len(self.node[P_nodeSource][self.mapping]),'lost=',lost
		return lost

	## merge association protien in source node into target node,
	# update the P_value of the target node, and delete source node from the graph
	# use self.association_acc to calculate PV
	def merge_nodes(self, source_node, target_node):
	
		lost = self.calculate_lost(source_node, target_node)
		P_Source = self.node[source_node][self.association]
		P_Target = self.node[target_node][self.association]
		self.node[target_node][self.association] = Union(P_Source, P_Target)

		#---
		if checkDup(self.node[target_node][self.association]) == 1:
			print '---Asso dup'

		P_Source2 = self.node[source_node][self.mapping]
		P_Target2 = self.node[target_node][self.mapping]
		self.node[target_node][self.mapping] = Union(P_Source2, P_Target2)

		#---
		if len(self.node[target_node][self.mapping])>self.NumberOfProtein_InList:
			print len(P_Source2), len(P_Target2)
		if checkDup(self.node[target_node][self.mapping]) ==1:
			list(set(self.node[target_node][self.mapping]))
			print '!!! mapping Dup'

		newPV = hypergeom_function(len(self.node[target_node][self.mapping]), self.NumberOfAllProtein, len(self.node[target_node][self.association_acc]), self.NumberOfProtein_InList)
		self.node[target_node][self.PV] = newPV
		self.TotalLost += lost
		Children_S = self.predecessors(source_node)
		Children_T = self.predecessors(target_node)
		C_S_sub_T = Difference(Children_T,Children_S)
		#print 'Children of S not of T=',C_S_sub_T
		for proteinTp in C_S_sub_T:
			self.add_edge(proteinTp,target_node)
			self.edge[proteinTp][target_node]['weight'] = self.edge[proteinTp][source_node]['weight'] + self.edge[source_node][target_node]['weight']
		self.remove_node(source_node)

	## return the name of a given term
	# @param term
	def getTermName(self,term):	
		"""
		return the name of a given term
		@param term
		"""	
		cursor=self.db.cursor()
		query="select name from term where acc='%s'"%(term)
		cursor.execute(query)
		query_result=cursor.fetchall()
		return query_result[0][0]

	## use P_GotermNumber to summarizate a given list of proteins
	# Topologically sort at first	
	# Format of merge result: {Goterm_1:[a list of genes_1,value_1], Goterm_2:[a list of genes_2,value_2],....}
	# Goterm_1: Goterm ID that is used to summarize the given list of gene.
	# a list of genes_1: a subset of genes (in the given list of gene) that are annotated by Goterm_1.
	# value_1: the level of Goterm_1 on the Go Ontology. The root note is in level 1.
	def gotermSummarization(self):

		self.node_Mapping_ProteinList_PV(self.genelist)
		self.simplify_Goterm_Structure()
		
		#Topologically sort all node, the first element is a leaf and the last element is the root
		New_Top_sort_nodes = networkx.topological_sort(self)

		#go through all nodes in topological order from leaves to the root
		for node_child in New_Top_sort_nodes:
			nodePV = self.node[node_child][self.PV]
			nodeSize = len(self.node[node_child][self.mapping])
			#if the current node's pv or size is not constrained by the setting conditions, merge this node to the closest parent node.
			if nodePV > self.p_value or nodeSize < self.subGeneListNo:
				# print "Merge is True"
				parents = self.successors(node_child)
				minWeight = 100000; 
				flag = 'none'
				for node in parents:
					if self.edge[node_child][node]['weight'] < minWeight:
						minWeight = self.edge[node_child][node]['weight']
						flag = node
				if flag == 'none':
					pass
					# print "no close parent find"
				else:
					# print "merge " + node_child + " to " + flag
					self.merge_nodes(node_child,flag)
		# print "Finish Merge"

		# print "Result#############################################"
		Goterms = {}
		for go in self.nodes():
			if len(self.node[go][self.mapping])>0:
				Goterms[go] = [self.node[go][self.mapping], self.node[go]['level']]
				# print go
				# print Goterms[go]

		with open(self.result + 'merge_result.csv', 'wb') as csvfile:
				writer=csv.writer(csvfile, delimiter=',')
				writer.writerow(["Total_lost", self.TotalLost])
				writer.writerow(["GOTerm", "TermName", "Level" , "SubGeneList"])
				for go in Goterms:
					writer.writerow([go, Goterms[go][1], self.getTermName(go), Goterms[go][0]])
	