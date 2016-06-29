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
    if len(data_list) == 0: ## NEED TO TEST
        return None
    data_str = '\\t'.join(sorted(data_list)) # use \\t, so \t appears in @PG, and the @PG doesn't think there are 2 ID keys
    readgroup_str = '@RG\\t' + data_str
    return readgroup_str

def bwa_aln(uuid, fastq1_path, fastq2_path, fastq_encoding, reference_fasta_path, readgroup_json_path, thread_count, engine, logger):
    step_dir = os.getcwd()
    fastq1_name = os.path.basename(fastq1_path)
    fastq2_name = os.path.basename(fastq2_path)
    reference_fasta = os.path.basename(reference_fasta_path)
    
    if fastq1_name.endswith('_1.fq.gz'):
        fastqbase_name = fastq1_name.replace('_1.fq.gz', '')
    elif fastq1_name.endswith('_1.fq'):
        fastqbase_name = fastq1_name.replace('_1.fq', '')
    else:
        logger.debug('unrecognized fastq file: %s' % fastq1_name)
        sys.exit(1)

    outbam = fastqbase_name + '.bam'
    sai1_name = fastqbase_name + '_1.sai'
    sai2_name = fastqbase_name + '_2.sai'

    home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
    bwa_path = os.path.join(home_dir, '.local', 'bin', 'bwa')

    #sai1
    aln_frontend = [bwa_path, 'aln', reference_fasta_path, '-t ' + str(thread_count), '"' + fastq1_path + '"']
    if fastq_encoding == 'Illumina-1.3' or fastq_encoding == 'Illumina 1.5':
        logger.info('%s is fastq_encoding, so use `bwa aln -I`' % fastq_encoding)
        bwa_frontend.insert(3, '-I')
    aln_backend = [  ' > ', '"' + sai1_name + '"' ]
    aln_cmd = aln_frontend + aln_backend
    shell_cmd = ' '.join(aln_cmd)
    output = pipe_util.do_shell_command(shell_cmd, logger)
    #store time/mem
    df = time_util.store_time(uuid, shell_cmd, output, logger)
    df['sai_name'] = sai1_name
    df['fastq'] = fastq1_name
    df['reference_fasta'] = reference_fasta
    df['thread_count'] = thread_count
    unique_key_dict = {'uuid': uuid, 'sai_name': sai1_name, 'reference_fasta': reference_fasta,
                       'thread_count': thread_count}
    table_name = 'time_mem_bwa_aln'
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

    #sai2
    aln_frontend = [bwa_path, 'aln', reference_fasta_path, '-t ' + str(thread_count), '"' + fastq2_path + '"']
    if fastq_encoding == 'Illumina-1.3' or fastq_encoding == 'Illumina 1.5':
        logger.info('%s is fastq_encoding, so use `bwa aln -I`' % fastq_encoding)
        bwa_frontend.insert(3, '-I')
    aln_backend = [  ' > ', '"' + sai2_name + '"' ]
    aln_cmd = aln_frontend + aln_backend
    shell_cmd = ' '.join(aln_cmd)
    output = pipe_util.do_shell_command(shell_cmd, logger)
    #store time/mem
    df = time_util.store_time(uuid, shell_cmd, output, logger)
    df['sai_name'] = sai2_name
    df['fastq'] = fastq2_name
    df['reference_fasta'] = reference_fasta
    df['thread_count'] = thread_count
    unique_key_dict = {'uuid': uuid, 'sai_name': sai2_name, 'reference_fasta': reference_fasta,
                       'thread_count': thread_count}
    table_name = 'time_mem_bwa_aln'
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

    #sampe
    rg_str = get_readgroup_str(readgroup_json_path, logger)
    if rg_str is None:
        bwa_cmd = [bwa_path, 'sampe', reference_fasta_path, sai1_name, sai2_name, '"' + fastq1_path + '"' , '"' + fastq2_path + '"' ]
    else:
        bwa_cmd = [bwa_path, 'sampe', '-r ' + '"' + rg_str + '"', reference_fasta_path, '"' + sai1_name + '"' , '"' + sai2_name + '"',
                   '"' + fastq1_path + '"' , '"' + fastq2_path + '"']
    samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')
    samtools_cmd = [samtools_path, 'view', '-Shb', '-o', '"' + outbam + '"', '-']
    shell_bwa_cmd = ' '.join(bwa_cmd)
    shell_samtools_cmd = ' '.join(samtools_cmd)
    shell_cmd = shell_bwa_cmd + ' | ' + shell_samtools_cmd
    output = pipe_util.do_shell_command(shell_cmd, logger)
    #store time/mem
    df = time_util.store_time(uuid, shell_cmd, output, logger)
    df['bam'] = outbam
    df['fastq1'] = fastq1_name
    df['fastq2'] = fastq2_name
    df['reference_fasta'] = reference_fasta
    df['thread_count'] = thread_count
    unique_key_dict = {'uuid': uuid, 'bam': outbam, 'reference_fasta': reference_fasta,
                       'thread_count': thread_count}
    table_name = 'time_mem_bwa_sampe'
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    
    return
