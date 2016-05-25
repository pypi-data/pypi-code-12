'''
Created on 30 Mar 2016

@author: steve
'''

"""
Helper functions for the analysis Module
"""

def single_file_output(in_file):
    """
    Parse in_file path to produce a name 
    for the output file
    
    In: path/to/in_file.fa
    Out: in_file
    """
    return in_file.split('/')[-1].split('.')[-2]

def rep_file_output(in_file_1, in_file_2):
    """
    Parse replicate in_file paths to produce a name 
    for the output file
    
    In: path/to/in_file_1.fa path/to/in_file_2.fa
    Out: in_file_1_in_file_2
    """
    return "{0}_{1}".format(single_file_output(in_file_1),
                            single_file_output(in_file_2))
    
def ref_seq_nt_output(in_seq_name, in_ref_name, nt, ext):
    """
    Generates a compound file name from a single_file_output, 
    rep_file_output, and nt with the correct enxtension
    
    Out: in_ref_name_in_seq_name_nt.ext
    """
    return "{0}_{1}_{2}.{3}".format(in_ref_name,
                                    in_seq_name,
                                    str(nt),
                                    ext)
def ref_seq_output(in_seq_name, in_ref_name, ext):
    """
    Generates a compound file name from a single_file_output, 
    rep_file_output, and nt with the correct enxtension
    
    Out: in_ref_name_in_seq_name_nt.ext
    """
    return "{0}_{1}.{2}".format(in_ref_name,
                                    in_seq_name,
                                    ext)
def header_output(header):
    """
    Fill in
    """
    
    return header[1:]

def cdp_file_output(in_seq_name1, in_seq_name2, ref, nt, ext):
    """
    Fill in
    """
    return "{0}_{1}_{2}_{3}.{4}".format(in_seq_name1,
                                    in_seq_name2,
                                    ref,
                                    nt,
                                    ext)