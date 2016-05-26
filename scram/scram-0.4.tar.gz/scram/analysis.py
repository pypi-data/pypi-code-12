'''
Created on 22 Jan 2016

@author: steve
'''
"""
Analysis module
"""
from ref_seq import Ref_Seq
from srna_seq import SRNA_Seq
import srna_seq
import write_to_file
import cdp
import analysis_helper as ah
import den as dn

#TODO: make single function for same bits of multiden and multidenAv etc.

def single_ref_coverage(seq_file, ref_file, nt, smoothWinSize=50, 
    fileFig = False, fileName = 'plot.pdf', min_read_size = 18, 
    max_read_size = 32, min_read_no=1, onscreen = False, no_csv = False, 
    ylim=0, pub=False):
    """
    Aligns reads from a single read file to a single reference sequence for
    a single sRNA size.
    """

    seq=SRNA_Seq()
    seq.load_seq_file(seq_file, 
        max_read_size, min_read_no, min_read_size)
    
    single_seq_output = ah.single_file_output(seq_file)
    
    dn.ref_coverage(seq, single_seq_output, ref_file, nt, smoothWinSize, fileFig, 
                 fileName, min_read_size, max_read_size, min_read_no, 
                 onscreen, no_csv, ylim, pub)
    

def single_ref_coverage_av(seq_file_1, seq_file_2, ref_file, nt, 
    smoothWinSize=50, fileFig=False, fileName = 'plot.pdf', 
    min_read_size = 18, max_read_size = 32, min_read_no=1, 
    onscreen = False, no_csv=False, ylim=0, pub=False):
    """
    Aligns average no. of reads from a pair of read files 
    to a single reference sequence for a single sRNA size.
    """


    seq=SRNA_Seq()
    seq.load_av_seq_files(seq_file_1, seq_file_2, 
        max_read_size, min_read_no, min_read_size)

    rep_seq_output = ah.rep_file_output(seq_file_1, seq_file_2)
    
    dn.ref_coverage(seq, rep_seq_output, ref_file, nt, smoothWinSize, fileFig, 
                 fileName, min_read_size, max_read_size, min_read_no, 
                 onscreen, no_csv, ylim, pub)   
    

def single_ref_coverage_21_22_24(seq_file, ref_file, smoothWinSize=50, 
    fileFig = True, fileName = 'plot.pdf', min_read_size = 18, 
    max_read_size = 32, min_read_no=1, onscreen = True, no_csv=False,
    y_lim=0, pub=False):
    """
    Align reads from a single seq file to a single reference for 21,22 and 24nt
    """

    seq=SRNA_Seq()
    seq.load_seq_file(seq_file, max_read_size, min_read_no, 
        min_read_size)
    single_seq_output = ah.single_file_output(seq_file)
    
    dn.coverage_21_22_24(seq, single_seq_output, ref_file, smoothWinSize, 
    fileFig, fileName, min_read_size, max_read_size, min_read_no,
    onscreen, no_csv,y_lim, pub)



def single_ref_coverage_21_22_24_av(seq_file_1, seq_file_2, ref_file, 
    smoothWinSize=50, fileFig = True, fileName = 'plot.pdf', min_read_size = 18, 
    max_read_size = 32, min_read_no=1, onscreen = True, no_csv=False,
    y_lim=0, pub=False):
    """
    Align reads from a single seq file to a single reference for 21,22 and 24nt
    """

    seq=SRNA_Seq()
    seq.load_av_seq_files(seq_file_1, seq_file_2, 
        max_read_size, min_read_no, min_read_size) 

    rep_seq_output = ah.rep_file_output(seq_file_1, seq_file_2)
    
    dn.coverage_21_22_24(seq, rep_seq_output, ref_file, smoothWinSize, 
    fileFig, fileName, min_read_size, max_read_size, min_read_no,
    onscreen, no_csv,y_lim, pub)    


