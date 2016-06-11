#!/usr/bin/python
# encoding:UTF-8

#######################################
# Here is the contents of version 1.1
# wiritten by mark
# inspired by Benjamin Gleitzman
#######################################
from __future__ import unicode_literals
from __init__ import __version__
import random
import glob
import os, sys
import re
import requests_cache
import requests
import sys, json
from bs4 import BeautifulSoup
import argparse
from requests.exceptions import ConnectionError
from requests.exceptions import SSLError
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters.terminal import TerminalFormatter
from pygments import highlight
from pygments.util import ClassNotFound
if sys.version>'3':
	from urllib.request import getproxies
	from urllib.parse import url_quote
else:
	from urllib import getproxies, quote as url_quote

if os.getenv('REHOWDOI_DISABLE_SSL'):
	SEARCH_URL = "http://www.google.com/search?q=site:{0}%20{1}"
	VERIFY_SSL_CERTIFICATE = False
else:
	SEARCH_URL = "https://www.google.com/search?q=site:{0}%20{1}"	
	VERIFY_SSL_CERTIFICATE = True 

URL = os.getenv('REHOWDOI_URL') or 'stackoverflow.com'
#DUCK_SEARCH_URL = 'http://duckduckgo.com/html?q=site%3Astackoverflow.com%20{0}'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17'

HEADER = {
	'Accept':'*/*',
	'User-Agent':USER_AGENT
}
ANSWERS_HEADER = '--- Answer {0} --- \n{1}'
NO_ANSWER_MSG = '< no answer given>'
XDG_CACHE_DIR = os.environ.get('XDG_CACHE_HOME',
				os.path.join(os.path.expanduser('~'), '.cache'))
CACHE_DIR = os.path.join(XDG_CACHE_DIR, 'rehowdoi')
CACHE_FILE = os.path.join(CACHE_DIR,
						'cache{0}'.format(sys.version_info[0] if sys.version_info[0]==3 else ''))
#PROXIES = {'http':'hppt://salmon.3.14159.in:24131'}
# get proxies, setting it through environment variable HTTP_PROXY	
def _get_proxies():
	proxies = getproxies()
	filtered_proxies = {}
	for key, val in proxies.items():
		if key.startswith('http'):
			if not val.startswith('http'):
				filtered_proxies[key] = 'http://%s' % val
			else:
				filtered_proxies[key] = val
	return filtered_proxies

def _get_result(url):
	print url
	try:
		result = requests.get(url, headers=HEADER,
								proxies=_get_proxies(),
								verify=VERIFY_SSL_CERTIFICATE)
		return result.text
	except requests.exceptions.SSLError as e:
		print '[ERROR] enconnected an SSL Error. Try using HTTP insteand of', \
				'HTTPS by setting the environment variable "REHOWDOI_DISABLE_SSL.\n"'
		raise e

def _get_links(query):
	search_page = _get_result(SEARCH_URL.format(URL, url_quote(query)))
	assert search_page, 'search_page gone'
	bs = BeautifulSoup(search_page, 'lxml')
	ans_links = bs.find_all('h3', {"class":"r"}) 
	return [ans_link.a['href'] for ans_link in ans_links] 
	
"""
def get_duck_links(query):
	url = DUCK_SEARCH_URL.format(url_quote(query))
	search_page = get_result(url)
	bs = BeautifulSoup(search_page, 'lxml')
	ans_links = bs.find_all('h2', {"class":"result_title"})
	return [ans_link.a['href'] for ans_link in ans_links]
"""

def _is_question_link(link):
	return re.search(r'/questions/\d+/', link)

def _get_question_links(links):
	return [link for link in links if _is_question_link(link)]

def get_link_at_pos(links, pos):
	#############################
	# not readability not concise closed in dark room
	#pos = pos -1
	#count, i=0, 0
	#while i<len(links):
	#	if is_question(links[i]):
	#		if count==pos:
	#			i+=1
	#			break
	#		else:
	#			count+=1
	#	i+=1
	#return links[i-1]
	##############################
	if not links:
		return False

	if len(links)>=pos:
		link = links[pos-1]
	else:
		link = links[-1]
	return link

