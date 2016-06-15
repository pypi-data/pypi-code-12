# -*- coding: utf-8 -*-

import sys
import argparse
import datetime
import random
from math import sqrt, modf, ceil, floor, log10

import numpy as np
from scipy.stats import lognorm, chi2, truncnorm

import dinopy as dp
# Note: import pysam on demand later (in main)

from .version import __version__, __author__, DESCRIPTION


DEFAULT_LOGNORMAL_PARAMETERS = (0.200110276521, -10075.4363813, 17922.611306)
BASES = [ord("A"), ord("C"), ord("G"), ord("T")]  # byte values of bases
QUALITIES = "!\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"

def read_reference(input_path):
    """
    Read a reference in fasta format.
    Return the reference as a list of tuples (sequence, name, length, interval),
    one tuple for each chromosome.
    """
    fp = dp.FastaReader(input_path)
    chromosomes = [(sequence, name.decode("utf-8").replace(" ", "_"), length, interval)
                   for sequence, name, length, interval in fp.entries(dtype=bytearray)]
    return chromosomes


def generate_reference(length, output_path, gc_content=0.5):
    """
    Generate a random DNA reference sequence with one chromosome and given GC content.
    Save the resulting sequence in FASTA format to 'output_path'.
    Return [(reference, name, len(reference), (0, len(reference)))] to be conform
    with the output when reading a reference, with [(bytearray, str, in, (int, int))]
    """
    reference = bytearray([0]*length)
    p_gc = gc_content / 2.0
    p_at = (1 - gc_content) / 2.0
    (ca, cc, cg) = (p_at, p_at+p_gc, p_at+2*p_gc)
    rnd = random.random
    for i in range(length):
        u = rnd()
        if u < ca:
            reference[i] = 65 # ord("A")
        elif u < cc:
            reference[i] = 67 # ord("C")
        elif u < cg:
            reference[i] = 71 # ord("G")
        else:
            reference[i] = 84 # ord("T")
    name = ">random_reference_with_{}_GC".format(gc_content)
    # Save reference in file at path
    with open(output_path, "wt") as f:
        f.write(name+"\n")
        f.write(reference.decode("utf-8"))
    return [(reference, name, len(reference), (0, len(reference)))]


class ReadlengthProvider:
    """If rlp is a ReadlengthProvider, rlp[i] provides the i-th read length"""

    def __init__(self, typ, value, num_reads, min_length=0):
        """
        Set the draw method according to type 'typ' and provide 'num_reads' read lengths.
        typ == 'fixed': value has to be int;
            __getitem__[i] returns fixed length;
        typ == 'list': value has to be a list of read lengths;
            num_reads random samples are drawn;
            __getitem__[i] returns the i-th random sample of the list
        typ == 'lognorm': value has to be a tuple of parameters;
            __getitem__[i] returns i-th sample from lognormal distribution.
        """
        self.value = value

        if typ == "fixed":
            if not (type(value) == int):
                raise TypeError("Fixed readlength has to be of type int.")
            self.lengths = [value] * num_reads

        elif typ == "list":
            if not (type(value) == list):
                raise TypeError("To draw readlength from list a list containing ints is required.")
            indices = np.random.randint(0, len(value)-1, size=num_reads)
            self.lengths = [value[i] for i in indices]

        elif typ == "lognorm":
            if not (type(value) == tuple and len(value) == 3):
                raise TypeError("To draw readlength from lognormal distribution a tuple with three floats is required.")
            sigma, loc, scale = value
            lengths = lognorm.rvs(s=sigma, loc=loc, scale=scale, size=num_reads)
            self.lengths = [max(min_length, int(x)) for x in lengths]

        else:
            raise ValueError("typ '{}' is unknown".format(typ))

    def __getitem__(self, i):
        return self.lengths[i]