def multi_seq_and_ref_21_22_24(seq_list, ref_file, smoothWinSize=50, 
    fileFig = True, fileName = 'auto', min_read_size = 18, 
    max_read_size = 32, min_read_no=1, onscreen = False, no_csv = False, 
    y_lim = 0, pub=False):
    """
    Complete for mutliple seq and ref files 
    See single_ref_coerage_21_22_24 for default values
    pairwise alignments for all seqs and refs will take place
    """

    refs = Ref_Seq()
    refs.load_ref_file(ref_file)

    seqs = srna_seq.load_seq_list(seq_list) 
    
    for single_seq in seqs:

        seq=SRNA_Seq()
        seq.load_seq_file(single_seq, max_read_size, min_read_no, 
            min_read_size) 
        single_seq_output = ah.single_file_output(single_seq)
        for header, single_ref in refs:
            ref_output = ah.header_output(header)
            dn.combined_21_22_24(seq, single_seq_output, ref_output, single_ref, 
                                 smoothWinSize, fileFig, fileName, 
                                 min_read_size, max_read_size, min_read_no,
                                 onscreen, no_csv,y_lim, pub)


def av_multi_seq_and_ref_21_22_24(seq_list, ref_file, smoothWinSize=50, 
    fileFig = True, fileName = 'plot.pdf', min_read_size = 18, 
    max_read_size = 32, min_read_no=1, onscreen = False, no_csv = False, 
    y_lim = 0, pub=False):
    """
    Complete for mutliple seq in replicate and ref files 
    See single_ref_coerage_21_22_24 for default values
    pairwise alignments for all seqs and refs will take place
    """
    
    refs = Ref_Seq()
    refs.load_ref_file(ref_file)

    seqs = srna_seq.load_av_seq_list(seq_list)
    
    for single_seq in seqs:

        seq=SRNA_Seq()
        seq.load_av_seq_files(single_seq[0], single_seq[1], 
            max_read_size, min_read_no, min_read_size) 
        rep_seq_output = ah.rep_file_output(single_seq[0], single_seq[1])
        
        for header, single_ref in refs:
            ref_output = ah.header_output(header)
            dn.combined_21_22_24(seq, rep_seq_output, ref_output, single_ref, 
                                 smoothWinSize, fileFig, fileName, 
                                 min_read_size, max_read_size, min_read_no,
                                 onscreen, no_csv,y_lim, pub)


def CDP(seq_file_1, seq_file_2, ref_file, nt, 
    fileFig=False, fileName = 'plot.pdf', 
    min_read_size = 18, max_read_size = 32, min_read_no=1, onscreen = False,
    pub=False):
    """
    Plots alignment count for each sRNA in ref file as (x,y)
    for 2 seq files.  No splitting of read count
    """  

    seq_1=SRNA_Seq()
    seq_1.load_seq_file(seq_file_1, max_read_size, min_read_no, 
        min_read_size)

    seq_2=SRNA_Seq()
    seq_2.load_seq_file(seq_file_2, max_read_size, min_read_no, 
        min_read_size)    
    
    seq_name_1 = ah.single_file_output(seq_file_1)
    seq_name_2 = ah.single_file_output(seq_file_2)
    
    cdp.CDP_shared(seq_1, seq_2, seq_name_1, seq_name_2, ref_file, nt,fileFig, 
               fileName, min_read_size, max_read_size, min_read_no, onscreen,
               pub)



def avCDP(seq_file_1, seq_file_2, seq_file_3, seq_file_4, ref_file, nt, 
    fileFig=False, fileName = 'plot.pdf', 
    min_read_size = 18, max_read_size = 32, min_read_no=1, onscreen = False, 
    pub=False):
    """
    Plots alignment count for each sRNA in ref file as (x,y)
    for 2 sets of replicate seq files.  No splitting of read count
    """      
    seq_1=SRNA_Seq()
    seq_1.load_seq_file(seq_file_1, seq_file_2, max_read_size, min_read_no, 
        min_read_size)

    seq_2=SRNA_Seq()
    seq_2.load_seq_file(seq_file_3, seq_file_4, max_read_size, min_read_no, 
        min_read_size)     
    
    seq_name_1 = ah.rep_file_output(seq_file_1, seq_file_2)
    seq_name_2 = ah.rep_file_output(seq_file_3, seq_file_4)    
    
    cdp.CDP_shared(seq_1, seq_2, seq_name_1, seq_name_2, ref_file, nt,fileFig, 
               fileName, min_read_size, max_read_size, min_read_no, onscreen,
               pub) 


