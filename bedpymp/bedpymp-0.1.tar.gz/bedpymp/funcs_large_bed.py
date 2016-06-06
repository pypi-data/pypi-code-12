
import pandas as pd
from pybedtools import BedTool
import pybedtools
import os
import glob
import subprocess
import csv
import multiprocessing as mp
import numpy as np


def subtract_bed_rmsk(bed_name, bed_filter):
    """REMOVES regions of annotation of interest that overlap with
    repeat-masked regions
    """
    pybedtools.set_tempdir('/sc/orga/scratch/richtf01')
    if not os.path.isfile(bed_name + '.noRmsk.bed'):
        bed = BedTool(bed_name + '.bed') # .merged.sorted
        print "Removing calls in rmsk from " + bed_name + "..."
        bed_no_overlap = bed.subtract(bed_filter)
        bed_no_overlap.saveas(bed_name + '.noRmsk.bed')
        print bed_name + " done!"
    else:
        print bed_name + " rmsk calls already removed"


def subtract_bed_sd(bed_name, bed_filter):
    """REMOVES regions of annotation of interest that overlap with
    segmental duplications
    """
    pybedtools.set_tempdir('/sc/orga/scratch/richtf01')
    if not os.path.isfile(bed_name + '.noRmsk.noSD.bed'):
        bed = BedTool(bed_name + '.noRmsk.bed')
        print "Removing calls in seg dup from " + bed_name + "..."
        bed_no_overlap = bed.subtract(bed_filter)
        bed_no_overlap.saveas(bed_name + '.noRmsk.noSD.bed')
        print bed_name + " done!"
    else:
        print bed_name + " Seg dup calls already removed"


def intersect_bed(bed_name, bed_filter):
    """KEEPS regions of annotation of interest that overlap with
    repeat-masked regions
    """
    pybedtools.set_tempdir('/sc/orga/scratch/richtf01')
    if not os.path.isfile(bed_name + '.Rmsk.bed'):
        bed = BedTool(bed_name + '.merged.sorted.bed')
        print "Keeping calls in rmsk from " + bed_name + "..."
        bed_overlap = bed.intersect(bed_filter)
        bed_overlap.saveas(bed_name + '.Rmsk.bed')
        print bed_name + " done!"
    else:
        print bed_name + " rmsk calls already isolated"


def sort_bed(bed_name):
    """ SORTS a bed file after removing rmsk, sd
    """
    pybedtools.set_tempdir('/sc/orga/scratch/richtf01')
    bed_in = bed_name + '.noRmsk.noSD.bed'
    bed_out = bed_name + '.sorted.noRmsk.noSD.bed'
    if not os.path.isfile(bed_out):
        print "Sorting " + bed_in + "... "
        sort_cmd = ("sort -V -k1,1 -k2,2 %s > %s"
            % (bed_in, bed_out))
        print sort_cmd
        subprocess.call(sort_cmd, shell = True)
        print bed_name + " sorted!"
    else:
        print bed_out + " already sorted"


def merge_bed(bed_name):
    """ MERGES a bed file after removing rmsk, sd
    """
    pybedtools.set_tempdir('/sc/orga/scratch/richtf01')
    bed_in = bed_name + '.sorted.noRmsk.noSD.bed'
    bed_out = bed_name + '.merged.sorted.noRmsk.noSD.bed'
    if not os.path.isfile(bed_out):
        bed = BedTool(bed_in)
        print "Merging " + bed_in + "..."
        bed_merged = bed.merge()
        bed_merged.saveas(bed_out)
        print bed_name + " done!"
    else:
        print bed_out + " already merged"


def calculate_length(bed_name):
    """read bedfile per line as running sum
    """
    print "Counting", bed_name
    bed_in = bed_name + '.merged.sorted.noRmsk.noSD.bed'
    running_sum = 0
    with open(bed_in, 'r') as bed_iter:
        for bed_line in csv.reader(bed_iter, delimiter="\t"):
            running_sum += (float(bed_line[2]) - float(bed_line[1]))
    return running_sum


def overlap_with_observed(bed_name, observed_name, observed_denovo):
    """ count the number of observed de novos that overlap with the bed file
    """
    pybedtools.set_tempdir('/sc/orga/scratch/richtf01')
    bed_intersect_dir = ("/sc/orga/projects/chdiTrios/Felix/wgs/" +
        "anno_obs_intersect/" + observed_name + "/")
    bed_out = (bed_intersect_dir + bed_name +
        '.merged.sorted.noRmsk.noSD.' + observed_name + '.bed')
    denovo_bed = BedTool('/hpc/users/richtf01/whole_genome/' +
        'variant_calls/' + observed_denovo)
    # create or load intersection file
    print bed_name + " overlap with " + observed_name
    if not os.path.isfile(bed_out):
        bed = BedTool(bed_name + '.merged.sorted.noRmsk.noSD.bed')
        print "intersecting.. "
        denovo_anno = bed.intersect(denovo_bed)
        denovo_anno.saveas(bed_out)
    else:
        print "already intersected"
        denovo_anno = BedTool(bed_out)
    counter = 0
    for i in denovo_anno:
        counter += 1
    return counter




