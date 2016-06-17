#!/bin/env python3

import sys
import os

module_path = os.path.abspath("../pysdcv")
if module_path not in sys.path:
	sys.path.insert(0, module_path)
import pysdcv

test_words = ('you',)


print ('Starting  tests packet...')
print('Created StarDict object...',end='')
d = pysdcv.Stardict(os.path.join('/','usr','share','stardict','dic'))
if d:
	print('Ok')
print('Prepare dictonaries...',end='')
d.prepare_dicts()
print(set(d.prepared_dicts()))
print(d)

print('Test translating all dictfile full output...')
for word in test_words:
	print('Translate word', word)
	w = d.find_word(word)
	try:
		for i in w:
			print(i)
			print(w[i])
		print('-'*80)
	except TypeError:
		print('Not found')

print('Test translating all dictfile full output... END')

print('Test translating first dictfile full output...')
for word in test_words:
	print('Translate word', word)
	w = d.find_word_by_dict(word,1)
	try:
		for i in w:
			print(i)
			print(w[i])
		print('-'*80)
	except TypeError:
		print('Not found')

print('Test translating first dictfile full output...END')

while 1:
	i = input('Enter number dictionary: ')
	try:
		w = d.find_word_by_dict(input('Enter your word (Press Ctrl+C to stop): '),int(i))
	except ValueError:
		print('Incorrect number')
	try:
		for i in w:
			print(i)
			print(w[i])
		print('-'*80)
	except TypeError:
		print('Not found')

