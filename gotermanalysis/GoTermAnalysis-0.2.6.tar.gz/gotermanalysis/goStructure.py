import MySQLdb
import networkx as nx
from lxml import etree as ET
import string
import sys
import porterStemmer
from stopWords import StopwordList
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import math
import xml.dom.minidom
import sets
import os

nltk.download('all')
"""
This part builds a GOterm graph structure, and calculate the new weights in this structure

Parameters:
a. inputfile: parsed pubmeds with ABNER
b. output_filepath: directory to store the output file,  output file is a GO term graph structure

Example of how to update weights:
g=goStructure.GoStructure(host, username, password, "assocdb”, inputfile, output_filepath)
g.updateWeights()
"""
class GoStructure:
	## Class constructor. It has 5 fields: a directed Graph, a database connector, a term-wordvector dictionary, a term-pubmed dictionary 
	# @param host
	# @param user
	# @param password
	# @param dbname
	# @param input_filepath
	# @param output_filepath
	def __init__(self, host, user, password, dbname, input_filepath, output_filepath):
		"""
		Class constructor. It has 5 fields: a directed Graph, a database connector, a term-wordvector dictionary, a term-pubmed dictionary 
		@param host
		@param user
		@param password
		@param dbname
		@param input_filepath
		@param output_filepath
		"""
		self.goGraph = nx.DiGraph()
		self.termWordvector = {}
		self.termPubMed = {}
		self.input_filepath = input_filepath
		self.output_filepath = self.determine_path() + "/extra_file/" + "weightedGraph.xml"
		self.stopwords = StopwordList(self.determine_path() + "/extra_file/stopwords.txt")
		self.db = MySQLdb.connect(host, user, password, dbname)

	## build GO term director graph, edge is from parent Node to child node
	def createGraph(self):
		"""
		build GO term director graph, edge is from parent Node to child node
		"""
		cursor = self.db.cursor();
		query = "SELECT term1_acc, term2_acc FROM termgraph"
		cursor.execute(query)
		query_result = cursor.fetchall()
		for row in query_result:
			parentNode = row[0]
			childNode = row[1]
			self.goGraph.add_edge(parentNode,childNode)

	## Build term-pubmed dictionary, term as key, set of pubmed is as value. Propagate associated pubmeds of child nodes to parent nodes
	def createTermPubMed(self):
		"""
		Build term-pubmed dictionary, term as key, set of pubmed is as value. Propagate associated pubmeds of child nodes to parent nodes
		"""
		nodesList = nx.topological_sort(self.goGraph, nbunch=None, reverse=True) 
		cursor = self.db.cursor()
		for i in range(len(nodesList)):
			term = nodesList[i]
			# print term
			query = "SELECT pmid FROM final_term_evidence WHERE acc = ('%s')"%(term)
			cursor.execute(query)
			query_result = cursor.fetchall()
			# print query_result	
			if len(query_result) == 0: 
				continue
			else:
				pmidSet = sets.Set()
				for row in query_result:
					pmidSet.add(row[0])
				if term in self.termPubMed:
					self.termPubMed[term].update(pmidSet)
				else:
					self.termPubMed[term] = pmidSet
				# print self.termPubMed.get(term)
				predecessors = self.goGraph.predecessors(term)
				if predecessors is None:
					continue
				else:
					for ancestorTerm in predecessors:
						# print ancestorTerm
						if ancestorTerm in self.termPubMed:
							self.termPubMed[ancestorTerm].update(pmidSet)
						else:
							self.termPubMed[ancestorTerm] = pmidSet

	## Returns the word vector of the Documented calculated on the fly
    # @param stemmer The function used to stem the words: takes a word, and the
    #       positions in the string of the word to be stemmed as input (p, i, j)
    # @param stopwords A list of stop words to removed from the word vector.
    #       An empty list is used if no list is provided.
	def wordVector(self, titleAbstract, stemmer, stopwords=[]):
		wordvector = {}
		punctuations = list(string.punctuation)
		titleAbstract = titleAbstract.lower()
		tokens = word_tokenize(titleAbstract)
		for word in tokens:
			if word in stopwords:
				continue;
			word = stemmer.stem(word, 0, len(word)-1)
			if word in wordvector:
				wordvector[word] += 1
			else:
					wordvector[word] = 1
		keys_to_remove = [key for key, value in wordvector.iteritems() if key in punctuations]
		for key in keys_to_remove:
				del wordvector[key]
		return wordvector

	## Return documents dictionary, pmid as key, a wordvector of title and abstract value
	# @oaram xmlfile parsed xmlfile contains all pubmed artiles
	# @return documents 
	def createDocuments(self, xmlfile):
		"""
		Return documents dictionary, pmid as key, a wordvector of title and abstract value
		@oaram xmlfile parsed xmlfile contains all pubmed artiles
		@return documents 
		"""
		articles = {}
		stemmer = porterStemmer.PorterStemmer()
		documents={}
		with open(xmlfile, 'rt') as f:
			tree = ET.parse(f)
			root = tree.getroot()
			for article in root.iter("PubMedArticle"):
				pmid = article.find("PMID").text
				titleAbstract = ""
				title = article.find("Title")
				if title is not None:
					titleAbstract=titleAbstract+title.text+". "
				elif title is None:
					pass
				abstract = article.find("Abstract").text
				if abstract is None:
					pass
				elif abstract is not None:
					titleAbstract = titleAbstract+abstract
				if titleAbstract == "":
					continue
				else:
					articles[pmid]=titleAbstract
		for key in articles:
			pmid = key
			if articles[key] is not None:
				titleAbstract = articles[key]
				wordvector = self.wordVector(titleAbstract, stemmer, self.stopwords);
				documents[pmid] = wordvector
		return documents

	## Add term definition to term - word vector dictionary
	def termDefWordvector(self):
		"""
		Add term definition to term - word vector dictionary
		"""
		cursor=self.db.cursor()
		stemmer = porterStemmer.PorterStemmer()
		punctuations = list(string.punctuation)
		nodes = self.goGraph.nodes() 
		for term in nodes:
			query= "SELECT TD.term_definition,T.name from term_definition as TD, term as T where T.id=TD.term_id and T.acc=('%s')"%(term)
			cursor.execute(query)
			query_result = cursor.fetchall();
			for row in query_result:
				wordvector={}
				termDef = row[0]
				termName = row[1]
				termDef = termDef.lower()
				termName = termName.lower()
				tokens = word_tokenize(termDef+","+termName)
				for word in tokens:
					if word in self.stopwords:
						continue;
					word = stemmer.stem(word,0,len(word)-1)
					if word in wordvector:
						wordvector[word] += 1
					else: 
						wordvector[word] =1
				keys_to_remove = [key for key, value in wordvector.iteritems() if key in punctuations]
				for key in keys_to_remove:
					del wordvector[key]
				self.termWordvector[term]=wordvector	

	## Add tokenized associated pubmed title and abstracts to term - word vector dictionary, term as key, word vector as value
	def termArticleWordvector(self):
		documents = self.createDocuments(self.input_filepath);
		nodes = self.goGraph.nodes()
		for acc in nodes:
			wordvectorList = []	
			wordvectorList.append(self.termWordvector[acc])
			# print self.termPubMed.get(acc)
			if self.termPubMed.get(acc) is not None:
				for pmid in self.termPubMed.get(acc):
					if pmid in documents:
						wordvectorList.append(documents[pmid]) 
					else:
						# print "do not find pubmed"
						continue
			res = Counter(wordvectorList[0])
			for i in range(1,len(wordvectorList)):
				c = Counter(wordvectorList[i])
				res = res+c
			self.termWordvector[acc]=dict(res)

	## Calculate kullback Leibler divergence of two given Goterms
	# @param term1
	# @param term2
	# @param smoother
	def calcWeightKL(self, term1, term2, smoother=0.001):
		"""
		Calculate kullback Leibler divergence of two given Goterms
	 	@param term1
	 	@param term2
		@param smoother
		"""
		if term1 in self.termWordvector:
			v1 = self.termWordvector[term1].copy()
		else:
			return 0
		if term2 in self.termWordvector:
			v2 = self.termWordvector[term2].copy()
		else:
			return 0

		total1 = 0.0
		total2 = 0.0
		for w in v1:
			if w not in v2:
				v2[w] = smoother
		for w in v2:
			if w not in v1:
				v1[w] = smoother
		for w in v1:
			total1 += v1[w]
		for w in v2:
			total2 += v2[w]
		distance = 0
		for w in v1:
			distance += v1[w]/total1 * math.log((v1[w]/total1)/(v2[w]/total2))
		return distance	

	## Add weights to the director GO term graph
	def updateWeights(self):
		"""
		Add weights to the directed GO term graph
		"""
		self.createGraph()
		self.createTermPubMed()
		self.termDefWordvector()
		self.termArticleWordvector()
		nodes = self.goGraph.nodes() 
		root = ET.Element("GOgraph")
		for i in range(len(nodes)):
			child = nodes[i]	
			predecessors = self.goGraph.predecessors(child)
			if predecessors is not None:
				termnode = ET.SubElement(root, "term", id = child)
				for j in range(len(predecessors)):			
					parent = predecessors[j] 
					parentNode = ET.SubElement(termnode, "parent", id = parent)
					ET.SubElement(parentNode, "relationship").text = "is_a"
					weight = self.calcWeightKL(child,parent)
					# print weight
					ET.SubElement(parentNode,"edge", type="KL").text = str(weight)
		tree = ET.ElementTree(root)	
		tree.write(self.output_filepath, pretty_print=True)

	def determine_path(self):
		try:
			root = __file__
			if os.path.islink (root):
				root = os.path.realpath (root)
			return os.path.dirname (os.path.abspath (root))
		except:
			print "I'm sorry, but something is wrong."
			print "There is no __file__ variable. Please contact the author."
			sys.exit ()
	

