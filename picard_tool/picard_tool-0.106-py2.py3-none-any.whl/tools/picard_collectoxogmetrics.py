import getpass
import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

from tools import picard_util

def picard_collectoxogmetrics(uuid, bam_path, db_snp_path, reference_fasta_path, input_state, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    db_snp_name = os.path.basename(db_snp_path)
    if pipe_util.already_step(step_dir, bam_base + '_CollectOxoGMetrics', logger):
        logger.info('already completed step `picard CollectOxoGMetrics` of: %s' % bam_name)
    else:
        logger.info('running step `picard CollectOxoGMetrics` of: %s' % bam_name)
        stats_path = 'oxoG_metrics.txt'
        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
        cmd = ['java', '-d64', '-jar', os.path.join(home_dir, 'tools/picard-tools/picard.jar'), 'CollectOxoGMetrics', 'INPUT=' + bam_path, 'OUTPUT=' + stats_path, 'DB_SNP='+ db_snp_path, 'REFERENCE_SEQUENCE=' + reference_fasta_path, 'VALIDATION_STRINGENCY=STRICT']
        output = pipe_util.do_command(cmd, logger)

        # save time/mem to db
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        df['db_snp_name'] = db_snp_name
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name, 'input_state': input_state, 'db_snp_name': db_snp_name}
        table_name = 'time_mem_picard_CollectOxoGMetrics'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

        # save stats to db
        table_name = 'picard_CollectOxoGMetrics'
        select = 'SAMPLE_ALIAS'
        df = picard_util.picard_select_tsv_to_df(stats_path, select, logger)
        df['db_snp_name'] = db_snp_name
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        
        pipe_util.create_already_step(step_dir, bam_base + '_CollectOxoGMetrics', logger)
        logger.info('completed running step `picard CollectOxoGMetrics` of: %s' % bam_name)
    return
