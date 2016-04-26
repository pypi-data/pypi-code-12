#!/usr/bin/env python

from KafNafParserPy import KafNafParser

f= '/home/izquierdo/data/opinion_annotations_nl/kaf/hotel.newdeps/dutch00001_046973f3141ba52fb0114ad1c6e4852a.kaf'
#f='/home/izquierdo/data/opinion_annotations_en/kaf/hotel/english00001_0123ff23e0d0dc0177f9b71a1928b674.kaf'
f = '/home/izquierdo/data/opinion_annotations_nl/kaf/hotel.newdeps/dutch00179_275f8af4f400ecfeb297c26129e2016e.kaf'
o = KafNafParser(f)
d = o.get_dependency_extractor()




s1  = ['t65','t66']
#s1 = ['t37','t38']
s1 = ['t44']

s2 = ['t6','t7','t8']
s2 = ['t73']
s2 = ['t45']
#s2 = ['t40','t41']

print 'Short span',d.get_shortest_path_spans(s1,s2)
