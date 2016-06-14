import getpass
import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def picard_collectsequencingartifactmetrics(uuid, bam_path, db_snp_path, input_state, engine, logger):
    step_dir = os.getcwd()
    bam_name = os.path.basename(bam_path)
    bam_base, bam_ext = os.path.splitext(bam_name)
    if pipe_util.already_step(step_dir, bam_base + '_CollectSequencingArtifactMetrics', logger):
        logger.info('already completed step `picard CollectSequencingArtifactMetrics` of: %s' % bam_name)
    else:
        logger.info('running step `picard CollectSequencingArtifactMetrics` of: %s' % bam_name)
        home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
        cmd = ['java', '-d64', '-jar', os.path.join(home_dir, 'tools/picard-tools/picard.jar'), 'CollectSequencingArtifactMetrics', 'INPUT=' + bam_path, 'OUTPUT=artifact_metrics.txt', 'DB_SNP='+ db_snp_path, 'VALIDATION_STRINGENCY=STRICT']
        output = pipe_util.do_command(cmd, logger)
        df = time_util.store_time(uuid, cmd, output, logger)
        df['bam_name'] = bam_name
        df['input_state'] = input_state
        unique_key_dict = {'uuid': uuid, 'bam_name': bam_name}
        table_name = 'time_mem_picard_collectsequencingartifactmetrics'
        df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
        pipe_util.create_already_step(step_dir, bam_base + '_CollectSequencingArtifactMetrics', logger)
        logger.info('completed running step `picard CollectSequencingArtifactMetrics` of: %s' % bam_name)
    return