def _format_output(code, args):
	if not args['color']:
		return code
	lexer = None
	for keyword in args['query'].split()+args['tag']:
		try:
			lexer = get_lexer_by_name(keyword)
			break
		except ClassNotFound:
			pass
	if not lexer:
		try:
			lexer = geuess_lexer(code)
		except ClassNotFound:
			return code

	return highlight(
		code,
		lexer,
		TerminalFormatter(bg='dark')
	)

def _get_answer(args, links):
	#link or result answer of stackoverflow 
	links = _get_question_links(links)
	link = get_link_at_pos(links, args['pos'])
	if not link:
		return False
	if args.get('link'):
		return link
	page = _get_result(link+'?answertab=votes')
	assert page, 'result_page gone'
	html = BeautifulSoup(page, 'lxml')
	first_answer = html.find('div', {'id':'answers'})
	instructions = first_answer.find('pre') or first_answer.find('code')
	args['tag'] = [tag.text for tag in html.find_all('a', {"class":"post-tag"})]
	if not args['all'] and not instructions:
		text = first_answer.find('div', {"class":"post-text"}).text
	elif args['all']:
		texts = []
		for html_tag in first_answer.find('div', {"class":"post-text"}).contents:
			current_text = None
			try:
				current_text = html_tag.text
			except AttributeError:
				pass
			if current_text:
				if html_tag.name in ['pre', 'code']:
					texts.append(_format_output(current_text, args))
				else:
					texts.append(current_text)
		texts.append('\n---\nAnswer from {0}'.format(link))
		text = '\n'.join(texts)
	else:
		text = _format_output(instructions.text, args)
	text = text.strip()
	if not text:
		text = NO_ANSWER_MSG
	return text
	
	"""
	if not args['all'] and instructions:
		text = instructions.text
	else:
		text = first_answer.find('div', {"class":"post-text"}).text
	return text
	"""

def _get_instructions(args):
	links = _get_links(args['query'])
	if not  links:
		#return ''
		return False
	answers = []
	append_header = args['num_answers']>1
	initial_position = args['pos']
	for answer_number in range(args['num_answers']):
		current_position = answer_number+initial_position
		args['pos'] = current_position
		answer = _get_answer(args, links)
		if not answer:
			break
		if append_header:
			answer = ANSWERS_HEADER.format(current_position, answer)
		answer += '\n'
		answers.append(answer)
	return '\n'.join(answers)


def rehowdoi(args):
	args['query'] = ' '.join(args['query']).replace('?', '')
	try:
		instructions = _get_instructions(args) or 'Sorry, couldnt find any help with that topic'
		return instructions
	except ConnectionError, SSLError:
		return 'Failed to establish network connections\n'

def get_parser():
	parser = argparse.ArgumentParser(description='code search tool for human beings Attention! its premium again:hh')
	parser.add_argument('query', type=str, nargs='*', help='the question to answer')
	parser.add_argument('-p', '--pos', type=int, help='select answser in specified position(default: 1)', default=1)
	parser.add_argument('-a', '--all', action='store_true', help='display the full text of the answer')
	parser.add_argument('-l', '--link', action='store_true', help='display only the answer link.')
	parser.add_argument('-n', '--num-answers', help='number of answers to return', default=1, type=int)
	parser.add_argument('-c', '--color', action='store_true', help='enable colorized output' )
	parser.add_argument('-C', '--clear_cache', action='store_true', help='clear the cache')
	parser.add_argument('-P', '--poxy', type=str, help='set poxy')
	parser.add_argument('-v', '--version', action='store_true', help='displays the current version of rehowdoi')
	return parser

def _enable_cache():
	if not os.path.exists(CACHE_DIR):
		os.makedirs(CACHE_DIR)
	requests_cache.install_cache(CACHE_FILE)

def _clear_cache():
	for f in glob.glob('{0}*'.format(CACHE_FILE)):
		os.remove(f)

def command_line_runner():
	parser = get_parser()
	args = vars(parser.parse_args())
	if args['poxy']:
		os.environ['HTTP_PROXY'] = args['poxy']

	if args['version']:
		print __version__
		return
	
	if args['clear_cache']:
		_clear_cache()
		print 'Cache cleared successfully'
		return

	if not args['query']:
		parser.print_help()
		return

	if not os.getenv('REHOWDOI_DISABLE_CACHE'):
		_enable_cache()

	# for Python 3.x
	if sys.version < '3':
		print rehowdoi(args).encode('UTF-8', 'ignore')
	else:
		print rehowdoi(args)


if __name__ == '__main__':
	command_line_runner()