def sample_reads(reference, num_reads, readlength_provider,
        chi2_params_n, chi2_params_s, max_passes,
        sqrt_params, norm_params, min_exp, prob_ins, prob_del, prob_subst,
        output_path, sam_output, no_sam):
    """
    Sample 'num_reads' reads from the given 'reference' and write them to a file.
    For each read, 
        determine the read length and draw a number of passes,
        depending on the length and the parameters of the chi^2 distribution.
        Adjust the base error probabilities according to the number of passes.
        Add errors to the read.
        Write the read at 'output_path' and  if 'no_sam' is False, the alignment
        at 'sam_output'.
    """

    reference_names = [r[1] for r in reference]
    reference_lengths = [r[2] for r in reference]
    max_chrom_length = max(reference_lengths)

    reversals = (np.random.random(num_reads) < 0.5).tolist()

    # normal distributed noise for quality increase has to be adapted with a sigmoidal factor
    sigmoidal_factor = lambda x: 1 / (1 + 2**(-2.5/3*x+6.5/3))

    if not no_sam:
        if sam_output is None:
            sam_output = output_path + '.sam'
        sam_writer = pysam.AlignmentFile(sam_output, 'wh',
            reference_names=reference_names, reference_lengths=reference_lengths)

    with open(output_path, "wt") as f:
        # Sample the reads
        for i in range(num_reads):
            # Choose read length and chromosome
            current_readlength = readlength_provider[i]
            current_readlength = min(current_readlength, max_chrom_length)
            length = -1
            while length < current_readlength:
                (current_ref, chr_name, length, interval) = random.choice(reference)

            # Get a random read from the chosen reference
            (start_pos, read) = get_raw_read(current_ref, current_readlength)

            # compute number of passes in prefix and suffix of the read
            (current_passes, cut_position, passes_left, passes_right, percentage_left) \
                = calculate_passes(current_readlength, chi2_params_n, chi2_params_s, max_passes)
            # modify 1-pass error probabilities according to number of passes
            (cum_probs_left, cum_probs_right) = modify_probabilities(
                min_exp, sqrt_params, norm_params, sigmoidal_factor,
                passes_left, passes_right,
                prob_ins, prob_del, prob_subst)
            # insert errors into read
            (read, insertions, deletions, substitutions) = traverse_read(
                read, current_ref, start_pos, cut_position, cum_probs_left, cum_probs_right)
            read = read[0:current_readlength]  # crop to readlength
            # determine quality characters
            quality_left = QUALITIES[min(round(-10 * log10(cum_probs_left[2])), len(QUALITIES)-1)]
            quality_right = QUALITIES[min(round(-10 * log10(cum_probs_right[2])), len(QUALITIES)-1)]
            quality_values = quality_left * cut_position \
                             + quality_right*(current_readlength-cut_position)
            # convert to string and reverse the read, maybe
            read = read.decode("ascii")
            if reversals[i]:
                read = dp.reverse_complement(read)
                quality_values = quality_values[::-1]  # reverse qualities

            # write the read
            num_total_errors = len(insertions) + len(deletions) + len(substitutions)
            total_error_prob = cum_probs_left[2]*percentage_left \
                               + cum_probs_right[2]*(1.0-percentage_left)
            name = "_".join(["Read", str(i), "length="+str(current_readlength)+"bp",
                             "startpos="+str(start_pos),
                             "number_of_errors="+str(num_total_errors),
                             "total_error_prob={:.2f}".format(total_error_prob),
                             "passes="+str(current_passes), "passes_left="+str(passes_left),
                             "passes_right="+str(passes_right), "cut_position="+str(cut_position),
                            ])
            print("@"+name, file=f)
            print(read, file=f)
            print("+", file=f)
            print(quality_values, file=f)
            # write SAM file if desired
            if not no_sam:
                mapping_error_probability = 0.0000000001 # very small error probability, since we know the alignment
                write_sam_file(sam_writer, name, read, quality_values.encode(), reversals[i],
                               mapping_error_probability, chr_name, start_pos,
                               current_readlength, insertions, deletions, substitutions)
            pass  # end for i
    if not no_sam:
        sam_writer.close()


def get_raw_read(current_ref, current_readlength, bases=BASES):
    """
    Given a reference 'current_ref' as bytearray,
    and a read length 'current_readlength' as int,
    draw a start position and copy the read with given read length.
    In the read, substitute all Ns with random bases.

    Return the pair (start_pos, read),
    where start_pos is an int and read is a bytearray.
    """
    assert type(current_ref) == bytearray
    start_pos = random.randint(0, len(current_ref)-current_readlength)
    read = current_ref[start_pos:start_pos+current_readlength]  # bytearray

    Ns = frozenset([ord('N'), ord('n')])
    choice = random.choice
    # change Ns in reference to a random base in read
    for b, base in enumerate(read):
        if base in Ns:
            read[b] = choice(bases)
    return (start_pos, read)


