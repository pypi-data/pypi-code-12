from __future__ import absolute_import
from celery.utils.log import get_task_logger
from celery.signals import after_setup_task_logger

from gwaportalpipeline.celery import celery
from gwaportalpipeline.common import *
from gwaportalpipeline import utils
from gwaportalpipeline import permute

from pygwas.core import genotype

import bisect
import numpy
import h5py
import os
import operator
import logging

logger = get_task_logger(__name__)

@after_setup_task_logger.connect
def setup_task_logger(**kwargs):
    ph = CeleryProgressLogHandler(candidate_gene_list_enrichment)
    logger.addHandler(ph)       


@celery.task(serialiazer='json')
def candidate_gene_list_enrichment(candidate_gene_list_id,study_id,genotypeid,windowSize,numberOfPermutations,top_snp_count):
    pval_file = None
    pval = None
    try:
        logger.info('Retrieving candidate gene list',extra={'progress':2})
        candidate_genes = restclient.get_candidate_genes(candidate_gene_list_id)
        if len(candidate_genes) == 0:
            raise Exception('No genes found in candidate gene list') 
        logger.info('Retrieve HDF5 File')
        pval_file = restclient.download_study_file(study_id,LOCAL_DATA_FOLDER)
        logger.info('Retrieve genotype')
        genotypeData = _load_genotype_(GENOTYPE_FOLDER,genotypeid) 
        chr_regions = genotypeData.chr_regions
        chr_pos_list= zip(genotypeData.chromosomes,genotypeData.positions)
        pval = _candidate_gene_list_enrichment(candidate_genes,pval_file,chr_pos_list,chr_regions,windowSize,numberOfPermutations,top_snp_count)
    except Exception,err:
        logger.exception(err)
        raise err
    finally:
        if pval_file is not  None:
            os.unlink(pval_file)
    return {'pvalue':pval}


def _candidate_gene_list_enrichment(candidate_genes,pval_file,pos_chr_list,chr_regions,windowSize,numberOfPermutations,TOP_SNP_LIMIT):
    pos_chr_list = numpy.asarray(pos_chr_list)
    logger.info('Retrieve %s TOP GWAS SNPs' % TOP_SNP_LIMIT)
    top_snps = utils.get_top_snps(pval_file,TOP_SNP_LIMIT)
    logger.info('Retrieve TOP SNP Matrix')
    top_snps_matrix = _get_snps_snps_matrix(pos_chr_list,top_snps,chr_regions)
    logger.info('Retrieve Gene Matrix (windowsize:%s)' % windowSize)
    candidate_gene_matrix = _get_gene_snps_matrix(pos_chr_list,candidate_genes,chr_regions,windowSize)
    per = permute.permute()
    per.load_vectors(candidate_gene_matrix,top_snps_matrix)
    logger.info('Starting permutation test (#: %s)' % numberOfPermutations,extra={'progress':5})
    pval = per.permute_p_val(numberOfPermutations)
    logger.info('Finished permutation test',extra={'progress':95})
    return pval


def _get_snps_snps_matrix(snps,top_snps,chr_regions):
    # sort by chr and position
    #use lexsort
    top_snps.sort(order=['chr','position'])
    chr_start = 0
    chr_start_ix = 0
    indices = []
    vector = numpy.zeros((len(snps),),dtype='int32')
    for snp in top_snps:
        chr = int(snp[0])
        if chr != chr_start:
            chr_start = chr
            chr_start_ix = chr_regions[chr-1][0]
            chr_end_ix = chr_regions[chr-1][1]
        indices.append(chr_start_ix + snps[chr_start_ix:chr_end_ix][:,1].searchsorted(snp[1]))
    vector[indices] = 1
    return vector

def _get_gene_snps_matrix(snps,genes,chr_regions,windowsize):
    # sort by gene name and first position
    sorted_genes = sorted(genes, key=operator.itemgetter(3, 0))
    chr_start = 0
    chr_start_ix = 0
    indices = []
    vector = numpy.zeros((len(snps),),dtype='int32')
    for gene in sorted_genes:
        chr = int(gene[3][2])
        if chr != chr_start:
            chr_start = chr
            chr_start_ix = chr_regions[chr-1][0]
            chr_end_ix = chr_regions[chr-1][1]
        ix_start = chr_start_ix+ snps[chr_start_ix:chr_end_ix][:,1].searchsorted(gene[0]-windowsize,side='left')
        ix_end = chr_start_ix + snps[chr_start_ix:chr_end_ix][:,1].searchsorted(gene[1]+windowsize,side='right')
        vector[ix_start:ix_end] = 1
    return vector



def _load_genotype_(folder,genotype_id):
    data_format = 'binary'
    file_prefix = os.path.join(folder,str(genotype_id))

    hdf5_file = os.path.join(file_prefix,'all_chromosomes_%s.hdf5' % data_format)
    if os.path.isfile(hdf5_file):
        return genotype.load_hdf5_genotype_data(hdf5_file)
    raise Exception('No Genotype files in %s folder were found.' % file_prefix)



