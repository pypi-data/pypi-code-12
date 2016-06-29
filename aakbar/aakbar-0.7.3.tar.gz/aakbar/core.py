# -*- coding: utf-8 -*-
'''Core commands for aakbar.
'''

# standard library imports
import os
import shutil
import locale
import stat

# external packages
import pkg_resources
import numpy as np
import pandas as pd
import pyfaidx

# Matplotlib -use non-interactive backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# module imports
from .common import *
from . import cli, get_user_context_obj, logger, log_elapsed_time

# global definitions
ALPHABETSIZE = 20 # number of coded amino acids
UNITNAME = 'Mbasepair'
UNITMULTIPLIER = 3.E6
AMBIGUOUS_RESIDUES = ['X', '.']
NUM_HISTOGRAM_BINS = 25
DEFAULT_MAX_SCORE = 0.3

#
# Helper functions begin here.
#
def is_unambiguous(seq):
    '''Check to see if all characters (residues) are unambiguous.

    :param seq: Input sequence, possibly containing ambiguous positions ('X')
                and masked (lower-case) positions.
    :return: True if no ambiguous are contained in seq.
    '''
    if any([char in seq for char in AMBIGUOUS_RESIDUES]):
        return False
    else:
        return True


def num_masked(seq):
    """Count the number of lower-case characters in a sequence.

        :param seq: Sequence of characters.
        :type seq: str, bytes, or other convertible sequence type.
        :return: Count of lower-case characters.
        :rtype: int
    """
    gene = to_str(seq)
    mask = []
    [mask.append(gene[i].islower()) for i in range(len(gene))]
    masked = sum(mask)
    return masked



def frequency_and_score_histograms(freqs, scores, dir, filestem):
    '''Writes frequency histograms to a khmer-compatible file.

    :param freqs: Vector of frequencies.
    :param scores: Vector of scores.
    :param filepath: Output file path.
    :return:
    '''
    # calculate frequency histogram
    binvals, freq_hist = np.unique(freqs, return_counts=True)
    max_freq = max(binvals)
    hist_filepath = os.path.join(dir, filestem+'_freqhist.csv')
    logger.debug('Writing frequency histogram to %s.', hist_filepath)
    cumulative = np.cumsum(freq_hist)
    total = np.sum(freq_hist)
    pd.DataFrame({'abundance':binvals,
                  'count':freq_hist,
                  'cumulative':cumulative,
                  'cumulative_fraction':cumulative/total},
                  columns=('abundance',
                           'count',
                           'cumulative',
                           'cumulative_fraction')).to_csv(hist_filepath,
                                                         index=False,
                                                         float_format='%.3f')
    logger.info('   Maximum term frequency is %d (%.2e per unique %s).',
                max_freq,
                max_freq*UNITMULTIPLIER/len(freqs),
                UNITNAME)

    # calculate score histogram
    (score_hist, bins) = np.histogram(scores, bins=[0.,
                                                    0.01, 0.03,
                                                    0.1, 0.3,
                                                    1.0, 1.3,
                                                    2.0,3.0,4.0,5.0,100.])
    score_hist = score_hist*100./len(scores)
    score_filepath = os.path.join(dir, filestem+'_scorehist.tsv')
    logger.debug('Writing score histogram to file "%s".', score_filepath)
    pd.Series(score_hist, index=bins[:-1]).to_csv(score_filepath, sep='\t',
                                                  float_format='%.2f')


def intersection_histogram(frame, dir, filestem, plot_type, n_sets, k):
    '''Do histograms of frequencies by intersection number.

    :param frame:
    :param dir:
    :param filestem:
    :param plot_type:
    :return:
    '''
    intersect_bins = []
    lastbin = 0
    nextbin = 1
    hists = {}
    intersect_filepath = os.path.join(dir, filestem+'_intersect.tsv')
    logger.debug('Writing intersection frequency histograms to %s.', intersect_filepath)
    max_freq = max(frame['max_count'])
    while nextbin < max_freq:
        inrange = frame[frame['max_count'].isin([lastbin,nextbin])]
        ibins, ifreqs = np.unique(inrange['intersections'], return_counts=True)
        intersect_bins.append(nextbin)
        hists[nextbin] = pd.Series(ifreqs, index=ibins)
        lastbin = nextbin
        nextbin *= 2
    intersect_frame = pd.DataFrame(hists).transpose().fillna(0).astype(int)
    intersect_frame.to_csv(intersect_filepath, sep='\t')
    #
    # plot intersection histograms
    #
    plot_filepath = os.path.join(dir, filestem+'_intersect.'+ plot_type)
    logger.debug('Plotting intersection histograms to %s.', plot_filepath)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xvals = np.array(list(range(2, n_sets+1)), dtype=np.int32)
    for i in range(len(intersect_frame)):
        bin_edge = intersect_frame.index[i]
        data = intersect_frame.iloc[i]
        sum = data.sum()
        if i == 0:
            label = 'Singletons (%s)' %locale.format('%d',
                                                     sum,
                                                     grouping=True)
        else:
            label='%d+/genome (%s)' %(bin_edge,
                                      locale.format('%d',
                                                    sum,
                                                    grouping=True))
        ax.plot(xvals,
                data*100./sum,
                '-',
                label=label)
    ax.legend(loc=9)
    plt.xlim([2,n_sets])
    plt.title('%d-mer Intersections Across %d Genomes' %(k, n_sets))
    plt.xlabel('Number Intersecting')
    plt.ylabel('% of Shared 10-mers in Bin')
    plt.savefig(plot_filepath)