def calculate_passes(current_readlength, chi2_params_n, chi2_params_s, max_passes):
    """
    Calculate the parameter n and s for the chi^2 distribution based on the
    'current_readlength' (int), 'chi2_params_n' (3-tuple float) and 'chi2_params_s'
    (5-tuple float) and draw the number of passes.
    The number of passes has max_passes (int) as upper bound.
    
    Calculate the cut position and the number of passes
    for the right and left side of the cut.

    Return (current_passes, cut_position, passes_left, passes_right, percentage_left):
    current_passes: passes for the current read (float)
    cut_position: position in the read where the qualities are split (int)
    passes_left: passes for the left part of the read (int)
    passes_right: passes for the right part of the read (int)
    percentage_left: percentage of the read on the left side of the cut (float)
    """
    # compute n parameter
    my_n = chi2_params_n[0] * min(current_readlength, chi2_params_n[2]) + chi2_params_n[1]
    current_n = max(0.001, my_n)

    # compute scale parameter
    if current_readlength <= chi2_params_s[2]:
        my_scale = chi2_params_s[0] * current_readlength - chi2_params_s[1]
        current_scale = max(0.001, my_scale)
    else:
        current_scale = chi2_params_s[3] / (current_readlength**chi2_params_s[4])

    # draw passes
    my_passes = chi2.rvs(current_n, scale=current_scale, loc=1)
    # draw new, when my_passes is greater than the 99.25 quantile of the current
    # chi^2 distribution -> prevents outlier over the a/x boundary
    while my_passes > chi2.ppf(0.9925, current_n, loc=1, scale=current_scale):
        my_passes = chi2.rvs(current_n, scale=current_scale, loc=1)
    # cut at maximum passes -> only for very small reads important
    current_passes = min(max_passes, my_passes)

    # find cut point
    (cut_factor, whole_passes) = modf(current_passes) # percentage of the read on one side of the cut, number of whole passes
    # left side of read has higher quality
    if whole_passes % 2 == 0:
        cut_position = round(current_readlength*cut_factor)
        passes_left = ceil(current_passes)
        passes_right = floor(current_passes)
        percentage_left = cut_factor
    # right side of read has higher quality
    else:
        cut_position = round(current_readlength * (1-cut_factor))
        passes_left = floor(current_passes)
        passes_right = ceil(current_passes)
        percentage_left = 1 - cut_factor
    return (current_passes, cut_position, passes_left, passes_right, percentage_left)


def modify_probabilities(
        min_exp, sqrt_params, norm_params, sigmoidal_factor,
        passes_left, passes_right, prob_ins, prob_del, prob_subst):
    """
    Modify the given subread probabilities with an increase factor based on the
    number of passes. The increase is determined with a noisy sqare root function
    adapted with a sigmoidal factor. For the purpose of quality trimming the
    increase exponent is bounded with min_exp.
    Return the cumulative modfified probabilities for the left and right part of
    the read: (cum_probs_left, cum_probs_right) with (ins, ins+del, ins+del+subst).
    """
    # calculate limits for left truncated normal distribution
    limit_left = (min_exp - (sqrt(passes_left+sqrt_params[0]) - sqrt_params[1])) \
        / sigmoidal_factor(passes_left)
    limit_right = (min_exp - (sqrt(passes_right+sqrt_params[0]) - sqrt_params[1])) \
        / sigmoidal_factor(passes_right)

    #draw the normal distributed noise
    increase_of_qualities_l = truncnorm.rvs(limit_left/norm_params[1], 1e10/norm_params[1],
                                            loc=norm_params[0], scale=norm_params[1], size=1)[0]
    increase_of_qualities_r = truncnorm.rvs(limit_right/norm_params[1], 1e10/norm_params[1],
                                            loc=norm_params[0], scale=norm_params[1], size=1)[0]
    # and calculate the exponents for quality increase
    ex_left = increase_of_qualities_l * sigmoidal_factor(passes_left) \
        + sqrt(passes_left+sqrt_params[0]) - sqrt_params[1]
    ex_right = increase_of_qualities_r * sigmoidal_factor(passes_right) \
        + sqrt(passes_right+sqrt_params[0]) - sqrt_params[1]
    # we expect these exponents to be >= 1.0 in general,
    # leading to an increase in quality.
    # They can, however, be < 1.0 by chance,
    # and we avoid that they fall below 0.6:
    exponent_left = max(0.6, ex_left)
    exponent_right = max(0.6, ex_right)

    pil = prob_ins ** exponent_left
    pdl = prob_del ** exponent_left
    psl = prob_subst ** exponent_left
    cum_probs_left = (pil, pil+pdl, pil+pdl+psl)

    pir = prob_ins ** exponent_right
    pdr = prob_del ** exponent_right
    psr = prob_subst ** exponent_right
    cum_probs_right = (pir, pir+pdr, pir+pdr+psr)

    return (cum_probs_left, cum_probs_right)


