'''
Created on 31 Mar 2016

@author: steve
'''
from ref_seq import Ref_Seq
import time
# import align
from align_srna import Align_sRNA
import analysis_helper as ah
import numpy
import write_to_file as wtf
import post_process as pp
import plot_reads as pr


def ref_coverage(seq, seq_output, ref_file, nt, smoothWinSize, fileFig, 
                 fileName, min_read_size, max_read_size, min_read_no, 
                 onscreen, no_csv, ylim, pub):
    """
    Fill out
    """
    
    ref = Ref_Seq()
    ref.load_ref_file(ref_file)
    
    if len(ref)>1:
        print "\nMultiple reference sequences in file. Use multiDen instead.\n"
        return 
    ref_output = ah.single_file_output(ref_file)
    #this is a hack    
    for header in ref.headers():
        single_ref=ref[header]
    start = time.clock()
    single_alignment = Align_sRNA()
    single_alignment.align_reads_to_seq(seq, single_ref, nt)
    if no_csv:
        wtf.csv_output(single_alignment,
                                 nt,
                                 seq_output,
                                 ref_output)   
    if fileFig or onscreen:
        single_sorted_alignemts = single_alignment.aln_by_ref_pos()
        graph_processed = pp.fill_in_zeros(single_sorted_alignemts, 
            len(single_ref), nt)
        x_ref = graph_processed[0]
        y_fwd_smoothed = pp.smooth(numpy.array(graph_processed[1]), 
            smoothWinSize, window='blackman')
        y_rvs_smoothed = pp.smooth(numpy.array(graph_processed[2]), 
            smoothWinSize, window='blackman')
        print "\n{0} nt alignment time time = {1} seconds\n"\
            .format(nt, str((time.clock() - start)))
        
        if fileName == "auto":
            fileName = ah.ref_seq_nt_output(seq_output, ref_output, nt, "pdf")
                
        pr.den_plot(x_ref, y_fwd_smoothed, y_rvs_smoothed, nt, fileFig, 
            fileName, onscreen, ref_output, ylim, pub)

def coverage_21_22_24(seq, seq_output, ref_file, smoothWinSize, 
    fileFig, fileName, min_read_size, max_read_size, min_read_no,
    onscreen, no_csv,y_lim, pub):     
    """
    Fill out
    """
    ref = Ref_Seq()
    ref.load_ref_file(ref_file)
    if len(ref)>1:
        print "\nMultiple reference sequences in file. Use multiDen instead.\n"
        return 
    ref_output = ah.single_file_output(ref_file)
    #this is a hack
    for header in ref.headers():
        single_ref=ref[header]    
    combined_21_22_24(seq, seq_output, ref_output, single_ref, smoothWinSize, 
    fileFig, fileName, min_read_size, max_read_size, min_read_no,
    onscreen, no_csv,y_lim, pub)    
       
    
def combined_21_22_24(seq, seq_output, ref_output, single_ref, smoothWinSize, 
    fileFig, fileName, min_read_size, max_read_size, min_read_no,
    onscreen, no_csv,y_lim, pub):
    
    single_alignment_21 = Align_sRNA()
    single_alignment_21.align_reads_to_seq(seq, single_ref, 21)
    single_alignment_22 = Align_sRNA()    
    single_alignment_22.align_reads_to_seq(seq, single_ref, 22)
    single_alignment_24 = Align_sRNA()        
    single_alignment_24.align_reads_to_seq(seq, single_ref, 24)

    print '\n21nt sRNAs:'
    single_sorted_alignemts_21 = single_alignment_21.aln_by_ref_pos()
    print '\n22nt sRNAs:'
    single_sorted_alignemts_22 = single_alignment_22.aln_by_ref_pos()
    print '\n24nt sRNAs:'
    single_sorted_alignemts_24 = single_alignment_24.aln_by_ref_pos()
    if no_csv:
        wtf.mnt_csv_output(single_alignment_21, single_alignment_22,
                                 single_alignment_24,
                                 seq_output,
                                 ref_output) 
    if fileFig or onscreen:
    
        graph_processed_21 = pp.fill_in_zeros(single_sorted_alignemts_21, 
            len(single_ref),21)
        graph_processed_22 = pp.fill_in_zeros(single_sorted_alignemts_22, 
            len(single_ref),22)
        graph_processed_24 = pp.fill_in_zeros(single_sorted_alignemts_24, 
            len(single_ref),24)
    
        x_ref = graph_processed_21[0]
        y_fwd_smoothed_21 = pp.smooth(numpy.array(graph_processed_21[1]), 
            smoothWinSize, window='blackman')
        y_rvs_smoothed_21 = pp.smooth(numpy.array(graph_processed_21[2]), 
            smoothWinSize, window='blackman')
        y_fwd_smoothed_22 = pp.smooth(numpy.array(graph_processed_22[1]), 
            smoothWinSize, window='blackman')
        y_rvs_smoothed_22 = pp.smooth(numpy.array(graph_processed_22[2]), 
            smoothWinSize, window='blackman')
        y_fwd_smoothed_24 = pp.smooth(numpy.array(graph_processed_24[1]), 
            smoothWinSize, window='blackman')
        y_rvs_smoothed_24 = pp.smooth(numpy.array(graph_processed_24[2]), 
            smoothWinSize, window='blackman')
    
        if fileName == "auto":
            fileName = ah.ref_seq_output(seq_output, ref_output, "pdf")
    
        pr.den_multi_plot_3(x_ref, y_fwd_smoothed_21, y_rvs_smoothed_21,
        y_fwd_smoothed_22, y_rvs_smoothed_22, y_fwd_smoothed_24, 
        y_rvs_smoothed_24, fileFig, fileName, onscreen, ref_output, y_lim, pub)


    