#
# Cli commands begin here.
#
@cli.command()
@click.option('-k', default=DEFAULT_K, show_default=True, help='Term length')
@click.argument('infilename', type=str)
@click.argument('outfilestem', type=str)
@click.argument('setlist', nargs=-1, type=DATA_SET_VALIDATOR)
@log_elapsed_time()
def calculate_peptide_terms(k, infilename, outfilestem, setlist):
    '''Write peptide terms and histograms.

    '''
    # context inputs
    user_ctx = get_user_context_obj()
    if user_ctx['first_n']:
        logger.info('Only first %d records will be used', user_ctx['first_n'])
    simplicity_obj = user_ctx['simplicity_object']
    logger.info('Simplicity function is %s.',
                simplicity_obj.desc)
    simplicity_obj.set_k(k)
    # parameter inputs
    logger.info('Term size is %d characters.', k)
    logger.info('Input file name is "%s".', infilename)
    logger.info('Output file stem is "%s".', outfilestem)
    setlist = DATA_SET_VALIDATOR.multiple_or_empty_set(setlist)
    logger.info('Calculating terms for %d data sets:', len(setlist))
    #
    # loop on sets
    #
    for calc_set in setlist:
        dir = config_obj.config_dict[calc_set]['dir']
        infilepath = os.path.join(dir, infilename)
        if not os.path.exists(infilepath):
            logger.error('Input file "%s" does not exist.', infilepath)
            sys.exit(1)
        #
        # calculate each unambiguous term and its score
        #
        term_score_list = []
        n_residues = 0
        n_raw_terms = 0
        fasta  = pyfaidx.Fasta(infilepath, mutable=True)
        if user_ctx['first_n']:
            keys = list(fasta.keys())[:user_ctx['first_n']]
        else:
            keys = fasta.keys()
        n_recs = len(keys)
        #
        # loop on genes, with or without progress bars
        #
        if user_ctx['progress']:
            with click.progressbar(keys, label='   %s genes processed' %calc_set,
                                   length=n_recs) as bar:
                for key in bar:
                    seq = fasta[key]
                    s_scores = np.array(simplicity_obj.score(seq))
                    seq = to_str(seq).upper()
                    n_residues += len(seq)
                    n_raw_terms += len(seq) - k + 1
                    term_score_list += [ (str(seq[i:i+k]), s_scores[i])
                                         for i in range(len(seq)-k)
                                         if is_unambiguous(str(seq[i:i+k]))]
        else:
            logger.info('  %s: ', calc_set)
            for key in keys:
                seq = fasta[key]
                s_scores = np.array(simplicity_obj.score(seq))
                seq = to_str(seq).upper()
                n_residues += len(seq)
                n_raw_terms += len(seq) - k + 1
                term_score_list += [ (str(seq[i:i+k]), s_scores[i])
                                     for i in range(len(seq)-k)
                                     if is_unambiguous(str(seq[i:i+k]))]

        fasta.close()
        term_arr = np.array([term for term, score in term_score_list],
                            dtype=np.dtype(('S%d'%(k))))
        score_arr = np.array([score for term, score in term_score_list],
                             dtype=np.int16)
        del term_score_list
        n_terms = len(term_arr)
        n_skipped = n_raw_terms - n_terms
        logger.info('   %s genes, %s residues, %s (%0.2f%%) ambiguous, and %s input terms.',
                    locale.format('%d', n_recs, grouping=True),
                    locale.format('%d', n_residues, grouping=True),
                    locale.format('%d', n_skipped, grouping=True),
                    100*n_skipped/n_raw_terms,
                    locale.format('%d', n_terms, grouping=True),
                    )
        #
        # calculate unique terms
        #
        sort_arr = np.argsort(term_arr)
        term_arr = term_arr[sort_arr]
        score_arr = score_arr[sort_arr]
        unique_terms, beginnings, freqs = np.unique(term_arr,
                                        return_index=True,
                                        return_counts=True)
        max_freq = max(freqs)
        mean_scores = np.array([score_arr[beginnings[i]:beginnings[i]+freqs[i]].mean()
                                for i in range(len(beginnings))], dtype=np.float32)
        n_unique = len(unique_terms)
        logger.info('   %s unique terms (%.2f%% of input, %.6f%% of %s possible %d-mers).',
                    locale.format('%d', n_unique, grouping=True),
                    100.*n_unique/n_terms,
                    100.*n_unique/(ALPHABETSIZE**k),
                    locale.format('%d', ALPHABETSIZE**k, grouping=True),
                    k)
        #
        # write terms, counts, and scores in sorted form
        #
        term_filepath = os.path.join(dir, outfilestem+'_terms.tsv')
        logger.debug('writing unique terms and counts to %s', term_filepath)
        sort_arr = np.argsort(freqs)
        pd.DataFrame({'count':freqs[sort_arr],
                      'score':mean_scores[sort_arr]},
                     index=[i.decode('UTF-8') for i in unique_terms[sort_arr]],
                     ).to_csv(term_filepath,
                              sep='\t',
                              float_format='%.2f')
        del sort_arr
        # histograms
        frequency_and_score_histograms(freqs, mean_scores, dir, outfilestem)


