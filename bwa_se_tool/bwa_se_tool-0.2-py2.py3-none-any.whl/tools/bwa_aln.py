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

def bwa_aln(uuid, fastq_path, fastq_encoding, reference_fasta_path, readgroup_json_path, thread_count, engine, logger):
    step_dir = os.getcwd()
    fastq_name = os.path.basename(fastq_path)
    reference_fasta = os.path.basename(reference_fasta_path)
    
    if fastq_name.endswith('_s.fq.gz'):
        fastqbase_name = fastq_name.replace('_s.fq.gz', '')
    elif fastq_name.endswith('_s.fq'):
        fastqbase_name = fastq_name.replace('_s.fq', '')
    elif fastq_name.endswith('_o1.fq.gz'):
        fastqbase_name = fastq_name.replace('_o1.fq.gz', '')
    elif fastq_name.endswith('_o1.fq'):
        fastqbase_name = fastq_name.replace('_o1.fq', '')
    elif fastq_name.endswith('_o2.fq.gz'):
        fastqbase_name = fastq_name.replace('_o2.fq.gz', '')
    elif fastq_name.endswith('_o2.fq'):
        fastqbase_name = fastq_name.replace('_o2.fq', '')
    else:
        logger.debug('unrecognized fastq file: %s' % fastq_name)
        sys.exit(1)

    outbam = fastqbase_name + '.bam'
    sai_name = fastqbase_name + '.sai'

    home_dir = os.path.join('/home', getpass.getuser()) #cwltool sets HOME to /var/spool/cwl, so need to be explicit
    bwa_path = os.path.join(home_dir, '.local', 'bin', 'bwa')

    #sai1
    aln_frontend = [bwa_path, 'aln', reference_fasta_path, '-t ' + str(thread_count), '"' + fastq_path + '"']
    if fastq_encoding == 'Illumina-1.3' or fastq_encoding == 'Illumina 1.5':
        logger.info('%s is fastq_encoding, so use `bwa aln -I`' % fastq_encoding)
        bwa_frontend.insert(3, '-I')
    aln_backend = [  ' > ', '"' + sai_name + '"' ]
    aln_cmd = aln_frontend + aln_backend
    shell_cmd = ' '.join(aln_cmd)
    output = pipe_util.do_shell_command(shell_cmd, logger)
    #store time/mem
    df = time_util.store_time(uuid, shell_cmd, output, logger)
    df['sai'] = sai_name
    df['fastq'] = fastq_name
    df['reference_fasta_name'] = reference_fasta_name
    df['thread_count'] = thread_count
    unique_key_dict = {'uuid': uuid, 'sai_name': sai_name, 'reference_fasta_name': reference_fasta_name,
                       'thread_count': thread_count}
    table_name = 'time_mem_bwa_aln'
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

    #samse
    rg_str = get_readgroup_str(readgroup_json_path, logger)
    if rg_str is None:
        bwa_cmd = [bwa_path, 'samse', reference_fasta_path, sai_name, '"' + fastq_path + '"' ]
    else:
        bwa_cmd = [bwa_path, 'sampe', '-r ' + '"' + rg_str + '"', reference_fasta_path, '"' + sai_name + '"' , 
                   '"' + fastq_path + '"' ]
    samtools_path = os.path.join(home_dir, '.local', 'bin', 'samtools')
    samtools_cmd = [samtools_path, 'view', '-Shb', '-o', '"' + outbam + '"', '-']
    shell_bwa_cmd = ' '.join(bwa_cmd)
    shell_samtools_cmd = ' '.join(samtools_cmd)
    shell_cmd = shell_bwa_cmd + ' | ' + shell_samtools_cmd
    output = pipe_util.do_shell_command(shell_cmd, logger)
    #store time/mem
    df = time_util.store_time(uuid, shell_cmd, output, logger)
    df['bam'] = outbam
    df['fastq'] = fastq_name
    df['reference_fasta_name'] = reference_fasta_name
    df['thread_count'] = thread_count
    unique_key_dict = {'uuid': uuid, 'bam': outbam, 'reference_fasta': reference_fasta,
                       'thread_count': thread_count}
    table_name = 'time_mem_bwa_sampe'
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    
    return
