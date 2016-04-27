from __future__ import absolute_import
from celery.utils.log import get_task_logger
from celery.signals import after_setup_task_logger
from gwaportalpipeline.celery import celery

from gwaportalpipeline.common import *

from pygwas import pygwas

import tempfile
import os 
import logging 
import ConfigParser
import shutil
import requests
import itertools
import tempfile




logger = get_task_logger(__name__)
pygwas_logger = logging.getLogger('pygwas')




@after_setup_task_logger.connect
def setup_task_logger(**kwargs):
    ph = CeleryProgressLogHandler(run_gwas)
    logging.getLogger('pygwas').addHandler(ph)
    logger.addHandler(ph)       


@celery.task(serializer='json')
def run_gwas(studyid):
    # create folders
    fh = None
    retval = {'status':'OK','studyid':studyid}
    base_folder = None
    try:
        base_folder = os.path.join(LOCAL_DATA_FOLDER,str(studyid))
        input_folder=  os.path.join(base_folder,'INPUT')
        output_folder = os.path.join(base_folder,'OUTPUT')
        log_folder = os.path.join(base_folder,'LOG')
        log_file = os.path.join(log_folder,'%s.log' % studyid)
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        hdf5_file = os.path.join(output_folder,'%s.hdf5' % studyid)
        fh = logging.FileHandler(log_file,'w')
        fh.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        logger.addHandler(fh)
        pygwas_logger.addHandler(fh)
        logger.info('Start GWAS for studyid %s, job: %s' % (studyid,studyid),extra={'progress':0})
        # get studydata (phenotypes, gentoype, etc) 
        phenotype_file = os.path.join(input_folder,'%s.csv'% studyid)
        data = restclient.get_phenotype_data(studyid)
        method = data['analysisMethod']
        genotype = data['genotype']
        phenotype_data = data['csvData']
        transformation = data['transformation']
        with open(phenotype_file,'w') as fd:
            fd.write(phenotype_data)
        # perform gwas
        logger.info('Start GWAS analysis',extra={'progress':1})
        genotype_file = '%s/%s' % (GENOTYPE_FOLDER,genotype)
        result = pygwas.perform_gwas(phenotype_file,method.lower(),genotype_file,transformation.lower())
        logger.info('Saving output files',extra={'progress':95})
        result.save_as_hdf5(hdf5_file)
        del result
        # POST hdf5 file 
        logger.info('Finished GWAS analysis..Storing output files',extra={'progress':99})
        restclient.upload_study_file(hdf5_file,studyid)
    except Exception,err:
        logger.exception(err)
        retval = {'status':'ERROR','statustext':str(err)}
        raise err
    finally: 
        if fh is not None:
            fh.close()
            logger.removeHandler(fh)
            pygwas_logger.removeHandler(fh)
        if base_folder is not None and retval['status'] == 'OK':
            shutil.rmtree(base_folder,ignore_errors=True)
    return retval   
