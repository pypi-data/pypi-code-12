#!/usr/bin/env python

from KafNafParserMod import *

obj = KafNafParser('examples/entity_example.naf')

header = obj.get_header()

my_file_desc = header.get_fileDesc()
if my_file_desc is None:
    #Create a new one
    my_file_desc =  CfileDesc()
    header.set_fileDesc(my_file_desc)
    
#Modify the attributes
my_file_desc.set_title('my new title')

#Dump the object to a new file (or the changes will not be changed)
obj.dump()





