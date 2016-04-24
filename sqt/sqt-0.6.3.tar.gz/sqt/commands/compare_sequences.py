#!/usr/bin/env python3
"""
Print a comparison matrix for sequences from a FASTA or text file.
All pairs of sequences are compared using the given comparison measure.
By default, this is edit distance, the minimum number of substitutions,
insertions, and deletions to transform one sequence into the other.

For the resulting matrix, a header row and column is printed;
this can be disabled by the options below.

The given list of sequences can be automatically extended by their
reverse complements, appending a suffix like _RC to each sequence's name.
"""

__author__ = "Sven Rahmann"

import sys
from sqt import HelpfulArgumentParser
from sqt.io.fasta import SequenceReader
from sqt.align import edit_distance
from sqt.dna import reverse_complement as revcomp


def get_argument_parser():
    parser = HelpfulArgumentParser(description=__doc__)
    parser.add_argument("file",
        help="file with sequences to compare")
    parser.add_argument("-c", "--compareby", default="editdistance",
        choices=("none", "identity", "editdistance"),
        help="comparison function [default: editdistance]")
    parser.add_argument("-s", "--show", default="matrix",
        choices=("none", "matrix", "min", "max"),
        help="output type (matrix or nearest neighbors)")
    parser.add_argument("-r", "--revcomp", nargs="?", const="_RC", metavar="SUFFIX",
        help="compare reverse complements, too; append _RC or argument to each name")
    parser.add_argument("-f", "--format", choices=("text","fasta","fastq"),
        help="explicitly specify file format if not FASTA")
    parser.add_argument("-R", "--norowheaders", action="store_true",
        help="do not print initial names in each row")
    parser.add_argument("-C", "--nocolumnheaders", action="store_true",
        help="do not print first row with column headers")
    parser.add_argument("-H", "--noheaders", action="store_true",
        help="both --norowheaders and --nocolumnheaders")
    parser.add_argument("-F", "--featurename", default="feature", metavar="NAME",
        help="use the given argument instead of 'feature' for features")
    parser.add_argument("-S", "--separator", default="\t", metavar="SEPARATOR",
        help="field separator [default: TAB]")
    return parser


comparison_function = dict(
    none = lambda s,t: None,
    identity = lambda s,t: int(s==t),
    editdistance = edit_distance
)


def process_file(fname, fformat):
    """return list of tuples (name, seq) from file <fname>"""
    if fformat=="text":
        with open(fname, "rt") as f:
            return [("seq_"+str(i), line.strip()) for line in f.readlines()]
    # now it's fasta or fastq
    seqs = []
    for record in SequenceReader(fname):
        name, _, _ = record.name.partition(" ")
        seq = record.sequence.upper()
        seqs.append((name,seq))
    return seqs


def show_matrix(sequences, args):
    featurename = args.featurename
    separator = args.separator
    compare = comparison_function[args.compareby]
    if not args.nocolumnheaders:
        clist = [] if args.norowheaders else [featurename]
        clist.extend([s[0] for s in sequences])
        print(separator.join(clist))
    for si in sequences:
        clist = [] if args.norowheaders else [si[0]]
        for sj in sequences:
            c = compare(si[1],sj[1])
            clist.append(str(c))
        print(separator.join(clist))


def show_neighbors(sequences, args):
    assert args.show in ("max", "min")
    domax = (args.show == "max")
    separator = args.separator
    compare = comparison_function[args.compareby]
    for i,si in enumerate(sequences):
        clist = [] if args.norowheaders else [si[0]]
        best = None;  bestlist = []
        for j,sj in enumerate(sequences):
            if i==j: continue
            c = compare(si[1],sj[1])
            if domax:
                if best is None or c > best:
                    best = c;  bestlist=[sj[0]]
                elif c == best:
                    bestlist.append(sj[0])
            else:
                if best is None or c < best:
                    best = c;  bestlist=[sj[0]]
                elif c == best:
                    bestlist.append(sj[0])
        clist.append(str(best))
        print(separator.join(clist+bestlist))


show_functions = dict(
    none = lambda sequence, args: None,
    matrix = show_matrix,
    min = show_neighbors,
    max = show_neighbors,
)


def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    sequences = process_file(args.file, args.format)
    if args.revcomp:
        rcsfx = args.revcomp
        rcs = [(name+rcsfx, revcomp(seq)) for (name,seq) in sequences]
        sequences.extend(rcs)
    fshow = show_functions[args.show]
    fshow(sequences, args)


if __name__ == '__main__':
    main()
