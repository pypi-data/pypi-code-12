import sys

for line in sys.stdin:
	sentence = line.split('\t')[1]
	print sentence