@cli.command()
@click.option('--cutoff', default=DEFAULT_MAX_SCORE, show_default=True,
              help='Maximum simplicity score to keep.')
@click.argument('infilestem', type=str)
@click.argument('outfilestem', type=str)
@log_elapsed_time()
def filter_peptide_terms(cutoff, infilestem, outfilestem):
    '''Removes high-simplicity terms.

    '''
    global config_obj
    dir = config_obj.config_dict['summary']['dir']
    # argument inputs
    logger.debug('Input file stem is "%s".', infilestem)
    logger.debug('Output file stem is "%s".', outfilestem)
    logger.info('Minimum simplicity value is %0.2f.', cutoff)
    #
    # Read input terms from merged set
    #
    infilepath = os.path.join(dir, infilestem+'_terms.tsv')
    logger.debug('Filtering file "%s".', infilepath)
    if not os.path.exists(infilepath):
        logger.error('input file "%s" does not exist.', infilepath)
        sys.exit(1)
    term_frame = pd.DataFrame().from_csv(infilepath, sep='\t')
    n_intersecting_terms = len(term_frame)
    k = len(term_frame.index[0])
    logger.info('   %d %d-mer terms initially.', n_intersecting_terms,
                k)
    #
    # drop terms that don't meet cutoff
    #
    term_frame.drop(term_frame[term_frame['score'] > cutoff].index,
                      inplace=True)
    n_scored_terms = len(term_frame)
    logger.info('   %s terms passing cutoff, representing',
                locale.format('%d', n_scored_terms, grouping=True))
    logger.info('       %.2f%% of %s intersecting terms, and',
                n_scored_terms * 100. / n_intersecting_terms,
                locale.format("%d", n_intersecting_terms, grouping=True))
    logger.info('       %.6f%% of possible %d-mers.',
                n_scored_terms * 100. / (ALPHABETSIZE ** k), k)
    #
    # write frequency and score histograms
    frequency_and_score_histograms(term_frame['count'],
                                   term_frame['score'],
                                   dir,
                                   outfilestem)
    #
    # write terms
    #
    term_frame.sort_values(by=['max_count', 'intersections'], inplace=True)
    term_filepath = os.path.join(dir, outfilestem + '_terms.tsv')
    logger.debug('Writing merged terms to "%s".', term_filepath)
    term_frame.to_csv(term_filepath, sep='\t',
                        float_format='%0.2f')
    #
    # calculate histogram of intersections
    #
    intersection_histogram(term_frame, dir, outfilestem,
                           config_obj.config_dict['plot_type'],
                           max(term_frame['intersections']), k)


