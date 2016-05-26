'''
Created on 7 Apr 2016

@author: steve
'''
class DNA(object):
    dna_alphabet = set("AGCTN")
    def __init__(self, sequence):
        self.sequence = sequence.upper()
    def __len__(self):
        return len(self.sequence)
    def __getitem__(self, key):
        return self.sequence[key]
    
    def __hash__(self):
        return hash((self.sequence))

    def __eq__(self, other):
        return self.sequence == other.sequence
    def complement(self):
        """Provides the complement in the 5' - 3' direction

        Assumption: reference consists of A, G, C, T only

        complement(str) --> str
        """
        d = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return (''.join(d[c] if c in d else c for c in reversed(self.sequence))) 
    def is_dna(self):
        """
        True if all nucleotides are from dna_alphabet
        """
        not_dna = set(self) - DNA.dna_alphabet
        return not not_dna