def PerLinePredictorFileFromBW(bed_name):
    bed_in_f = bed_name + '.merged.sorted.noRmsk.noSD.bed'
    bed_lineid_f = bed_name + '.lineID.bed'
    if not os.path.isfile(bed_lineid_f):
        print "creating line id file for", bed_name
        with open(bed_in_f, 'r') as bed_in, \
            open(bed_lineid_f, 'a+') as bed_lineid:
            count = 0
            for line in bed_in:
                in_list = line.strip().split("\t")
                chrom = in_list[0]
                start = in_list[1]
                end = in_list[2]
                lineID = "lineID" + str(count)
                out_line = "\t".join([chrom, start, end, lineID])
                bed_lineid.write(out_line + "\n")
                count += 1
    else:
        print "line id file already created for", bed_name
    bw_list = ["All_hg19_RS", "recombRate", "repliseq"]
    for bw in bw_list:
        bw_file = ("/sc/orga/projects/chdiTrios/Felix/wgs/" + \
            "bigwig_predictors/%s.bw") % (bw)
        out_f = ("/sc/orga/projects/chdiTrios/Felix/wgs/" + \
            "bigwig_predictors/%s/%s.merged.sorted.noRmsk.noSD." + \
            "lineid.%s") % (bw, bed_name, bw)
        bw_cmd = ("bigWigAverageOverBed %s \"%s\" \"%s.tab\" " + \
            "-bedOut=\"%s.bed\"")
        if not os.path.isfile(out_f + ".bed"):
            print bw_cmd % (bw_file, bed_lineid_f, out_f, out_f)
            subprocess.call(bw_cmd % (bw_file, bed_lineid_f, out_f, out_f),
                shell = True)
        else:
            print ("%s already combined with bw file %s") % (bed_name, bw)


def AvgVariancePerBedFile(bed_name, bw_name):
    bed_file_bw = ("/sc/orga/projects/chdiTrios/" +
        "Felix/wgs/bigwig_predictors/" + bw_name +
        "/" + bed_name + ".merged.sorted.noRmsk.noSD.lineid." +
        bw_name + ".bed")
    if os.path.isfile(bed_file_bw):
        print "avererging "+ bed_name + " over " + bw_name
        m = np.loadtxt(bed_file_bw, usecols=(4,), delimiter = "\t")
        # m_sum = np.sum(m, axis = 0)
        m_avg = m.mean()
        m_var = 0
        # m.var(ddof = 1)) # sd^2 = var
    else:
        print bed_name + " was not averaged over " + bw_name
        m_avg = 0
        m_var = 0
    return (m_avg, m_var)


def AvgRecombRate(bed_name):
    bed_file_bw = ("/sc/orga/projects/chdiTrios/Felix/wgs/bigwig_predictors/" + \
        "recombRate/" + bed_name + ".merged.sorted.noRmsk.noSD.lineid." + \
        "recombRate.bed")
    if os.path.isfile(bed_file_bw):
        print "avererging "+ bed_name + " over recombRate"
        m = np.loadtxt(bed_file_bw, usecols=(4,), delimiter = "\t")
        # m_sum = np.sum(m, axis = 0)
        m_binary = np.where(m > 2, 1, 0)
        return (m_binary.mean()) # sd^2 = var
    else:
        print bed_name + " was not averaged over recombRate"
        return (0)


def BedToFasta(bed_name):
    if not os.path.isfile(bed_name + ".fasta"):
        fa_cmd = ("bedtools getfasta -fi $GATKRSRC_ROOT/ucsc.hg19.fasta " + \
            "-bed %s.merged.sorted.noRmsk.noSD.bed " + \
            "-fo %s.fasta")
        print fa_cmd % (bed_name, bed_name)
        subprocess.call(fa_cmd % (bed_name, bed_name), shell = True)
    else:
        print "fasta already generated for", bed_name


def TrinucProbabilityGCCount(bed_name):
    # mutRateDict = load_trinuc_dict.load_trinuc_mut_rate_dict()
    expectedMutRate = 0
    total_len = 0
    gc_count = 0
    with open(bed_name + ".fasta", "r") as fa:
        for line in fa:
            if line.startswith('>'):
                line_split = re.split("[>:-]", line.strip())
            if not line.startswith('>'):
                dna = line.upper()
                seg_len = len(dna)
                total_len += seg_len
                for trinucleotide in mutRateDict.keys():
                    expectedMutRate += (mutRateDict[trinucleotide] * \
                                        dna.count(trinucleotide) )
                gc_count += dna.count('G') + dna.count('C')
    return (expectedMutRate, gc_count)