@cli.command()
@click.argument('filestem', type=str)
@click.argument('setlist', nargs=-1, type=DATA_SET_VALIDATOR)
@log_elapsed_time()
def intersect_peptide_terms(filestem, setlist):
    '''Find intersecting terms from multiple sets.

    :param filestem: input and output filename less '_terms.tsv'
    :param setlist:
    :return:
    '''
    #
    # get configuration inputs
    #
    global config_obj
    outdir = config_obj.config_dict['summary']['dir']
    if not os.path.exists(outdir) and not os.path.isdir(outdir):
        logger.info('Making summary directory %s', outdir)
        os.makedirs(outdir)
    #
    # get argument inputs
    #
    infilename = filestem+'_terms.tsv'
    logger.info('Input filenames will be "%s".', infilename)
    setlist = DATA_SET_VALIDATOR.multiple_or_empty_set(setlist)
    n_sets = len(setlist)
    logger.info('Joining terms from %d sets:', n_sets)
    #
    # read and merge the term_lists
    #
    merged_frame = None
    n_terms_total = 0
    for calc_set in setlist:
        dir = config_obj.config_dict[calc_set]['dir']
        infilepath = os.path.join(dir, infilename)
        if not os.path.exists(infilepath):
            logger.error('input file "%s" does not exist.', infilepath)
            sys.exit(1)
        working_frame = pd.DataFrame.from_csv(infilepath,
                                              sep='\t',
                                              index_col=0)
        n_terms_set = len(working_frame)
        n_terms_total += n_terms_set
        if merged_frame is None:    # first one read
            merged_frame = pd.DataFrame({'intersections': [1]*n_terms_set,
                                         'count': working_frame['count'],
                                         'max_count': working_frame['count'],
                                         'score': working_frame['score']*working_frame['count']},
                                        index=working_frame.index,
                                        columns=('intersections', 'count', 'max_count', 'score')
                                        )
        else: # join this frame
            working_frame.rename(columns={'count':'working_count',
                                          'score':'working_score'},
                                 inplace=True)
            merged_frame = merged_frame.join(working_frame)
            del working_frame
            merged_frame = merged_frame.fillna(0)
            merged_frame['count'] += merged_frame['working_count']
            merged_frame['max_count'] = merged_frame[['max_count','working_count']].max(axis=1)
            merged_frame['score'] += merged_frame['working_score']* merged_frame['working_count']
            merged_frame['intersections'] += (merged_frame['working_count'] > 0).astype(np.int)
            del merged_frame['working_count']
            del merged_frame['working_score']
        n_unique_terms = len(merged_frame)
        logger.info('   %s: %s terms in (%.0f%% of %s unique, %.0f%% of %s total read)',
                    calc_set,
                    locale.format("%d", n_terms_set, grouping=True),
                    100.*n_terms_set/n_unique_terms,
                    locale.format("%d", n_unique_terms, grouping=True),
                    100.*n_terms_set/n_terms_total,
                    locale.format('%d', n_terms_total, grouping=True))
    k = len(merged_frame.index[0])
    logger.info('%s unique %d-mers (%0.1f%% of %s total in).',
                locale.format("%d", n_unique_terms, grouping=True),
                k,
                100.*n_unique_terms/n_terms_total,
                locale.format('%d', n_terms_total, grouping=True))
    #
    # drop terms that don't intersect in two sets
    #
    merged_frame.drop(merged_frame[merged_frame['intersections'] == 1].index,
                      inplace=True)
    n_intersecting_terms = len(merged_frame)
    logger.info('%s intersecting terms (%.1f%% of unique).',
                locale.format('%d', n_intersecting_terms, grouping=True),
                100.*n_intersecting_terms/n_unique_terms)
    #
    # clean up and normazlize
    #
    merged_frame['count'] = merged_frame['count'].astype(np.int32)
    merged_frame['max_count'] = merged_frame['max_count'].astype(np.int32)
    merged_frame['score'] = merged_frame['score']/merged_frame['count']
    #
    # calculate frequency and score histograms
    #
    frequency_and_score_histograms(merged_frame['count'],
                                   merged_frame['score'],
                                   outdir,
                                   filestem)
    #
    # write terms
    #
    merged_frame.sort_values(by=['max_count', 'intersections'], inplace=True)
    term_filepath = os.path.join(outdir, filestem+'_terms.tsv')
    logger.debug('Writing merged terms to "%s".', term_filepath)
    merged_frame.to_csv(term_filepath, sep='\t',
                        float_format='%0.2f')
    #
    # calculate histogram of intersections
    #
    intersection_histogram(merged_frame, outdir, filestem,
                           config_obj.config_dict['plot_type'],
                           n_sets, k)


