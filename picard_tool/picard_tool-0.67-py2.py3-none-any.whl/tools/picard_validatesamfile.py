import os
import getpass
import logging
import sys
from collections import defaultdict

import pandas as pd

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def store_validate_error(uuid, bam_name, validate_file, engine, logger):
    val_error_dict = defaultdict(dict)
    with open(validate_file, 'r') as validate_file_open:
        for line in validate_file_open:
            if line.startswith('ERROR:'):
                validation_type = 'ERROR'
                line_split = line.strip().split(',')
                if len(line_split) == 4:
                    line_error = line_split[2:]
                    line_error = ', '.join(line_error)
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 3:
                    line_error = line_split[2]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 2:
                    line_error = line_split[1]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 1:
                    line_error = line_split[0]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                else:
                    logger.debug('validation_type=ERROR')
                    logger.debug('line: %s' % line)
                    logger.debug('Need to handle this comma amount: %s' % len(line_split))
                    sys.exit(1)
            elif line.startswith('WARNING:'):
                validation_type = 'WARNING'
                line_split = line.strip().split(',')
                if len(line_split) == 4:
                    line_error = line_split[2:]
                    line_error = ', '.join(line_error)
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 3:
                    line_error = line_split[2]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 2:
                    line_error = line_split[1].strip()
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 1:
                    line_error = line_split[0]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                else:
                    logger.debug('validation_type=WARNING')
                    logger.debug('line: %s' % line)
                    logger.debug('Need to handle this comma amount: %s' % len(line_split))
                    sys.exit(1)
            elif line.startswith('No errors found'):
                validation_type = 'PASS'
                line_error = line.strip()
                val_error_dict[validation_type][line_error] = 1
            else:
                logger.info('unknown picard validation line')
                logger.info('line=%s' % line)
                sys.exit(1)

    validation_type = 'ERROR'
    for akey in sorted(val_error_dict[validation_type].keys()):
        store_dict = dict()
        store_dict['value'] = akey
        store_dict['count'] = val_error_dict[validation_type][akey]
        store_dict['uuid'] = [uuid]  # a non scalar
        store_dict['bam_name'] = bam_name
        store_dict['severity'] = validation_type
        logger.info('store_validate_error() store_dict=%s' % store_dict)
        df = pd.DataFrame(store_dict)
        table_name = 'picard_ValidateSamFile'
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name, 'error': akey}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    validation_type = 'WARNING'
    for akey in sorted(val_error_dict[validation_type].keys()):
        store_dict = dict()
        store_dict['value'] = akey
        store_dict['count'] = val_error_dict[validation_type][akey]
        store_dict['uuid'] = [uuid]  # a non scalar
        store_dict['bam_name'] = bam_name
        store_dict['severity'] = validation_type
        logger.info('store_validate_error() store_dict=%s' % store_dict)
        df = pd.DataFrame(store_dict)
        table_name = 'picard_ValidateSamFile'
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name, 'error': akey}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    validation_type = 'PASS'
    for akey in sorted(val_error_dict[validation_type].keys()):
        store_dict = dict()
        store_dict['value'] = akey
        store_dict['count'] = val_error_dict[validation_type][akey]
        store_dict['uuid'] = [uuid]  # a non scalar
        store_dict['bam_name'] = bam_name
        store_dict['severity'] = validation_type
        logger.info('store_validate_error() store_dict=%s' % store_dict)
        df = pd.DataFrame(store_dict)
        table_name = 'picard_ValidateSamFile'
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name, 'error': akey}
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    return

                    
def picard_validatesamfile(uuid, bam_path, input_state, engine, logger):
    step_dir = os.getcwd()
    home_dir = os.path.join('home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
    bam_name = os.path.basename(bam_path)
    validate_file = bam_name + '.validate'

    if pipe_util.already_step(step_dir, 'validate', logger):
        logger.info('already completed step `validate` of: %s' % bam_name)
    else:
        logger.info('running step validate of: %s' % bam_name)
        mo = int((2 ** 32) / 2) - 1
        
        cmd = ['java', '-Djava.io.tmpdir='+step_dir, '-d64', '-jar', os.path.join(home_dir, 'tools/picard-tools/picard.jar'), 'ValidateSamFile', 'MO=' + str(mo), 'INPUT=' + bam_path, 'OUTPUT=' + validate_file, 'VALIDATION_STRINGENCY=LENIENT', 'TMP_DIR='+step_dir]
        output = pipe_util.do_command(cmd, logger, allow_fail=True)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_picard_ValidateSamFile'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        logger.info('completed running step validate of: %s' % bam_name)
        pipe_util.create_already_step(step_dir, 'validate', logger)

    if pipe_util.already_step(step_dir, 'validate_db', logger):
        logger.info('alread stored `picard validate` to db')
    else:
        logger.info('storing `picard validate` to db')
        store_validate_error(uuid, bam_name, validate_file, engine, logger)
        pipe_util.create_already_step(step_dir, 'validate_db', logger)
        logger.info('completed storing `picard validate` to db')
    return
