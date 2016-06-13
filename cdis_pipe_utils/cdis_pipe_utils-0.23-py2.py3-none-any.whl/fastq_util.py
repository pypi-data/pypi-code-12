import ast
import glob
import os
import re
import subprocess
import sys

import pandas as pd

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def buildpefastqdict(fastqlist):
    pefastq_dict = dict()
    fastq_re = re.compile("(^[a-zA-Z0-9_#'.-]+)_(1).fq.gz")
    for fastq in fastqlist:
        fastq_match = fastq_re.match(fastq)
        if fastq_match is None:
            continue
        if len(fastq_match.groups()) == 2:
            read1 = fastq_match.group()
            read2 = fastq_match.groups()[0] + '_2.fq.gz'
            if read2 in fastqlist:
                pefastq_dict[read1] = read2
            else:
                logger.debug('expected fastq not found: %s' % read2)
                sys.exit(1)
    return pefastq_dict


def buildo1fastqlist(fastqlist):
    ofastq_list = list()
    fastq_re = re.compile("(^[a-zA-Z0-9_#'.-]+)_(o1).fq.gz")
    for fastq in fastqlist:
        fastq_match = fastq_re.match(fastq)
        if fastq_match is None:
            continue
        if len(fastq_match.groups()) == 2:
            oread = fastq_match.group()
            ofastq_list.append(oread)
    return ofastq_list


def buildo2fastqlist(fastqlist):
    ofastq_list = list()
    fastq_re = re.compile("(^[a-zA-Z0-9_#'.-]+)_(o2).fq.gz")
    for fastq in fastqlist:
        fastq_match = fastq_re.match(fastq)
        if fastq_match is None:
            continue
        if len(fastq_match.groups()) == 2:
            oread = fastq_match.group()
            ofastq_list.append(oread)
    return ofastq_list


def buildsefastqlist(fastqlist):
    sefastq_list = list()
    fastq_re = re.compile("(^[a-zA-Z0-9_#'.-]+)_(s).fq.gz")
    for fastq in fastqlist:
        fastq_match = fastq_re.match(fastq)
        if fastq_match is None:
            continue
        if len(fastq_match.groups()) == 2:
            seread = fastq_match.group()
            sefastq_list.append(seread)
    return sefastq_list


def buildfastqlist(adir, logger):
    sorted_fastqlist_file=os.path.join(adir, 'fastqlist.txt')
    if pipe_util.already_step(adir, 'fastqlist', logger):
        logger.info('already completed building fastq list in %s' % adir)
        with open(sorted_fastqlist_file, 'r') as sorted_fastqlist_open:
            sorted_fastqlist_txt = sorted_fastqlist_open.readline()
        sorted_fastqlist =  ast.literal_eval(sorted_fastqlist_txt)
        return sorted_fastqlist
    else:
        logger.info('building fastq list in %s' % adir)
        fastqlist = [os.path.basename(fastq) for fastq in (glob.glob(os.path.join(adir, '*.fq.gz')))]
        sorted_fastqlist = sorted(fastqlist)
        with open(sorted_fastqlist_file, 'w') as sorted_fastqlist_open:
            sorted_fastqlist_open.write(str(sorted_fastqlist))
        pipe_util.create_already_step(adir, 'fastqlist', logger)
        logger.info('completed building fastq list in %s' % adir)
        return sorted_fastqlist


def buildfastq_len_list(adir):
    fastq_len_list = [fastq_path for fastq_path in (glob.glob(os.path.join(adir, '*.fq.gz.len')))]
    return sorted(fastq_len_list)


def get_max_fastq_length(fastq_length_file):
    max_length = 0
    with open(fastq_length_file, 'r') as fastq_length_file_open:
        for line in fastq_length_file_open:
            if int(line.strip()) > max_length:
                max_length = int(line)
    return max_length


def get_maxofmax_fastq_length(fastq_dir, logger):
    fastq_len_list = buildfastq_len_list(fastq_dir)
    max_len = 0
    for fastq_len_file in fastq_len_list:
        with open(fastq_len_file, 'r') as fastq_len_file_open:
            logger.info('fastq_len_file=%s' % fastq_len_file)
            fastq_len_str = fastq_len_file_open.readline().strip()
            if fastq_len_str == '':
                continue
            fastq_len = int(fastq_len_str)
            logger.info('\t fastq_len=%s' % str(fastq_len))
            if fastq_len > max_len:
                max_len = fastq_len
    logger.info('max_len=%s' % str(max_len))
    return max_len

