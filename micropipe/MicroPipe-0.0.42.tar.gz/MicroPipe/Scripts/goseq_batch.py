#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<>
  Purpose: 
  Created: 2016/3/2
"""

from lpp import *
import os
usage = "python2.7 %prog [options]"
parser = OptionParser(usage =usage )
parser.add_option("-i", "--Input", action="store",
                  dest="data",

                  help=" Differential gene list by Deseq ")
parser.add_option("-l", "--Genelength", action="store",
                  dest="genelength",

                  help="All Gene Length")

parser.add_option("-g", "--Go", action="store",
                  dest="Go",

                  help="All Gene Go Annotation")
(options, args) = parser.parse_args()

data = options.data
length = options.genelength
go = options.Go

doc_list = glob.glob(data+"/*/")
for each_doc in doc_list:
    each_path = os.path.abspath(each_doc)+'/'
    os.system("""
    for i in %(path)s/*.end; do goseq.py  -i $i  -o ${i%.*}/${i%.*} -g %(go)s -l %(length)s  & done 
    
    """%(
           {
               "path":each_doc,
               "go":go,
               "length":length
           }
       )
       )