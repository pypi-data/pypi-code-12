# -*- coding: utf-8 -*-
from sys import stdout



def statusBar(step, total, bar_len=20, onlyReturn=False):
	'''
	print a ASCI-art statusbar of variable length e.g.showing 25%:
	
	>>> step = 25
	>>> total = 100
	
	>>> print statusBar(step, total, bar_len=20, onlyReturn=True)
	\r[=====o---------------]25%

	as default onlyReturn is set to False
	in this case the last printed line would be flushed every time when
	the statusbar is called to create a the effect of one moving bar
	'''

	norm=100.0/total
	step *= norm
	step = int(step)
	increment = 100/bar_len
	n = (step / increment)
	m = bar_len - n
	text = "\r[" + "="*n +"o" +  "-"*m + "]" +  str(step) + "%"
	if onlyReturn:
		return text
	stdout.write(text)
	stdout.flush()



if __name__ == "__main__":
	import doctest
	doctest.testmod()