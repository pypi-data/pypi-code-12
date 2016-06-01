#!/usr/bin/python
# encoding:UTF-8

#######################################
# Here is the contents of version 1.1
# wiritten by mark
# inspired by Benjamin Gleitzman
#######################################
import re
import requests
import urllib
import sys, json
from bs4 import BeautifulSoup
import argparse

GOOGLE_SEARCH_URL = "https://www.google.com/search?q=site:stackoverflow.com%20{0}"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"
HEADER = {
	'Accept':'*/*',
	'User-agent':USER_AGENT
}
def get_result(url):
	print url
	result = requests.get(url, headers=HEADER)
	return result.text

def get_google_links(query):
	url = GOOGLE_SEARCH_URL.format(urllib.quote(query))
	search_page = get_result(url)
	bs = BeautifulSoup(search_page, 'lxml')
	ans_links = bs.find_all('h3', {"class":"r"})
	return [ans_link.a['href'] for ans_link in ans_links]

def get_link_at_pos(links, pos):
	def is_question(link):
		return re.search(r'/questions/\d+/', link)
	pos = pos-1
	curr_link = links[0]
	count, i=0, 0
	while True:
		if is_question(links[i]):
			if count==pos:
				break
			else:
				count+=1
		i+=1
	return links[i]
	
def get_instructions(args):
	#return links list
	links = get_google_links(args['query'])
	if not links:
		return ''
	link = get_link_at_pos(links, args['pos'])
	if args.get('link'):
		return '>'+link
	link = link+ '?answertab=votes'
	page = get_result(link)
	html = BeautifulSoup(page, 'lxml')
	first_answer = html.find('div', {'id':'answers'})
	instructions = first_answer.find('pre') or first_answer.find('code')
	if args['all']==None or instructions:
		text = instructions.text
	else:
		text = first_answer.find('div', {"class":"post-text"}).text
	if not text:
		return ''
	text = '>' + text
	text = text.replace('\n', '\n>> ')
	return text
	"""
		try:
			link = response['items'][0]['link']
			page = get_result(link)
			bs = BeautifulSoup(page, 'lxml')
			first_ans = bs.find('div', {'id':'answers'})
			instructions = first_ans.find('code') or first_ans.find('pre')
			return instructions.text
		except:
			return ''
	"""
def howdoi(args):
	args['query'] = ' '.join(args['query']).replace('?', '')
	instructions = get_instructions(args) or 'Sorry, couldnt find any help with that topic'
	print instructions

def command_line_runner():
	parser = argparse.ArgumentParser(description='code search tool for human beings')
	parser.add_argument('query', type=str, nargs=argparse.REMAINDER, help='the question to answer')
	parser.add_argument('-p', '--pos', type=int, help='select answser in specified position(default: 1)', default=1)
	parser.add_argument('-a', '--all', action='store_true', help='display the full text of the answer')
	parser.add_argument('-l', '--link', action='store_true', help='display only the answer link.')
	args = vars(parser.parse_args())
	howdoi(args)

if __name__ == '__main__':
	command_line_runner()