def trimmomatic_log_to_df(uuid, o1read, trimlog_path, logger):
    pass


def get_fastq_length(uuid, fastq_dir, fastq_name, engine, logger):
    fastq_path = os.path.join(fastq_dir, fastq_name)
    fastq_base, fastq_ext = os.path.splitext(fastq_name)
    fastq_length_file = fastq_path + '.len'
    logger.info('fastq_name=%s' % fastq_name)
    logger.info('fastq_path=%s' % fastq_path)
    if pipe_util.already_step(fastq_dir, 'length_' + fastq_base, logger):
        logger.info('already determined length of fastq: %s' % fastq_path)
        sequence_length = get_max_fastq_length(fastq_length_file)
    else:
        logger.info('determining length of fastq: %s' % fastq_path)
        fastq_length_command = "cat " + fastq_path + " | awk '{if(NR%4==2) print length($1)}' | sort | uniq > " + fastq_length_file
        time_cmd = '/usr/bin/time -v ' + fastq_length_command
        proc = subprocess.Popen(time_cmd, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        logger.info('output=%s' % output)
        #df=time_util.store_time(uuid,time_cmd,output,logger)
        #df['fastq_path']=fastq_path
        #table_name='time_mem_fastq_length'
        #unique_key_dict={'uuid':uuid,'fastq_path':fastq_path}
        #df_util.save_df_to_sqlalchemy(df,unique_key_dict,table_name,engine,logger)
        pipe_util.create_already_step(fastq_dir, 'length_' + fastq_base, logger)
        sequence_length = get_max_fastq_length(fastq_length_file)
    return sequence_length

def trimmomatic(uuid, fastq_dir, adapter_pickle_path, thread_count, engine, logger):
    logger.info()
    fastq_list = buildfastqlist(fastq_dir)
    logging.info('fastqlist=%s' % fastq_list)
    pefastqdict = fastq_util.buildpefastqdict(fastq_list)
    logger.info('pefastqdict=%s' % pefastqdict)
    sefastqlist = fastq_util.buildsefastqlist(fastq_list)
    logger.info('sefastqlist=%s' % sefastqlist)
    o1fastqlist = fastq_util.buildo1fastqlist(fastq_list)
    logger.info('o1fastqlist=%s' % o1fastqlist)
    o2fastqlist = fastq_util.buildo2fastqlist(fastq_list)
    logger.info('o2fastqlist=%s' % o2fastqlist)
    trimmomatic_dir = os.path.join(fastq_dir,'trimmomatic')
    step_dir=trimmomatic_dir

    home_dir = os.path.expanduser('~')
    os.makedirs(trimmomatic_dir, exist_ok=True)
    for read1 in sorted(pefastqdict.keys()):
        read1_name, read1_ext = os.path.splitext(read1)
        fq1_in_path = os.path.join(fastq_dir, read1)
        fq2_in_path = os.path.join(fastq_dir, pefastqdict[read1])
        fq1_out_path = os.path.join(trimmomatic_dir, read1)
        fq1_unpaired_path = fq1_out_path + 'UP'
        fq2_out_path = os.path.join(trimmomatic_dir, pefastqdict[read1])
        fq2_unpaired_path = fq2_out_path + 'UP'
        diff1_path = fq1_out_path + '.diff'
        diff2_path = fq2_out_path + '.diff'
        diff1_xz_path = diff1_path + '.xz'
        diff2_xz_path = diff2_path + '.xz'
        diff1_name = os.path.basename(diff1_path)
        diff2_name = os.path.basename(diff2_path)
        fastq_type='PE'
        #generate trim
        if pipe_util.already_step(step_dir, 'trim_pe_' + read1_name, logger):
            logger.info('already completed pe trim on %s' % read1)
        else:
            logger.info('running step PE `trimmomatic` of: %s' % read1)
            trimmomatic_path = os.path.join(home_dir,'tools','trimmomatic','dist','jar','trimmomatic.jar')
            cmd = ['java', '-jar', trimmomatic_path, 'PE', '-threads', thread_count, '-phred33',
                   fq1_in_path, fq2_in_path, fq1_out_path, fq1_unpaired_path,
                   fq2_out_path, fq2_unpaired_path, 'ILLUMINACLIP:' + adapter_path]
            output = pipe_util.do_command(cmd, logger)

            #save time/mem to db
            df = time_util.store_time(uuid, cmd, output, logger)
            df['fastq'] = read1
            unique_key_dict = {'uuid': uuid, 'fastq': read1}
            table_name = 'time_mem_trimmomatic'
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_pe_' + read1_name, logger)
            logger.info('completed step PE `trimmomatic` of: %s' % read1)
            
        #generate diff
        if pipe_util.already_step(step_dir, 'trim_pe_diff_' + read1_name, logger):
            logger.info('already generated diff of trimmomatic of %s' % read1_name)
        else:
            logger.info('generating PE diff of trimmomatic of %s' % read1_name)
            cmd1 = ['diff', '-u', fq1_out_path, fq1_in_path, '>', diff1_path]
            cmd2 = ['diff', '-u', fq2_out_path, fq2_in_path, '>', diff2_path]
            shell_cmd1 = ' '.join(cmd1)
            shell_cmd1 = ' '.join(cmd2)
            output1 = pipe_util.do_shell_command(shell_cmd1, logger)
            output2 = pipe_util.do_shell_command(shell_cmd2, logger)

            #save time/mem to db
            df1 = time_util.store_time(uuid, cmd1, output1, logger)
            df2 = time_util.store_time(uuid, cmd2, output2, logger)
            df1['diff'] = diff1_name
            df2['diff'] = diff2_name
            df1['fastq_type'] = fastq_type
            df2['fastq_type'] = fastq_type
            unique_key_dict1 = {'uuid': uuid, 'diff':diff1_name, 'fastq_type': fastq_type}
            unique_key_dict2 = {'uuid': uuid, 'diff':diff2_name, 'fastq_type': fastq_type}
            table_name = 'time_mem_trimmomatic_diff'
            df_util.save_df_to_sqlalchemy(df1, unique_key_dict1, table_name, engine, logger)
            df_util.save_df_to_sqlalchemy(df2, unique_key_dict2, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_pe_diff_' + read1_name, logger)
            logger.info('completed generating PE diff of trimmomatic of %s' % read1_name)
            
        #generate diff stats
        if pipe_util.already_step(step_dir, 'trim_pe_summary_diff_log_' + read1_name, logger):
            logger.info('already completed step `summary stats of diff` of %s' % read1_name)
        else:
            logger.info('running step PE `summary of diff` of %s' % read1_name)
            trimmomatic_summ_met_dir = os.path.dirname(os.path.realpath(__file__))
            trimmomatic_summ_met_path = os.path.join(trimmomatic_summ_met_dir, 'trimmomatic_summary_metrics_from_diff.py')
            cmd1 = [trimmomatic_summ_met_path, '-d', diff1_path]
            cmd2 = [trimmomatic_summ_met_path, '-d', diff2_path]
            output1 = pipe_util.do_command(cmd1, logger)
            output2 = pipe_util.do_command(cmd2, logger)

            #save time/mem to db
            df1 = time_util.store_time(uuid, cmd1, output1, logger)
            df2 = time_util.store_time(uuid, cmd2, output2, logger)
            df1['diff'] = diff1_name
            df2['diff'] = diff2_name
            unique_key_dict1 = {'uuid': uuid, 'diff': diff1_name, 'fastq_type': fastq_type}
            unique_key_dict1 = {'uuid': uuid, 'diff': diff2_name, 'fastq_type': fastq_type}
            table_name = 'time_mem_trimmomatic_diff_summary'
            df_util.save_df_to_sqlalchemy(df1, unique_key_dict1, table_name, engine, logger)
            df_util.save_df_to_sqlalchemy(df2, unique_key_dict2, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_pe_summary_diff_log_' + read1_name, logger)
            
        #save stats to db
        if pipe_util.already_step(step_dir, 'trim_pe_summary_db_' + read1_name + '_db', logger):
            logger.info('already stored PE `trimmomatic` of %s to db' % read1)
        else:
            logger.info('storing `trimmomatic` of %s to db' % read1)
            df = trimmomatic_diff_summary_to_df(uuid, read1, trimlog_path, logger)
            df['uuid'] = uuid
            table_name = 'trimmomatic_diff_summary'
            unique_key_dict1 = {'uuid': uuid, 'fastq': read1_name}
            unique_key_dict2 = {'uuid': uuid, 'fastq': read2_name}
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_pe_summary_db_' + read1_name + '_db', logger)
            logger.info('completed storing PE `trimmomatic` of %s to db' % read1)

        #compress diff
        if pipe_util.already_step(step_dir, 'xz_pe_diff_' + read1_name, logger):
            logger.info('already compressed PE diff: %s' % diff1_name)
        else:
            logger.info('compressing PE diff: %s' % diff1_name)
            cmd1 = ['xz', '-9', diff1_path]
            cmd2 = ['xz', '-9', diff2_path]
            output1 = pipe_util.do_command(cmd1, logger)
            output2 = pipe_util.do_command(cmd2, logger)

            #save timem/mem to db
            df1 = time_util.store_time(uuid, cmd1, output1, logger)
            df2 = time_util.store_time(uuid, cmd2, output2, logger)
            df1['diff'] = diff1_name
            df2['diff'] = diff2_name
            unique_key_dict1 = {'uuid': uuid, 'diff': diff1_name, 'fastq_type': fastq_type}
            unique_key_dict2 = {'uuid': uuid, 'diff': diff2_name, 'fastq_type': fastq_type}
            table_name = 'time_mem_diff_xz'
            df_util.save_df_to_sqlalchemy(df1, unique_key_dict1, table_name, engine, logger)
            df_util.save_df_to_sqlalchemy(df2, unique_key_dict2, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'xz_pe_diff_' + read1_name, logger)
            logger.info('completed compressing PE diff: %s' % diff1_name)
            
    for seread in sefastqlist:
        read_name, read_ext = os.path.splitext(seread)
        if pipe_util.already_step(step_dir, 'trim_se_' + read_name, logger):
            logger.info('already completed se trim on %s' % seread)
        else:
            logger.info('running step SE `trimmomatic` of: %s' % seread)
            fq_in_path = os.path.join(fastq_dir, seread)
            fq_out_path = os.path.join(trimmomatic_dir, seread)
            cmd=['java', '-jar', trimmomatic_path, 'SE', '-threads', thread_count, '-phred33', 
                 fq_in_path, fq_out_path, 'ILLUMINACLIP:', ]
            output = pipe_util.do_command(cmd, logger)

            #save time/mem to db
            df = time_util.store_time(uuid, cmd, output, logger)
            df['fastq'] = seread
            unique_key_dict = {'uuid': uuid, 'fastq': seread}
            table_name = 'time_mem_trimmomatic'
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_se_' + read_name, logger)
            logger.info('completed running step SE `trimmomatic` of: %s' % fq_in_path)
        #save stats to db
        if pipe_util.already_step(step_dir, 'trim_se_' + read_name + '_db', logger):
            logger.info('already stored SE `trimmomatic` of %s to db' % seread)
        else:
            logger.info('storing `trimmomatic` of %s to db' % seread)
            df = trimmomatic_log_to_df(uuid, seread, trimlog_path, logger)
            df['uuid'] = uuid
            table_name = 'trimmomatic_log'
            unique_key_dict = {'uuid': uuid, 'fastq': seread}
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_se_' + read_name + '_db', logger)
            logger.info('completed storing SE `trimmomatic` of %s to db' % seread)
            
    for o1read in o1fastqlist:
        read_name, read_ext = os.path.splitext(o1read)
        if pipe_util.already_step(step_dir, 'trim_o1_' + read_name, logger):
            logger.info('already completed se trim on %s' % o1read)
        else:
            logger.info('running step SE `trimmomatic` of: %s' % o1read)
            fq_in_path = os.path.join(fastq_dir, o1read)
            fq_out_path = os.path.join(trimmomatic_dir, o1read)
            cmd=['java', '-jar', trimmomatic_path, 'SE', '-threads', thread_count, '-phred33',
                 fq_in_path, fq_out_path, 'ILLUMINACLIP:', ]
            output = pipe_util.do_command(cmd, logger)

            #save time/mem to db
            df = time_util.store_time(uuid, cmd, output, logger)
            df['fastq'] = o1read
            unique_key_dict = {'uuid': uuid, 'fastq': o1read}
            table_name = 'time_mem_trimmomatic'
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_o1_' + read_name, logger)
            logger.info('completed running step SE `trimmomatic` of: %s' % fq_in_path)
        #save stats to db
        if pipe_util.already_step(step_dir, 'trim_o1_' + read_name + '_db', logger):
            logger.info('already stored SE `trimmomatic` of %s to db' % o1read)
        else:
            logger.info('storing `trimmomatic` of %s to db' % o1read)
            df = trimmomatic_log_to_df(uuid, o1read, trimlog_path, logger)
            df['uuid'] = uuid
            table_name = 'trimmomatic_log'
            unique_key_dict = {'uuid': uuid, 'fastq': o1read}
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_o1_' + read_name + '_db', logger)
            logger.info('completed storing SE `trimmomatic` of %s to db' % o1read)

            
    for o2read in o2fastqlist:
        read_name, read_ext = os.path.splitext(o2read)
        if pipe_util.already_step(step_dir, 'trim_o2_' + read_name, logger):
            logger.info('already completed se trim on %s' % o2read)
        else:
            fq_in_path = os.path.join(fastq_dir, o2read)
            fq_out_path = os.path.join(trimmomatic_dir, o2read)
            cmd=['java', '-jar', trimmomatic_path, 'SE', '-threads', thread_count, '-phred33',
                 fq_in_path, fq_out_path, 'ILLUMINACLIP:', ]
            output = pipe_util.do_command(cmd, logger)

            #save time/mem to db
            df = time_util.store_time(uuid, cmd, output, logger)
            df['fastq'] = o2read
            unique_key_dict = {'uuid': uuid, 'fastq': o2read}
            table_name = 'time_mem_trimmomatic'
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_o2_' + read_name, logger)
            logger.info('completed running step SE `trimmomatic` of: %s' % o2read)
        #save stats to db
        if pipe_util.already_step(step_dir, 'trim_se_' + read_name + '_db', logger):
            logger.info('already stored SE `trimmomatic` of %s to db' % o2read)
        else:
            logger.info('storing `trimmomatic` of %s to db' % o2read)
            df = trimmomatic_log_to_df(uuid, o2read, trimlog_path, logger)
            df['uuid'] = uuid
            table_name = 'trimmomatic_log'
            unique_key_dict = {'uuid': uuid, 'fastq': o2read}
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(step_dir, 'trim_se_' + read_name + '_db', logger)
            logger.info('completed storing SE `trimmomatic` of %s to db' % o2read)


def get_duplicate_qname_df(uuid, fastq_name, log_path, logger):
    qname_set = set()
    with open(log_path, 'r') as f:
        for line in f:
            if 'duplicate:' in line:
                line_split = line.split(' ')
                qname = line_split[1].strip()
                qname_set.add(qname)
    qname_list = sorted(list(qname_set))
    df = pd.DataFrame(columns=['uuid', 'fastq_name', 'id'])
    df['id'] = qname_list
    df['uuid'] = uuid
    df['fastq_name'] = fastq_name
    logger.info('get_duplicate_qname_df() df=\n%s' % df)
    return df
                      

def get_duplicate_summary(uuid, fastq_name, log_path, logger):
    logger.info('get_duplicate_summary() log_path=%s' % log_path)
    kept_readcount = int()
    duplicate_readcount = int()
    with open(log_path, 'r') as f:
        for line in f:
            if 'readcounter' in line:
                line_split = line.split('=')
                kept_readcount = int(line_split[1].strip())
            elif 'duplicatecounter' in line:
                line_split = line.split('=')
                duplicate_readcount = int(line_split[1].strip())
    df = pd.DataFrame(columns=['uuid', 'fastq_name', 'kept_readcount', 'duplicate_readcount'])
    df['uuid'] = [uuid]
    df['fastq_name'] = fastq_name
    df['kept_readcount'] = str(kept_readcount)
    df['duplicate_readcount'] = str(duplicate_readcount)
    logger.info('get_duplicate_summary() df=\n%s' % df)
    return df
                      

def remove_duplicate_reads(uuid, fastq_dir, engine, logger):
    outdir = os.path.join(fastq_dir, 'rmdup')
    os.makedirs(outdir, exist_ok = True)
    fastq_list = buildfastqlist(fastq_dir, logger)
    for fastq_name in fastq_list:
        fastq_basename, fastq_ext = os.path.splitext(fastq_name)
        fastq_path = os.path.join(fastq_dir, fastq_name)
        outfile = os.path.join(outdir, fastq_name)
        log_path = os.path.join(outdir, 'rmdup_' + fastq_basename + '.log')
        logger.info('remove_duplicate_reads() fastq_path=%s' % fastq_path)
        logger.info('remove_duplicate_reads() outfile=%s' % outfile)
        logger.info('remove_duplicate_reads() log_path=%s' % log_path)
        if pipe_util.already_step(outdir, fastq_name + '_rmdup', logger):
            logger.info('already completed rmdup of: %s' % fastq_name)
        else:
            logger.info('running rmdup of: %s' % fastq_name)
            decomp_cmd = [ 'zcat', '"' + fastq_path + '"' ]
            home_dir = os.path.expanduser('~')
            python_cmd = os.path.join(home_dir, '.virtualenvs', 'p3', 'bin', 'python3')
            rmdup_cmd_path = os.path.join(home_dir, 'pipelines', 'dnaseq', 'other', 'remove_duplicate_mate_pair.py')
            rmdup_cmd = [ rmdup_cmd_path, '-l', '"' + log_path + '"' , '-' ]
            comp_cmd = [ 'gzip', '-', '>', '"' + outfile + '"' ]
            decomp_cmd_shell = ' '.join(decomp_cmd)
            #python_cmd_shell = ' '.join(python_cmd)
            rmdup_cmd_shell = ' '.join(rmdup_cmd)
            comp_cmd_shell = ' '.join(comp_cmd)
            shell_cmd = decomp_cmd_shell + ' | ' + python_cmd + ' ' + rmdup_cmd_shell + ' | ' + comp_cmd_shell
            logger.info('remove_duplicate_reads() shell_cmd=%s' % shell_cmd)
            output = pipe_util.do_shell_command(shell_cmd, logger)

            #save time/mem to db
            df = time_util.store_time(uuid, shell_cmd, output, logger)
            df['fastq'] = fastq_name
            unique_key_dict = {'uuid': uuid, 'fastq': fastq_name}
            table_name = 'time_mem_rmdup_fastq'
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
            pipe_util.create_already_step(outdir, fastq_name + '_rmdup', logger)
            logger.info('completed running rmdup of: %s' % fastq_name)

        #save stats to db
        if pipe_util.already_step(outdir, fastq_name + '_rmdup_db', logger):
            logger.info('already stored rmdup run of %s to db' % fastq_name)
        else:
            logger.info('storing rmdup run of %s to db' % fastq_name)
            #get details
            df = get_duplicate_qname_df(uuid, fastq_name, log_path, logger)
            table_name = 'rmdup_record_id'
            unique_key_dict = {'uuid':uuid, 'fastq_name': fastq_name, 'id':'impossible_match'}
            if len(df) > 0:
                df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

            #get summary
            df = get_duplicate_summary(uuid, fastq_name, log_path, logger)
            table_name = 'rmdup_summary'
            unique_key_dict = {'uuid':uuid, 'fastq_name': fastq_name}
            df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

            pipe_util.create_already_step(outdir, fastq_name + '_rmdup_db', logger)
            logger.info('completed storing rmdup run o0f %s to db' % fastq_name)
    return


def get_max_fastq_length_from_db(engine, logger):
    df = pd.read_sql_query('select * from fastqc_data_Basic_Statistics where Measure="Sequence length"', engine)
    max_fastq_length = int(max(list(df['Value'])))
    return max_fastq_length