@cli.command()
@click.option('--cutoff', default=DEFAULT_SIMPLICITY_CUTOFF, help='Minimum simplicity level to unmask.')
@click.option('--plot/--no-plot', default=False, help='Plot histogram of mask fraction.')
@click.argument('infilename', type=str)
@click.argument('outfilestem', type=str)
@click.argument('setlist', nargs=-1, type=DATA_SET_VALIDATOR)
def peptide_simplicity_mask(cutoff, plot, infilename, outfilestem, setlist):
    '''Lower-case high-simplicity regions in FASTA.

    :param infilename: Name of input FASTA files for every directory in setlist.
    :param outfilestem: Stem of output filenames.
    :param cutoff: Minimum simplicity level to unmask.
    :param plot: If specified, make a histogram of masked fraction.
    :param setlist: List of defined sets to iterate over.
    :return:

    Note that this calculation is single-threaded and may be time-consuming, so
    starting multiple processes may be a good idea.
    '''
    global config_obj
    user_ctx = get_user_context_obj()
    setlist = DATA_SET_VALIDATOR.multiple_or_empty_set(setlist)
    simplicity_obj = user_ctx['simplicity_object']
    simplicity_obj.set_cutoff(cutoff)
    logger.info('Simplicity function is %s with cutoff of %d.',
                simplicity_obj.desc, cutoff)
    logger.debug('Reading from FASTA file "%s".', infilename)
    instem, ext = os.path.splitext(infilename)
    outfilename = outfilestem + ext
    logger.debug('Output FASTA file name is "%s".', outfilename)
    histfilename = outfilestem + '-hist.tsv'
    logger.debug('Output histogram file is "%s".', histfilename)
    if plot:
        plotname = outfilestem + '.' + config_obj.config_dict['plot_type']
        logger.debug('Plot to file "%s".', plotname)
    for calc_set in setlist:
        dir = config_obj.config_dict[calc_set]['dir']
        inpath = os.path.join(dir, infilename)
        outpath = os.path.join(dir, outfilename)
        shutil.copy(inpath, outpath)
        fasta  = pyfaidx.Fasta(outpath, mutable=True)
        percent_masked_list = []
        if user_ctx['first_n']:
            keys = list(fasta.keys())[:user_ctx['first_n']]
        else:
            keys = fasta.keys()
        if user_ctx['progress']:
            with click.progressbar(keys, label='%s genes processed' %calc_set,
                                   length=len(keys)) as bar:
                for key in bar:
                    masked_gene = simplicity_obj.mask(fasta[key])
                    percent_masked = 100.*num_masked(masked_gene)/len(masked_gene)
                    percent_masked_list.append(percent_masked)
        else:
            for key in keys:
                masked_gene = simplicity_obj.mask(fasta[key])
                percent_masked = 100.*num_masked(masked_gene)/len(masked_gene)
                percent_masked_list.append(percent_masked)
        fasta.close()
        #
        # histogram masked regions
        #
        (hist, bins) = np.histogram(percent_masked_list, bins=np.arange(0.,100.,100./NUM_HISTOGRAM_BINS))
        bin_centers = (bins[:-1] + bins[1:])/2.
        hist = hist*100./len(percent_masked_list)
        hist_filepath = os.path.join(dir, histfilename)
        logger.debug('writing histogram to file "%s".', hist_filepath)
        pd.Series(hist, index=bin_centers).to_csv(hist_filepath, sep='\t',
                                                  float_format='%.3f')
        #
        # plot histogram, if requested
        #
        if plot:
            plotpath = os.path.join(dir, plotname)
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(bin_centers, hist)
            plt.title('Peptide %s Simplicity Distribution with Cutoff %d'%(simplicity_obj.label.capitalize()
                                                                           ,cutoff))
            plt.xlabel('Percent of Peptide Sequence Masked')
            plt.ylabel('Percent of Peptide Sequences')
            plt.savefig(plotpath)

@cli.command()
@click.option('--force/--no-force', default=False, help='Force copy into non-empty directory.')
def install_demo_scripts(force):
    """Copy demo scripts to the working directory.

    :return:
    """
    if not force:
        files = os.listdir()
        try:
            files.remove('logs')
        except ValueError:
            pass
        if len(files) >0:
            logger.error('Current working directory is not empty.  Use --force to copy anyway.')
            sys.exit(1)
    example_files = pkg_resources.resource_listdir('aakbar', 'examples')
    for file in example_files:
        shutil.copyfile(pkg_resources.resource_filename('aakbar', os.path.join('examples', file)),
                        file)
        if file.endswith('.sh'): # set .sh files as executable
            os.chmod(file, os.stat(file).st_mode| stat.S_IEXEC)
            logger.debug('Created executable file "%s".', file)
        else:
            logger.debug('Created file "%s".', file)
    # print README
    readme = to_str(pkg_resources.resource_string('aakbar', os.path.join('examples', 'README.txt')))
    print(readme)


