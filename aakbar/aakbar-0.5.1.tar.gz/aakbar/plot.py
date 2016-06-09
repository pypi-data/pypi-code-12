# -*- coding: utf-8 -*-
'''Core commands for aakbar.
'''

# standard library imports
import os
import math
import csv

# external packages
import pandas as pd

# module imports
from .common import *
from . import cli, get_user_context_obj, logger

@cli.command()
@click.argument('filestem', type=str)
@click.argument('setlist', nargs=-1, type=DATA_SET_VALIDATOR)
def find_strict_signatures(filestem, setlist):
    """Signatures in search results that were found in all reference genomes

    :param filestem: Input filestem.
    :param setlist: List of data sets.
    :return:
    """
    global config_obj
    user_ctx = get_user_context_obj()
    if user_ctx['first_n']:
        logger.info('Only first %d records will be used.', user_ctx['first_n'])
        first_n = user_ctx['first_n']
    else:
        first_n = 1E12
    # parameter inputs
    infilename = filestem + '_sigcounts.tsv'
    logger.debug('Input file name is "%s".', infilename)
    setlist = DATA_SET_VALIDATOR.multiple_or_empty_set(setlist)
    #
    # Read input terms from merged set
    #
    intersect_dir = config_obj.config_dict['summary']['dir']
    termfilepath = os.path.join(intersect_dir, filestem+'_terms.tsv')
    logger.debug('Reading terms from file "%s".', termfilepath)
    if not os.path.exists(termfilepath):
        logger.error('input file "%s" does not exist.', termfilepath)
        sys.exit(1)
    term_frame = pd.DataFrame().from_csv(termfilepath, sep='\t')
    del term_frame['score']
    n_terms = len(term_frame)
    k = len(term_frame.index[0])
    n_intersections = max(term_frame['intersections'])
    logger.info('%d %d-mer terms defined.', n_terms,
                k)
    logger.info('Calculating terms for %d data sets:', len(setlist))
    #
    # operate on LCA terms only
    #
    lca_terms = term_frame[term_frame['intersections'] == n_intersections]
    del term_frame
    del lca_terms['intersections']
    n_lca_terms = len(lca_terms)
    logger.info('%d LCA terms in signature set.', n_lca_terms)
    logger.info('Maximum number of intersections is %d.', n_intersections)
    #
    # loop on sets
    #
    for calc_set in setlist:
        logger.info('set %s:', calc_set)
        dir = config_obj.config_dict[calc_set]['dir']
        infilepath = os.path.join(dir, infilename)
        if not os.path.exists(infilepath):
            logger.error('Input file "%s" does not exist.', infilepath)
            sys.exit(1)
        sig_frame = pd.read_csv(infilepath,
                                usecols=[0, 'counts'],
                                index_col=0,
                                sep='\t')
        n_sigs = 0
        n_lca_sigs = 0
        sigs_in_lca = set()
        for sig in sig_frame.index:
            if sig in lca_terms.index:
                sigs_in_lca.add(sig)
                n_lca_sigs += 1
                #my_lca_counts.loc[sig] = sig_frame.loc[sig]['counts']
                #term_stats = lca_terms.loc[sig]
                #logger.info(sig_frame.loc[sig]['counts'])
            if n_sigs > first_n:
                break
            n_sigs += 1
        bins = [1,2,3,4,5,6,7,8,
                10,12,14,16,
                20,24,28,32,
                40,48,56,64,
                80,96,112,128,
                160,192,224,256]
        lastbin = 0
        #
        # Fraction found historam initialization
        #
        fractionfoundpath = os.path.join(dir, filestem + '_fractionfound.tsv')
        fractionfoundfh = open(fractionfoundpath, 'wt')
        fractionfoundwriter = csv.DictWriter(fractionfoundfh,
                                            fieldnames=['bin',
                                                        'n_found',
                                                        'found_percent',
                                                        'sigma_percent'],
                                            delimiter='\t')
        fractionfoundwriter.writeheader()
        #
        # Missing list initialization
        #
        missinglistpath = os.path.join(dir, filestem + '_missingsigs.tsv')
        missinglistfh = open(missinglistpath, 'wt')
        missinglistwriter = csv.DictWriter(missinglistfh,
                                            fieldnames=['signature',
                                                        'avg_count',
                                                        'max_count'],
                                            delimiter='\t')
        missinglistwriter.writeheader()
        #
        logger.info('   bin\tLCAsigs\tfraction\t+/-')
        for i in range(len(bins)):
            nextbin = bins[i]
            inrange = lca_terms[lca_terms['max_count'].isin([lastbin,nextbin])].index
            rangeset = set([term for term in inrange])
            n_terms_in_bin = len(rangeset)
            if n_terms_in_bin == 0:
                continue
            sigs_in_range = rangeset.intersection(sigs_in_lca)
            for missing in rangeset.difference(sigs_in_lca):
                missinglistwriter.writerow({
                    'signature': missing,
                    'avg_count': lca_terms.loc[missing]['count']/float(n_intersections),
                    'max_count': lca_terms.loc[missing]['max_count']
                })
            n_sigs_in_bin = len(sigs_in_range)
            fraction_found = 100.*n_sigs_in_bin/n_terms_in_bin
            sigma = math.sqrt(n_sigs_in_bin)
            sigma_percent = 100.*sigma/n_terms_in_bin
            logger.info('   %d: %d\t%.1f\t%.1f',
                        nextbin,
                        n_sigs_in_bin,
                        fraction_found,
                        sigma_percent)
            fractionfoundwriter.writerow({
                'bin': nextbin,
                'n_found': n_sigs_in_bin,
                'found_percent': fraction_found,
                'sigma_percent': sigma_percent
            })
            lastbin = nextbin
        logger.info('   %d (%.1f%% of overall) LCA sigs in %s.',
                    n_lca_sigs,
                    n_lca_sigs * 100. / n_lca_terms,
                    calc_set)
        fractionfoundfh.close()
        missinglistfh.close()




