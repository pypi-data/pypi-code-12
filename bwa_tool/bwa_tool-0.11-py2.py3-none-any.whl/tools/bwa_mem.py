import getpass
import json
import os
import sys

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

def get_readgroup_str(readgroup_json_path, logger):
    json_data=open(readgroup_json_path).read()
    data = json.loads(json_data)
    data_list = [k + ':' + v for k,v in data.items()]
    data_str = '\\t'.join(sorted(data_list)) # use \\t, so \t appears in @PG, and the @PG doesn't think there are 2 ID keys
    readgroup_str = '@RG\\t' + data_str
    return readgroup_str

def bwa_mem(uuid, fastq1_path, fastq2_path, reference_fasta_path, readgroup_json_path, thread_count, engine, logger):
    step_dir = os.getcwd()
    fastq1_name = os.path.basename(fastq1_path)

    if fastq1_name.endswith('_1.fq.gz'):
        fastqbase_name = fastq1_name.replace('_1.fq.gz', '')
    elif fastq1_name.endswith('_1.fq'):
        fastqbase_name = fastq1_name.replace('_1.fq', '')
    else:
        logger.debug('unrecognized fastq file: %s' % fastq1_name)
        sys.exit(1)

    outbam = fastqbase_name + '.bam'
    
    rg_str = get_readgroup_str(readgroup_json_path, logger)

    home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
    bwa_path = os.path.join(home_dir, '.local', 'bin', 'bwa')
    bwa_cmd = [bwa_path, 'mem', '-t ' + str(thread_count), '-T', '0', '-R ' + '"' + rg_str + '"', reference_fasta_path,
               '"' + fastq1_path + '"' , '"' + fastq2_path + '"']
    samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')
    samtools_cmd = [samtools_path, 'view', '-Shb', '-o', '"' + outbam + '"', '-']
    shell_bwa_cmd = ' '.join(bwa_cmd)
    shell_samtools_cmd = ' '.join(samtools_cmd)
    shell_cmd = shell_bwa_cmd + ' | ' + shell_samtools_cmd
    output = pipe_util.do_shell_command(shell_cmd, logger)

    
    df = time_util.store_time(uuid, shell_cmd, output, logger)
    df['bam'] = outbam
    reference_fasta = os.path.basename(reference_fasta_path)
    df['reference_fasta'] = reference_fasta
    df['thread_count'] = thread_count
    unique_key_dict = {'uuid': uuid, 'bam': outbam, 'reference_fasta': reference_fasta,
                       'thread_count': thread_count}
    table_name = 'time_mem_bwa_mem_pe'
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    
    return