def traverse_read(read, current_ref, start_pos, cut_position, cum_probs_left, cum_probs_right,
    bases=BASES):
    """
    Traverse the read and insert errors with the given probabilities.
    read: bytearray with ASCII codes of ACGT
    current_ref: bytearray of chromosome
    start_pos: start position of read in chromosome (current_ref)
    cut_position: use cum_probs_left in read[0:cut_position] 
        and cum_probs_right in read[cut_position:]
    cum_probs_left: triples of cumulative error probabilities (ins, ins+del, ins+del+subst)
    cum_probs_right: dito

    Return the modified read and the lists containing the errors:
    (read, insertions, deletions, substitutions)
    """
    insertions = []
    deletions = []
    substitutions = []
    choice = random.choice
    current_readlength = len(read)
    Ns = frozenset([ord('N'), ord('n')])

    random_numbers = np.random.random(current_readlength*2).tolist()  # *2 for possible insertions
    j = 0  # current read position
    current_rand_pos = 0
    while j < current_readlength:
        assert 0 <= j < current_readlength, "error! j not in correct range"
        ci, cd, cs = cum_probs_left  if j < cut_position  else cum_probs_right
        r = random_numbers[current_rand_pos]
        current_rand_pos += 1

        if r < ci:
            # insert a base
            insertions.append(j)
            read[j:] = bytearray([choice(bases)]) + read[j:-1]  # preserve read length
            j += 1
        elif r < cd:
            # delete a base
            deletions.append(j)
            # add next base of reference at the end to preserve read length,
            # or a random base if reference is exceeded.
            next_pos = start_pos + current_readlength + len(deletions) - len(insertions)

            if next_pos < len(current_ref):
                new_base = current_ref[next_pos]
                if new_base in Ns:
                    new_base = choice(bases)
            else:
                # random base after end of reference
                new_base = choice(bases)
            read = read[0:j] + read[j+1:] + bytearray([new_base])
            # do not change j
        elif r < cs:
            # substitute a base
            substitutions.append(j)
            base = choice(bases)
            while base == read[j]:
                base = choice(bases)
            read[j] = base
            j += 1
        else:
            # no error at this position
            j += 1
    return (read, insertions, deletions, substitutions)


