'''
Created on 1 Apr 2016

@author: steve
'''
"""
A class for reference sequences  - stores header:seq pairs in a dictionary

{header:seq}
"""
import time
from dna import DNA

class Ref_Seq(object):
    def __init__(self):
        self._internal_dict = {}
    
    def __setitem__(self, header, sequence):
        self._internal_dict[header]=sequence
    
    def __getitem__(self, header):
        return self._internal_dict[header]
    
    def __iter__(self):
        return self._internal_dict.iteritems()
    
    def __len__(self):
        return len(self._internal_dict)

    def headers(self):
        return self._internal_dict.keys()

    def sequences(self):
        return self._internal_dict.values()    
    

    def load_ref_file(self, ref_file):
        """
        Load ref file in fasta format
    
        Product ref_dict --> header:sequence
        """
        start = time.clock()
        #ref_dict = {}
        ref_count = 0
        loaded_ref = open(ref_file, 'rU')
        full_len_seq = ''
        key = ''
        first_header = True
        for line in loaded_ref:
            if line[0] == '>' and full_len_seq == '':
                key = line.strip()
                ref_count += 1
                if first_header:
                    first_header = False
            elif line[0] == '>' and full_len_seq != '':
                self._internal_dict.update({key: DNA(full_len_seq)})
                key = line.strip()
                full_len_seq = ''
                ref_count += 1
            elif line[0] == '' and full_len_seq != '':
                self._internal_dict.update({key: DNA(full_len_seq)})
                key = line.strip()
                full_len_seq = ''
            elif line[0] == '':
                pass
            else:
                full_len_seq += line.strip().upper()
    
        self._internal_dict.update({key: DNA(full_len_seq)})
    
        print '\n ---- {0} reference sequences loaded for alignment ----'\
            .format(ref_count)
        if len(self._internal_dict) ==1:
            print "\n{0} length = {1} bp".format(ref_file.split('/')[-1],
                                             len(full_len_seq))
        print "\nReference sequence loading time = "\
         + str((time.clock() - start)) + " seconds\n"
        print "-"*50