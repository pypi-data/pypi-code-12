'''
Created on 18 Feb 2016

@author: alastair.mccormack
'''
import pymp4parse

filename = '/Users/alastair.mccormack/nbcu-debug/160221_2989249_Spinning_a_Web_4000_1-encrypted_track1_dashinit_bdd3e7a2df4d485e9aa7801e068ce742_.mp4-par2'

boxes = pymp4parse.F4VParser.parse(filename=filename)

for box in boxes:
    for b in boxes:
        print b