def write_sam_file(sam_writer, name, read, quality_values, reverse,
        mapping_error_probability, chr_name, start_pos, current_readlength,
        insertions, deletions, substitutions):
    """
    Write the sam file entry for a given read into an open sam_writer.
    name: name of the read (str)
    read: sequence of the read (bytearray)
    quality_values: (bytes)
    reverse: (boolean)
    mapping_quality: error probability for correct mapping
    chr_name: (str)
    start_pos: start position of the read in the chromosome (int)
    current_readlength: (int)
    insertions: list of positions with insertions
    deletions: list of positions with deletions
    substitutions: list of positions with substitutions
    """
    assert type(quality_values) == bytes
    cigar = calculate_cigar_operations(current_readlength, insertions, deletions, substitutions)

    a = pysam.AlignedSegment()
    a.query_name = name
    a.query_sequence = read
    if reverse:
        a.flag = 16
    else:
        a.flag = 0
    a.reference_id = sam_writer.gettid(chr_name)
    a.reference_start = start_pos
    a.mapping_quality = -10*log10(mapping_error_probability)
    a.cigar = cigar
    a.next_reference_id = sam_writer.gettid(chr_name)
    a.next_reference_start = -1
    a.template_length = current_readlength
    # a.query_qualities = pysam.fromQualityString(quality_values)
    a.query_qualities = pysam.qualitystring_to_array(quality_values)
    number_of_errors = len(insertions) + len(deletions) + len(substitutions)
    a.set_tag("NM", number_of_errors, "i")
    a.set_tag("XS", 0, "i")
    a.set_tag("XE", current_readlength, "i")
    a.set_tag("XQ", current_readlength, "i")
    sam_writer.write(a)


def calculate_cigar_operations(current_readlength, insertions, deletions, substitutions):
    """
    Given a read length, and three lists of positions
    with insertions, deletions, substitutions, respectively,
    calculate the cigar string for one read.
    Return list of pairs of (cigar operation codes, count) for pysam.
    """
    MATCH, DELETION, INSERTION, SUBST = (7, 2, 1, 8)  # PySam CIGAR Operation Codes
    cigar = []
    count = 0
    last_op = MATCH
    point_ins = 0
    point_del = 0
    point_sub = 0
    for i in range(current_readlength):
        if point_del < len(deletions) and i == deletions[point_del]:
            # multiple deletions get the same index
            cigar.append((last_op, count))
            count = 1
            last_op = DELETION
            point_del += 1
            while point_del < len(deletions) and i == deletions[point_del]:
                count += 1
                point_del += 1

        if point_ins < len(insertions) and i == insertions[point_ins]:
            point_ins += 1
            if last_op == INSERTION:
                count += 1
            else:
                cigar.append((last_op, count))
                count = 1
                last_op = INSERTION
        elif point_sub < len(substitutions) and i == substitutions[point_sub]:
            point_sub += 1
            if last_op == SUBST:
                count += 1
            else:
                cigar.append((last_op, count))
                count = 1
                last_op = SUBST
        else:
            if last_op == MATCH:
                count += 1
            else:
                cigar.append((last_op, count))
                count = 1
                last_op = MATCH
    cigar.append((last_op, count))
    if cigar[0][1] == 0:
        cigar = cigar[1:]
    return cigar


def read_readlenghts_from_reads(files, output):
    """
    Read all reads from a file and return the list of read lengths.
    If output is not None, write the read lengths to that file.
    """
    lengths = []
    for filename in files:
        fr = dp.FastqReader(filename)
        for read, name in fr.reads(quality_values=False, dtype=bytes):
            lengths.append(len(read))
    if output is not None:
        with open(output, "wt") as writer:
            print("\n".join(map(str,lengths)), file=writer)
    return lengths


def read_readlenghts_from_file(filename):
    """
    Read the read lengths from a file containing one length in each line.
    Return a list of read lengths (int).
    """
    with open(filename, "r") as f:
        lengths = [int(line.strip())  for line in f  if len(line.strip())>0]
    return lengths


def calculate_minimum_exponent(probability_threshold, p_i, p_d, p_s):
    """ Calculate the minimum exponent for quality increase to ensure that the
        sum of modified error probabilities is < probability_threshold.
        Return the minimum exponent.
    """
    min_exp = 1.0
    # term is the sum of the modified probabilities that must be < probability_threshold
    term = lambda ex: p_i**ex + p_d**ex + p_s**ex
    # geometric search for the value
    if term(min_exp) < probability_threshold:
        while term(min_exp) < probability_threshold:
            min_exp = min_exp / 2
        left = min_exp
        right = min_exp * 2
    else:
        while term(min_exp) > probability_threshold:
            min_exp = min_exp * 2
        left = min_exp / 2
        right = min_exp
    # binary search with fixed number of iterations
    for i in range(15):
        m = (left + right) / 2
        if term(m) == probability_threshold:
            min_exp = m
            break
        elif term(m) > probability_threshold:
            left = m
            min_exp = (m + right) / 2
        else:
            right = m
            min_exp = (left + m) / 2
    return min_exp


