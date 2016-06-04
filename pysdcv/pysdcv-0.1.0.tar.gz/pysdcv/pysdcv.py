#!/bin/env python3

import os.path
from gzip import GzipFile
from platform import architecture
from io import StringIO
from glob import glob
from struct import unpack, calcsize
from pysdcv._xdxf import XdxfParser


def _parse_without_sametypesequence(t):
	""" in process """
	pass

def _parse_with_x_type(t,tostring=True):
	
	"""xdxf parser"""
	
	parser = XdxfParser()
	parser.parse(t)
	if tostring:
		return(parser.tostring())
	else:
		return(parser.tostringlists())


class Stardict(object):
	""" Class Stardict represent set of Stardict Dictionaries """


	class DictFile(object):
		""" Class DictFile  implemented  a  set of dictfile .ifo, .idx, dict.dz)  """
		
		def __init__(self, filename):
			self.ifo_filename = filename
			self.__prepared__ = False
			try:
				for line in open(self.ifo_filename):
					p,v = self._parse_ifo(line)
					if p:
						setattr(self,p,v)
				try:
					if self.idxoffsetbits  == 64:
						self.offsetfmt = 'sQI'
					elif self.idxoffsetbits  == 32:
						self.offsetfmt = 'sII'
				except AttributeError:
					self.offsetfmt = 'sII'
			except (OSError, IOError) as ioerr:
				print (ioerr)
			else:
				dict_dir = os.path.split(self.ifo_filename)[0]
				self.idx_filename = os.path.join(dict_dir, self.bookname+'.idx')
				if os.path.isfile(os.path.join(dict_dir, self.bookname + '.dict')):
					self.dict_filename = os.path.join(dict_dir, self.bookname + '.dict')
				elif os.path.isfile(os.path.join(dict_dir, self.bookname + '.dict.dz')):
					self.dict_filename = os.path.join(dict_dir, self.bookname + '.dict.dz')
				else:
					raise OSError('FileNotFound','Error reading file' + os.path.join(dict_dir, self.bookname +'.dict or .dict.dz' ))


		def compatability(self):
			if self.offsetfmt == 'sQI' and architecture()[0] == '32bit':
				return False
			else:
				return True

		
		def __repr__(self):
			return 'DictFile(bookname: {}, version: {}, wordcount: {}, idxfilesize: {})'.format(
							 self.bookname, self.version, self.wordcount,self.idxfilesize
							) 
		
		def prepare(self):
			""" Read index files  prepare  dict.dz files"""
			
			if self.compatability():
				with open(self.idx_filename, mode = 'rb') as idx_handler:
					self._parse_idx(idx_handler.read())
				if self.dict_filename.endswith('.dict'):
					self.dict_data = open(self.dict_filename, mode = 'rb')
				else:
					self.dict_data = GzipFile(self.dict_filename)
				self.__prepared__ = True
			return self.__prepared__


		def _parse_ifo(self,line):
			try:
				parameter,value =line.split('=')
			except ValueError:
				return (None,None)
			else:
				return (parameter.strip(), value.strip())

		def _parse_idx(self,idx):
			brake = chr(0x00).encode('utf8')
			oldindex = 0 
			self.idx={}
			try:
				while True:
					index =idx.index(brake, oldindex)
					fmt = '!' + str(index - oldindex + 1) + self.offsetfmt
					word_struct = unpack(fmt,idx[oldindex:index + 9])
					oldindex = oldindex + calcsize(fmt)
					self.idx[word_struct[0].decode('utf8')[:-1]] = (word_struct[1],word_struct[2])
			except ValueError:
				pass

		def find_word(self,word,tostring=True):
			""" Search word  """
			try:
				offset = self.idx[word][0]
				size = self.idx[word][1]
			except KeyError:
				return None
			else:
				self.dict_data.seek(offset)
				return self._parse_translated(self.dict_data.read(size).decode('utf8'),tostring)
					

		def _parse_translated(self,translated,tostring=True):
			"""parse data from  dictionary """
			try:
				if self.sametypesequence == 'x':
					return _parse_with_x_type(translated,tostring)
				else:
					return None
			except AttributeError:
				return _parse_without_sametypesequence(translated)


		
	def __init__(self,dict_dir):
		self.dict_dir = dict_dir
		self._dictfiles = []
		dictfiles = [ i for i in glob(os.path.join(self.dict_dir,'*.ifo'))]
		for d in dictfiles:
			dictfile = Stardict.DictFile(d)
			self._dictfiles.append(dictfile)

	def __repr__(self):
		dictionaries = '\n'.join(map(repr,self._dictfiles))
		return 'Stardict(Dict Directory: {}\n{}\n)'.format(self.dict_dir, dictionaries)

	def prepare_dicts(self):
		"""Prepare all dictfiles """
		
		for one_dict in self._dictfiles:
			one_dict.prepare()
	
	def prepared_dicts(self):
		""" Return  set with  Dictfiles status """
		return (one_dict.__prepared__ for one_dict in  self._dictfiles)
	

	def find_word_by_dict(self,word,index=0,tostring=True):
		"""Search a word in  a particulary Dictfile """
		
		try:
			trans = self._dictfiles[index].find_word(word)
		except IndexError:
			print('There isn\'t ' + str(index) + '-th  dictonary')
			return None
		else:
			return trans

	def find_word(self,word,tostring=True):
		"""Search a word in every Dictfile """
		
		result = {}
		for one_dict in self._dictfiles:
			trans =  one_dict.find_word(word,tostring)
			if trans:
				result[one_dict.bookname] = trans
		return result

