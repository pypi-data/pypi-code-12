from  io import StringIO 
from xml.etree import ElementTree as eltree
from collections import defaultdict


xdxf_header ='<?xml version="1.0" encoding="UTF-8" ?><!DOCTYPE xdxf SYSTEM "http://xdxf.sourceforge.net/xdxf_lousy.dtd"><xdxf lang_from="ENG" lang_to="ENG" format="visual">'

sup_codes = {
	'1' : u"\u00B9",
	'2' : u"\u00B2",
	'3' : u"\u00B3",
	'4' : u"\u2074",
	'5' : u"\u2075",
	'6' : u"\u2076",
	'7' : u"\u2077",
	'8' : u"\u2078",
	'9' : u"\u2079",
	'0' : u"\u2070"
}

sub_codes = {
        '1' : u"\u2081",
        '2' : u"\u2082",
        '3' : u"\u2083",
        '4' : u"\u2084",
	'5' : u"\u2085",
        '6' : u"\u2086",
        '7' : u"\u2087",
        '8' : u"\u2088",
        '9' : u"\u2089",
        '0' : u"\u2080"
}


def get_scripted_char(ch):
	try:
		return cur_codes[ch]
	except KeyError:
		return u"\u207B"
	except NameError as e:
		raise e('unkonown codes list')

def get_scripted_string(st,codes):
	global cur_codes
	cur_codes = codes
	return ''.join(map(get_scripted_char,st))


class Storage(object):

	def __init__(self):
		self.meta_data = defaultdict(list)
		self.articles = defaultdict(list)

	def __repr__(self):
		return ','.join(map(repr,self.meta_data)) + '\n' + '\n'.join(map(repr,self.articles)) 

	def add_metadata(self,key,value=None):
		self.meta_data[key] = value

	def add_articles_key(self,key):
		self.articles[key] = [key]

	def add_articles_body(self,key,value,last=False):
		if last:
			self.articles[key][len(self.articles[key]) - 1] +=  value
		else:
			self.articles[key].append(value)

class XdxfParser(object):

	def __init__(self, storage=None):
		if storage:
			self.storage = storage
		else:

			self.storage = Storage()

	def _createabbrs(self,element):
		abbrs = {}
		for abrdef in element:
			if abrdef.tag.lower() == 'abr_def':
				value = abrdef.find('v')
				if value:
					value_txt = value.text
					for key in abrdef.findall('k'):
						abbrs[key.text] = value_txt
		return abbrs

	def _handler_tag(self,element,parent):
		handler = getattr(self,'_handler_tag_' + element.tag, self._handler_tag_default)
		handler(element,parent)

	def _handler_tag_default(self,element,parent):
		pass

	def _handler_tag_k(self,element,parent):
		self._current_key = element
		self.storage.add_articles_key(element.text)
	
	def _handler_tag_dtrn(self,element,parent):
		for child in element:
			self._handler_tag(child,None)

	def _handler_tag_blockquote(self,element, parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, element.text)
		for child in element:
			self._handler_tag(child,element)
	
	def _handler_tag_co(self,element, parent):
		if element.text:
			 self.storage.add_articles_body(self._current_key.text, element.text)
		for child in element:
			self._handler_tag(child,element)
	
	def _handler_tag_abr(self,element, parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, '(' + element.text + ') ',True)
		for child in element:
			self._handler_tag(child,element)
	
	def _handler_tag_i(self,element, parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, ' ' + element.text, True)
		for child in element:
			self._handler_tag(child,element)

	def _handler_tag_c(self,element, parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, ' ' + element.text, True)
		for child in element:
			self._handler_tag(child,element)
	
	def _handler_tag_b(self,element, parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, ' ' + element.text, True)
		for child in element:
			self._handler_tag(child,element)
			
	def _handler_tag_sub(self,element,parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, get_scripted_string(element.text, sub_codes), True)

	def _handler_tag_sup(self,element,parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, get_scripted_string(element.text, sup_codes), True)

	def _handler_tag_kref(self,element, parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, '[' + element.text + '] ',True)
		for child in element:
			self._handler_tag(child,element)

	def _handler_tag_ex(self,element, parent):
		if element.text:
			self.storage.add_articles_body(self._current_key.text, ' ' + element.text,True)
		for child in element:
			self._handler_tag(child,element)
	
	def _handler_tag_xdxf(self,element,parent):
		for child in element:
			self._handler_tag(child,element) 

	def parse(self,xdxf_string):
		abbreviations = {}
		if xdxf_string.find(xdxf_header) == -1:
			xdxf_string = xdxf_header + xdxf_string +'</xdxf>'
		for _, el in eltree.iterparse(StringIO(xdxf_string)):
			if el.tag == 'description' or el.tag == 'title' or el.tag == 'full_title' or el.tag == 'publisher' or el.tag == 'description':
				self.storage.add_metadata(el.tag, el.text)
				el.clear()
			elif el.tag == 'xdxf':
				self.storage.add_metadata('article_language', el.get('lang_to'))
				self.storage.add_metadata('index_language', el.get('lang_from'))
				self.storage.add_metadata('xdxf_format', el.get('format'))
				self._handler_tag_xdxf(el,None)

	def tostringlists(self):
		return self.storage.articles

	def tostring(self):
		res = {}
		for key in self.storage.articles:
			st = ''
			for i in self.storage.articles[key]:
				st += i
			res[key] = st
		return res

			