def get_argument_parser():
    """
    Return the argument parser for this applicaton
    """
    parser = argparse.ArgumentParser(prog="simlord",
        description="SimLoRD v{} -- {}".format(__version__,DESCRIPTION))
    parser.add_argument('--version', action='version', version="SimLoRD v"+__version__)

    group_ref = parser.add_mutually_exclusive_group(required=True)
    group_ref.add_argument("--read-reference", "-rr", metavar="PATH",
        help="Read a reference from PATH to sample  reads from")
    group_ref.add_argument("--generate-reference", "-gr", metavar=("GC", "LENGTH"),
        nargs=2, type=float,
        help="Generate a random reference with given GC-content and given length")

    parser.add_argument("--save-reference", "-sr", metavar="PATH",
        help="Save the random reference as fasta-file at given PATH. "
        "By default, save at output path with '_reference.fasta' appended.")

    parser.add_argument("--num-reads", "-n", metavar="INT", type=int, default=1000,
        help="Number of reads to simulate (%(default)s).")

    parser.add_argument("--chi2-params-s", "-xs", metavar="PAR", type=float, nargs=5,
        default=(0.01214, -5.12, 675, 48303.0732881, 1.4691051212330266),
        help="Parameters for the curve determining the parameter scale for the chi^2 distribution: m,b, z, c, a for  'm*x + b' if x <= z and 'c * x^-a' if x > z (default= %(default)s)")

    parser.add_argument("--chi2-params-n", "-xn", metavar="PAR", type=float, nargs=3,
        default=(1.89237136e-03, 2.53944970e+00, 5500),
        help="Parameters for the function determining the parameter n for the chi^2 distribution: m, b, z  for 'm*x + b' if x < z and 'm*z + b' for x >=z (default= %(default)s).")

    parser.add_argument("--max-passes", "-mp", metavar="INT", type=int, default=40,
        help="Maximal number of passes for one molecule (default= %(default)s).")

    parser.add_argument("--sqrt-params", "-sq", metavar="PAR", type=float, nargs=2,
        default=(0.5, 0.2247),
        help="Parameters for the sqare root function for the quality increase: a, b for 'sqrt(x+a) - b' (default= %(default)s)")

    parser.add_argument("--norm-params", "-nd", metavar="PAR", type=float, nargs=2,
        default=(0, 0.2),
        help="Parameters for normal distributed noise added to quality increase sqare root function (default= %(default)s)")

    parser.add_argument("--probability-threshold", "-t", metavar="FLOAT", type=float, nargs=1,
        default=(0.2),
        help="Upper bound for the modified total error probability (default= %(default)s)")

    parser.add_argument("--prob-ins", "-pi", metavar="FLOAT", type=float, default=0.11,
        help="Probability for insertions for reads with one pass. (default= %(default)s)")
    parser.add_argument("--prob-del", "-pd", metavar="FLOAT", type=float, default=0.04,
        help="Probability for deletions for reads with one pass. (default= %(default)s)", )
    parser.add_argument("--prob-sub", "-ps", metavar="FLOAT", type=float, default=0.01,
        help="Probability for substitutions for reads with one pass. (default= %(default)s)")

    parser.add_argument("--min-readlength", "-mr", metavar="INT", type=int,
        help="Minium read length (default= %(default)s) for lognormal distribution", default=50)

    group_len = parser.add_mutually_exclusive_group()
    group_len.add_argument("--lognorm-readlength", "-ln", metavar="PARAMETER", nargs="*",
        type=float, #default=[0.200110276521, -10075.4363813, 17922.611306],
        help="Parameters for lognormal read length distribution: (sigma, loc, scale), empty for defaults")
    group_len.add_argument("--fixed-readlength", "-fl", metavar="INT", type=int,
        help="Fixed read length for all reads.")
    group_len.add_argument("--sample-readlength-from-fastq", "-sf", metavar="PATH", nargs="+",
        help="Sample read length from a fastq-file at PATH containing reads.")
    group_len.add_argument("--sample-readlength-from-text", "-st", metavar="PATH",
        help="Sample read length from a text file (one length per line).")

    parser.add_argument("output", metavar="OUTPUT_PREFIX",
        help="Save the simulated reads as a fastq-file at OUTPUT_PREFIX.fastq")

    parser.add_argument("--sam-output", "-so", metavar="SAM_OUTPUT",
        help="Save the alignments in a sam-file at SAM_OUTPUT. "
        "By default, use OUTPUT_PREFIX.sam.")
    parser.add_argument("--no-sam", action='store_true',
        help="Do not calculate the alignment and write a sam file.")
    return parser


