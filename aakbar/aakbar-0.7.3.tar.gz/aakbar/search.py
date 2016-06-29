# -*- coding: utf-8 -*-
'''Searching for signature occurrances in aakbar.
'''

# standard library imports
import os
import shutil
from collections import Counter
import csv

# external packages
import numpy as np
import pandas as pd
import pyfaidx
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

# module imports
from .common import *
from . import cli, get_user_context_obj, logger, log_elapsed_time

# Matplotlib -use non-interactive backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#
# Global constants
#
RESIDUES_TO_BASES = 3
HISTOGRAM_BINS = 14

#
# Classes begin here.
#
class PeptideSignatureSearcher(object):
    '''Find peptide signatures in sequences.
    '''
    def __init__(self, filestem, sig_frame, k, n_sets, genome_size,
                 nucleotides=False):
        self.filestem = filestem
        self.k = k
        self.sig_frame = sig_frame
        self.n_sets = n_sets
        self.genome_size = genome_size
        self.nucleotide_input = nucleotides
        #
        self.signatures = np.array(sig_frame.index, dtype=np.dtype(('S%d' % (self.k))))
        self.signatures.sort()
        logger.info('%d %d-mer terms defined in signature file.',
                     len(self.signatures), k)
        # attributes to be initialized per set
        self.input_dict = None
        self.counter = None
        self.code = None
        self.residues_read = None
        self.dir = None
        self.coverage = None
        self.divergence = None
        self.n_seqs = None
        # per-gene attributes
        self.weightarr = None

    def init_set(self, input_dict, code, dir):
        global config_obj
        self.input_dict = input_dict
        self.code = code
        self.counter = Counter()
        self.residues_read = 0
        self.n_seqs = 0
        self.coverage = []
        self.divergence = []
        self.sigcountpath = os.path.join(dir, self.filestem + '_sigcounts.tsv')
        #
        # Signature list initialization
        #
        siglistpath = os.path.join(dir, self.filestem + '_siglist.tsv')
        self.siglistfh = open(siglistpath, 'wt')
        self.siglistwriter = csv.DictWriter(self.siglistfh,
                                            fieldnames=['signature',
                                                        'key',
                                                        'length',
                                                        'position',
                                                        'intersections',
                                                        'max_count',
                                                        'frame'],
                                            delimiter='\t')
        self.siglistwriter.writeheader()
        #
        # Gene list initialization
        #
        genestatspath = os.path.join(dir, self.filestem + '_genestats.tsv')
        self.genestatsfh = open(genestatspath, 'wt')
        self.genestatswriter = csv.DictWriter(self.genestatsfh,
                                              fieldnames=['key',
                                                          'length',
                                                          'coverage',
                                                          'divergence'],
                                              delimiter='\t')
        self.genestatswriter.writeheader()
        #
        # coverage and divergence histograms
        #
        self.coveragehistpath = os.path.join(dir, self.filestem + '_coveragehist.tsv')
        self.coverageplotpath = os.path.join(dir, self.filestem + '_coverageplot.' +
                                             config_obj.config_dict['plot_type'])
        self.divergencehistpath = os.path.join(dir, self.filestem + '_divergencehist.tsv')
        self.divergenceplotpath = os.path.join(dir, self.filestem + '_divergenceplot.' +
                                               config_obj.config_dict['plot_type'])


    def _count_matches(self, match, terms, key, frame):
        match_positions = np.where(terms == match)[0]
        forwards = bool(frame%2)
        offset = int(frame/2)
        if self.nucleotide_input:
            if forwards:
                match_positions = match_positions*3 + offset
                k = self.k * 3
            else:
                match_positions = len(self.seq) - 1 - match_positions*3 - offset
                k = self.k * -3
        else:
            k = self.k
        match_str = to_str(match)
        match_count = len(match_positions)
        self.counter[match_str] += match_count
        sig_stats = self.sig_frame.loc[match_str]
        intersections = sig_stats['intersections']
        max_count = sig_stats['max_count']
        for pos in match_positions:
            self.siglistwriter.writerow({
                    'signature': to_str(match),
                    'key': key,
                    'length': len(self.seq),
                    'position': pos,
                    'intersections': intersections,
                    'max_count': max_count,
                    'frame': frame})
            for i in range(pos, pos+k):
                self.weightarr[i] = max(self.weightarr[i], intersections)


    def _init_weightarr(self, seq):
        self.seq = seq
        self.weightarr = np.zeros(len(self.seq), dtype=np.int32)


    def _write_weightstats(self, key):
        # calculate per-gene stats
        nonzero = self.weightarr > 0
        coverage = nonzero.astype(int).mean()
        self.coverage.append(coverage)
        if coverage > 0.0:
            divergence = (1. - self.weightarr[nonzero]/self.n_sets).mean()
        else:
            divergence = np.nan # avoid warning on mean if no signatures found
        self.divergence.append(divergence)
        self.genestatswriter.writerow({
            'key': key,
            'length':len(self.seq),
            'coverage': coverage,
            'divergence':divergence})
        #
        weight_str = ''.join(['%x' %i for i in self.weightarr])
        if isinstance(self.seq, str):  # strings need to have whole length set
            self.seq = weight_str
        else:  # may be MutableSeq that needs lengths
            end = len(self.seq)
            self.seq[:end] = weight_str[:end]


    def search_as_peptide(self, key):
        s = self.input_dict[key]
        if len(s) == 0:
            logger.warn('  Empty sequence with key "%s".', key)
            return
        self.n_seqs +=1
        self.residues_read += len(s)
        self._init_weightarr(s)
        if self.nucleotide_input: # do 6-frame translation
            seq_bytes_list = []
            seq = to_bytes(str(s))
            length = len(seq)
            for offset in range(3): # three bases in a codon
                DNA = Seq(to_str(seq[offset:offset+int((length-offset)/3)*3]), generic_dna)
                seq_bytes_list.append(DNA.translate())
                seq_bytes_list.append(DNA.reverse_complement().translate())
        else:
            seq_bytes_list = [to_bytes(str(s))]
        for frame, seq_bytes in enumerate(seq_bytes_list):
            terms = np.array([to_str(seq_bytes[i:i + self.k]) for i in range(len(seq_bytes) - self.k)],
                             dtype=np.dtype(('S%d' % (self.k))))
            unique_terms = np.unique(terms)
            for match in np.intersect1d(self.signatures, unique_terms, assume_unique=True):
                self._count_matches(match, terms, key, frame)
            self._write_weightstats(key)


    def close_set(self):
        self.siglistfh.close()
        self.genestatsfh.close()
        logger.info('   %d sequences, %d residues read in %s.',
                    self.n_seqs, self.residues_read, self.code)
        if self.genome_size is None:
            self.genome_size = self.residues_read*RESIDUES_TO_BASES
        logger.info('   Mean per-gene coverage is %.2f%%.',
                    np.array(self.coverage).mean()*100.)
        logger.info('   Genome size for frequency calculations is %d bp.',
                    self.genome_size)
        most_common = self.counter.most_common()
        if len(most_common) >0:
            top_sig, top_freq = most_common[0]
        else: # no signatures found
            top_sig = '""'
            top_freq = 0
        logger.info('   Most common signature is %s, which occurs %d times (%e/bp).',
                    top_sig,
                    top_freq,
                    top_freq/self.genome_size)
        signatures = []
        counts = []
        count_freqs = []
        sig_freqs = []
        max_counts = []
        for signature, count in most_common:
            signatures.append(signature)
            counts.append(count)
            count_freqs.append(count/self.genome_size)
            sig_stats = self.sig_frame.loc[signature]
            sig_freqs.append(float(sig_stats['intersections'])/self.n_sets)
            max_counts.append(sig_stats['max_count'])
        #
        # write signature counts
        #
        logger.debug('Writing signature counts file "%s".', self.sigcountpath)
        pd.DataFrame({'counts': counts,
                      'count_freq':count_freqs,
                      'sig_weight': sig_freqs,
                      'max_count':max_counts},
                    columns=['counts',
                             'count_freq',
                             'max_count',
                             'sig_weight'],
                     index=signatures
        ).to_csv(self.sigcountpath, sep='\t')
        #
        # write and plot coverage histogram
        #
        coverage_hist, bins = np.histogram(np.array(self.coverage)*100.,
                                                    bins=HISTOGRAM_BINS,
                                                    range=[0.,100.])
        bin_centers = bins[:-1]  # zero should really be zero
        coverage_hist = coverage_hist*100./len(self.coverage)
        logger.debug('Writing coverage histogram to "%s".', self.coveragehistpath)
        pd.Series(coverage_hist, index=bin_centers).to_csv(self.coveragehistpath,
                                                  sep='\t',
                                                  float_format='%.3f')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(bin_centers, coverage_hist)
        plt.title('Coverage Distribution for %s' % (self.code.capitalize()))
        plt.xlabel('Percent Covered')
        plt.ylabel('Percent of Genes')
        plt.savefig(self.coverageplotpath)
        #
        # write divergence histogram
        #
        divergence_hist, bins = np.histogram(self.divergence,
                                             bins=HISTOGRAM_BINS,
                                             range=[0.,1.])

        bin_centers = (bins[:-1] + bins[1:]) / 2.
        divergence_hist = divergence_hist * 100. / len(self.divergence)
        logger.debug('Writing divergence histogram to "%s".', self.divergencehistpath)
        pd.Series(coverage_hist, index=bin_centers).to_csv(self.divergencehistpath,
                                                           sep='\t',
                                                           float_format='%.3f')
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(bin_centers, divergence_hist)
        plt.title('Divergence Distribution for %s' % (self.code.capitalize()))
        plt.xlabel('Signature Divergence Score')
        plt.ylabel('Percent of Genes')
        plt.savefig(self.divergenceplotpath)