def CDP_split(seq_file_1, seq_file_2, ref_file, nt, 
    fileFig=False, fileName = 'plot.pdf', 
    min_read_size = 18, max_read_size = 32, min_read_no=1, onscreen = False,
    pub=False):

    """
    Plots alignment count for each sRNA in ref file as (x,y)
    for 2 seq files.  Read count split by number of times an sRNA aligns
      
    """  

    seq_1=SRNA_Seq()
    seq_1.load_seq_file(seq_file_1, max_read_size, min_read_no, 
        min_read_size)

    seq_2=SRNA_Seq()
    seq_2.load_seq_file(seq_file_2, max_read_size, min_read_no, 
        min_read_size)   
    
    seq_name_1 = ah.single_file_output(seq_file_1)
    seq_name_2 = ah.single_file_output(seq_file_2)
    
    cdp.CDP_split_shared(seq_1, seq_2, seq_name_1, seq_name_2, ref_file, 
                     nt, fileFig, fileName,min_read_size, max_read_size, 
                     min_read_no, onscreen, pub)


def avCDP_split(seq_file_1, seq_file_2, seq_file_3, seq_file_4, ref_file, nt, 
    fileFig=False, fileName = 'plot.pdf', 
    min_read_size = 18, max_read_size = 32, min_read_no=1, onscreen = False, 
    pub=False):
 

    seq_1=SRNA_Seq()
    seq_1.load_seq_file(seq_file_1, seq_file_2, max_read_size, min_read_no, 
        min_read_size)

    seq_2=SRNA_Seq()
    seq_2.load_seq_file(seq_file_3, seq_file_4, max_read_size, min_read_no, 
        min_read_size)     
 
    seq_name_1 = ah.rep_file_output(seq_file_1, seq_file_2)
    seq_name_2 = ah.rep_file_output(seq_file_3, seq_file_4) 

    cdp.CDP_split_shared(seq_1, seq_2, seq_name_1, seq_name_2, ref_file, 
                     nt, fileFig, fileName,min_read_size, max_read_size, 
                     min_read_no, onscreen, pub)    
    

def CDP_single_split(seq_file_1, ref_file, nt, 
    min_read_size = 18, max_read_size = 32, min_read_no=1):
    """
    Normalised split alignments for a single reference - all recorded
    including 0
    
    
    TODO: may be incorrect - check with unit tests!!!!!!
    """

    refs = Ref_Seq()
    refs.load_ref_file(ref_file)
    seq_1=SRNA_Seq()
    seq_1.load_seq_file(seq_file_1, 
        max_read_size, min_read_no, min_read_size)
    
    seq_name_1 = ah.single_file_output(seq_file_1)

    alignment_dict_1={} #header:aligned_sRNAs


    sRNA_align_count_1={} #sRNA:no_of_times_aligned


    header_split_count_1={} #header:count


    counts_by_ref = {} #header (align_count_1, align_count_2)

    #calc aligned sRNAs for each header, duplicate if necessary
    for header, single_ref in refs:

        alignment_dict_1[header] = \
        cdp.list_align_reads_to_seq_split(seq_1, single_ref, nt)
        
    
    #calc no of times each sRNA is aligned - 1    
    for header, sRNA_list in alignment_dict_1.iteritems():
        for sRNA in sRNA_list:
            if sRNA in sRNA_align_count_1:
                sRNA_align_count_1[sRNA] +=1
            else:
                sRNA_align_count_1[sRNA] = 1


    #calc split alignment count for each header - 1
    for header, sRNA_list in alignment_dict_1.iteritems():
        header_split_count_1[header] = 0
        for sRNA in sRNA_list:
            header_split_count_1[header] +=seq_1[sRNA]/sRNA_align_count_1[sRNA]

    #construct x,y counts for each header
    for header in refs.headers():

        counts_by_ref[header] = header_split_count_1[header]


    write_to_file.cdp_single_output(counts_by_ref, 
                                    seq_name_1, 
                                    nt)