def simulate(args):
    """
    Simulate reads according to the given parameters.
    """

    # Obtain the reference.
    t1 = datetime.datetime.now()
    if args.read_reference is not None:
        reference = read_reference(args.read_reference)
    elif args.generate_reference is not None:
        (gc, length) = args.generate_reference
        length = int(length)  # parameters are initially floats
        if gc < 0.0 or gc > 1.0:
            raise ValueError("GC content of generated reference must be in [0, 1].")
        if length < 0:
            raise ValueError("Length of generated reference must be >= 0.")
        if args.save_reference is not None:
            reference_path = args.save_reference
        else:
            reference_path = args.output + "_reference.fasta"
        reference = generate_reference(length, reference_path, gc)
    else:
        raise RuntimeError("Must read or generate reference!")
    t2 = datetime.datetime.now()
    print("Time for reading/generating the reference: {} h".format(t2-t1), file=sys.stderr)

    # Manage the read length sampling method.
    if args.fixed_readlength is not None:
        readlength_provider = ReadlengthProvider("fixed", args.fixed_readlength, args.num_reads)
    elif args.sample_readlength_from_fastq is not None:
        lengths = read_readlenghts_from_reads(args.sample_readlength_from_fastq, None)
        readlength_provider = ReadlengthProvider("list", lengths, args.num_reads)
    elif args.sample_readlength_from_text is not None:
        lengths = read_readlenghts_from_file(args.sample_readlength_from_text)
        readlength_provider = ReadlengthProvider("list", lengths, args.num_reads)
    elif args.lognorm_readlength is not None:
        nparams = len(args.lognorm_readlength)
        if nparams == 0:  # -ln without parameter
            ln_values = DEFAULT_LOGNORMAL_PARAMETERS
        elif nparams == 3:
            ln_values = tuple(args.lognorm_readlength)
        else:
            raise ValueError("Wrong number of parameters for lognorm distribution. Values for sigma, loc and scale are required.")
        readlength_provider = ReadlengthProvider("lognorm", ln_values, args.num_reads, args.min_readlength)
    else:  # all read length args are None, use default of lognormal distribution
        ln_values = DEFAULT_LOGNORMAL_PARAMETERS
        readlength_provider = ReadlengthProvider("lognorm", ln_values, args.num_reads, args.min_readlength)

    if args.prob_ins + args.prob_del + args.prob_sub > 1:
        raise ValueError("Sum of error probabilities must be < 1.")

    min_exp = calculate_minimum_exponent(args.probability_threshold, args.prob_ins,
                                         args.prob_del, args.prob_sub)

    # Actually sample the reads
    t3 = datetime.datetime.now()
    sample_reads(reference=reference, num_reads=args.num_reads,
        readlength_provider=readlength_provider, chi2_params_n=args.chi2_params_n,
        chi2_params_s=args.chi2_params_s, max_passes=args.max_passes,
        sqrt_params=args.sqrt_params, norm_params=args.norm_params,
        min_exp=min_exp, prob_ins=args.prob_ins, prob_del=args.prob_del,
        prob_subst=args.prob_sub, output_path=args.output+".fastq",
        sam_output=args.sam_output, no_sam=args.no_sam)
    t4 = datetime.datetime.now()
    print("Time for simulation of {} reads: {} h.".format(args.num_reads, t4-t3),
        file=sys.stderr)



def main():
    """
    (main function)
    Import pysam at the global level if SAM output is desired.
    Then run simulate() with given arguments.
    """
    global pysam
    parser = get_argument_parser()
    args = parser.parse_args()
    if not args.no_sam:
        import pysam
    else:
        pysam = None
    simulate(args)


if __name__ == "__main__":
    main()