#
# Cli commands begin here.
#
@cli.command()
@click.option('--genome_size', type=int, default=None,
              help='Genome size in bp for frequency calculations')
@click.option('--nucleotides/--no-nucleotides', default=False,
              help='Input file is nucleotides.')
@click.argument('infilename', type=str)
@click.argument('filestem', type=str)
@click.argument('setlist', nargs=-1, type=DATA_SET_VALIDATOR)
@log_elapsed_time()
def search_peptide_occurrances(genome_size, nucleotides, infilename, filestem, setlist):
    '''Find signatures in peptide space.

    '''
    global config_obj
    # context inputs
    user_ctx = get_user_context_obj()
    if user_ctx['first_n']:
        logger.info('Only first %d records will be used', user_ctx['first_n'])
    # parameter inputs
    logger.debug('Input file name is "%s".', infilename)
    logger.info('Signature file stem is "%s".', filestem)
    setlist = DATA_SET_VALIDATOR.multiple_or_empty_set(setlist)
    logger.info('Searching in %d data sets:', len(setlist))
    #
    # read signature file
    #
    summarydir = config_obj.config_dict['summary']['dir']
    sigfilepath = os.path.join(summarydir, filestem + '_terms.tsv')
    if not os.path.exists(sigfilepath):
        logger.error('Signature file "%s" does not exist.', sigfilepath)
        sys.exit(1)
    logger.debug('Reading signature file "%s".', sigfilepath)
    sig_frame = pd.read_csv(sigfilepath,
                            usecols=[0, 1, 3],
                            index_col=0,
                            sep='\t')
    k = len(sig_frame.index[0])
    n_sets = max(sig_frame['intersections'])
    outfilestem = os.path.splitext(infilename)[0]+'-'+filestem
    searcher = PeptideSignatureSearcher(outfilestem,
                                        sig_frame,
                                        k,
                                        n_sets,
                                        genome_size,
                                        nucleotides=nucleotides)
    #
    # loop on sets
    #
    for calc_set in setlist:
        dir = config_obj.config_dict[calc_set]['dir']
        fastapath = os.path.join(dir, infilename)
        if not os.path.exists(fastapath):
            logger.error('Input file "%s" does not exist.', fastapath)
            sys.exit(1)
        footprintpath = os.path.join(dir, filestem+'_footprints.faa')
        shutil.copy(fastapath, footprintpath)
        fasta = pyfaidx.Fasta(footprintpath, mutable=True)
        searcher.init_set(fasta, calc_set, dir)
        #
        # iterate on genes in FASTA file
        #
        if user_ctx['first_n']:
            keys = list(fasta.keys())[:user_ctx['first_n']]
        else:
            keys = fasta.keys()
        n_recs = len(keys)
        #
        # loop on genes, with or without progress bars
        #
        if user_ctx['progress']:
            with click.progressbar(keys, label='   %s genes processed' % calc_set,
                                   length=n_recs) as bar:
                for key in bar:
                    searcher.search_as_peptide(key)
        else:
            logger.info('  %s: ', calc_set)
            for key in keys:
                searcher.search_as_peptide(key)
        searcher.close_set()
        fasta.close()

