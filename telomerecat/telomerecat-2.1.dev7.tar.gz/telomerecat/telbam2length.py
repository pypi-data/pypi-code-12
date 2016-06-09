import sys
import textwrap
import time
import os
import re
import parabam
import pdb

import numpy as np
import pandas as pd

from shutil import copy
from numpy import genfromtxt,mean,sqrt,\
                  rot90,tril,log,zeros,std
from numpy import round as np_round
from itertools import izip,combinations
from collections import namedtuple,Counter

from pprint import pprint as ppr

import simulator

######################################################################
##
##      Create a length estimate given a set of TELBAMS 
##
##      Author: jhrf
##
######################################################################

class SimpleReadFactory(object):

    def __init__(self,vital_stats=None,trim_reads=False):
        self._SimpleRead = namedtuple("SimpleRead","seq qual" +
                                      " five_prime pattern mima_loci"+
                                      " avg_qual")

        if vital_stats:
            self._read_len = vital_stats["read_len"]
            self._phred_offset = vital_stats["phred_offset"]
        else:
            self._read_len = 100
            self._phred_offset = 33

        self._trim_reads = trim_reads
        self._templates = self.__get_compare_templates__(["TTAGGG","CCCTAA"])
        self._compliments = {"A":"T","T":"A",
                             "C":"G","G":"C",
                             "N":"N"}

    def get_simple_read(self,read):
        seq,qual = self.__flip_and_compliment__(read)
        if self._trim_reads:
            seq,qual = self.__trim_seq__(seq,qual)
        pattern = self.__get_pattern__(seq)

        mima_loci,frameshift_loci,pattern = \
                                self.__get_mima_loci__(seq,qual,pattern)

        avg_qual = self.__get_average_qual__(qual,mima_loci)

        simple_read = self._SimpleRead(
            seq,
            qual,
            self.__get_five_prime__(pattern),
            pattern,
            mima_loci,
            avg_qual)

        return simple_read

    def __get_average_qual__(self,qual,mima_loci):
        if len(mima_loci) == 0:
            return 0
        phreds = np.array([ord(qual[i])-self._phred_offset for i in mima_loci])
        return np.mean(phreds)

    def __get_compare_templates__(self,patterns):
        templates = {}
        for pattern in patterns:
            templates[pattern] = {}

            overshoot = (self._read_len / len(pattern)) + 1
            append_seq = pattern * overshoot

            for i in xrange(len(pattern)):
                reference = pattern[len(pattern)-i:] + append_seq
                reference = reference[:self._read_len]
                templates[pattern][i] = reference

        return templates

    def __trim_seq__(self,seq,qual):
        cutoff = 0
        min_sequence = 0
        for q in qual:
            qual_byte = ord(q) - self._phred_offset
            if qual_byte == 0:
                min_sequence += 1
            else:
                min_sequence = 0
            
            if min_sequence == 5:
                cutoff = cutoff - 5
                break

            cutoff += 1

        return seq[:cutoff],qual[:cutoff]

    def __get_five_prime__(self,pattern):
        if pattern is None:
            return None
        else:
            return pattern == "CCCTAA"

    def __get_pattern__(self,seq):
        cta,tag = "CCCTAA","TTAGGG"
        pattern = None
        if cta in seq or tag in seq:   
            if seq.count(cta) > seq.count(tag):
                pattern = cta
            else:
                pattern = tag
        return pattern

    def __flip_and_compliment__(self,read):
        if read.is_reverse:
            compliments = self._compliments
            seq_compliment = map(lambda base: compliments[base],read.seq)
            seq_compliment = "".join(seq_compliment)
            return(seq_compliment[::-1],read.qual[::-1])
        else:
            return (read.seq,read.qual)

    def __get_mima_loci__(self,seq,qual,pattern):
        if pattern is not None:
            return self.__generate_mima_loci__(seq,pattern)
        else:
            tga_mima = self.__get_simple_mima_loci__(seq,"TTAGGG")
            cta_mima = self.__get_simple_mima_loci__(seq,"CCCTAA")
            if len(cta_mima) < len(tga_mima):
                return cta_mima,[],"CCCTAA"
            else:
                return tga_mima,[],"TTAGGG"

    def __generate_mima_loci__(self,seq,pattern):
        simple_mima_loci = self.__get_simple_mima_loci__(seq,pattern)
        if len(simple_mima_loci) == 0:
            return [],[],pattern

        segments = re.split("(%s)" % (pattern,), seq)
        segments = self.__join_segments__(segments, pattern)
        mima_loci,fuse_loci = self.__get_damage_loci__(segments,pattern)
        return_loci = [m for m in mima_loci if m in simple_mima_loci]
        return_loci.extend(fuse_loci)

        return sorted(return_loci),fuse_loci,pattern

    def __get_simple_mima_loci__(self,seq,pattern):
        
        best_mima_loci = []
        best_mima_score = len(seq)+1

        for offset,ref in self._templates[pattern].items():
            cur_mima_loci = []
            cur_mima_score = 0
            for i,(s,r) in enumerate(izip(seq,ref)):
                if s != r:
                    cur_mima_loci.append(i)
                    cur_mima_score += 1

                if cur_mima_score > best_mima_score:
                    break
            if cur_mima_score < best_mima_score:
                best_mima_score = cur_mima_score
                best_mima_loci = cur_mima_loci
        return best_mima_loci

    def __get_damage_loci__(self,segments,pattern):
        mima_loci = []
        fuse_loci = []
        prev_was_tel = False
        offset = 0

        for segment in segments:
            if pattern in segment:
                if prev_was_tel:
                    fuse_loci.append(offset)
                else:
                    prev_was_tel = True
            else:
                mima_loci.extend(xrange(offset,offset+len(segment)))
                prev_was_tel = False
            offset += len(segment)
        return mima_loci,fuse_loci
            
    def __join_segments__(self,fragments,pattern):
        segments = []
        current_segment = ""
        prev_was_pattern = False
        for frag in fragments:

            if frag == "":
                continue

            elif current_segment == "":
                current_segment = frag
                prev_was_pattern = (frag == pattern)

            elif frag == pattern:
                if prev_was_pattern:
                    current_segment = current_segment + frag
                else:
                    new_segment = frag
                    count = 0
                    for c,p in izip(reversed(current_segment),
                                    reversed(pattern)):
                        if c == p:
                            new_segment = c + new_segment
                            count += 1
                        else:
                            break

                    not_matched = current_segment[:(len(current_segment) - count)]
                    if not_matched != "":
                        segments.append(not_matched)
                    current_segment = new_segment
                    prev_was_pattern = True

            else:
                new_segment = current_segment
                count = 0
                for c,p in izip(frag, pattern):
                    if c == p:
                        new_segment = new_segment + c
                        count += 1
                    else:
                        break
                segments.append(new_segment)
                if count == len(frag):
                    current_segment = ""
                else:
                    current_segment = frag[count:]

                prev_was_pattern = False

        if current_segment != "":
            segments.append(current_segment)
        
        return segments

class VitalStatsFinder(object):

    def __init__(self,temp_dir,total_procs,task_size):
        self._temp_dir = temp_dir
        self._total_procs = total_procs
        self._task_size = task_size

    def __csv_to_dict__(self,stats_path):
        insert_dat = np.genfromtxt(stats_path,delimiter=",",
                                names=True,dtype=("S256",float,float,
                                                         float,float,
                                                         float,float,
                                                         float,float,
                                                         float))

        ins_N = int(insert_dat['N'])
        if ins_N == 0:
            insert_mean = -1
            insert_sd = -1
        else:
            ins_sum = int(insert_dat['sum'])
            ins_power_2 = int(insert_dat['power_2'])

            insert_mean,insert_sd = \
                        self.__get_mean_and_sd__(ins_sum, ins_power_2, ins_N)
    
        min_qual = int(insert_dat['min_qual'])
        qual_mean,qual_sd = self.__get_mean_and_sd__(insert_dat["qual_sum"],
                                                    insert_dat["qual_power_2"],
                                                    insert_dat["qual_N"])

        return {"insert_mean":insert_mean, 
                "insert_sd": insert_sd,
                "min_qual":min_qual,
                "max_qual":int(insert_dat['max_qual']),
                "read_len":int(insert_dat['read_len']),
                "qual_mean":qual_mean,
                "qual_sd":qual_sd}

    def __get_mean_and_sd__(self,x_sum,x_power_2,x_N):
        x_mean = x_sum / x_N
        x_sd = np.sqrt( (x_N * x_power_2) - x_sum**2) / x_N

        return x_mean,x_sd

    def get_vital_stats(self,sample_path):

        vital_stats_csv = self.__run_vital_engine__(sample_path)
        vital_stats = self.__csv_to_dict__(vital_stats_csv)
        vital_stats["phred_offset"] = vital_stats["min_qual"]
 
        return vital_stats

    def __run_vital_engine__(self,sample_path,keep_in_temp=True):
        def engine(read,constants,master):
            stats = {}

            hash_count = read.qual.count("#")
            if read.is_read1 and read.is_proper_pair and read.mapq > 38:
                insert_size = abs(read.template_length)
                stats["sum"] = {"result":insert_size}
                stats["power_2"] = {"result":insert_size**2}
                stats["N"] = {"result":1}
            
            stats["read_len"] = {"result": len(read.seq)}
            byte_vals = map(ord,read.qual)
            min_qual = min(byte_vals)
            max_qual = max(byte_vals)

            qual_mean = np.mean(byte_vals)
            stats["qual_sum"] = {"result":qual_mean}
            stats["qual_power_2"] = {"result":qual_mean**2}
            stats["qual_N"] = {"result":1}

            stats["min_qual"] = {"result":min_qual}
            stats["max_qual"] = {"result":max_qual}

            return stats

        structures = {}

        structures["sum"] = {"data":0,"store_method":"cumu"}
        structures["power_2"] = {"data":0,"store_method":"cumu"}
        structures["N"] = {"data":0,"store_method":"cumu"}
        structures["read_len"] = {"data":0,"store_method":"max"}

        structures["min_qual"] = {"data":999,"store_method":"min"}
        structures["max_qual"] = {"data":0,"store_method":"max"}


        structures["qual_sum"] = {"data":0,"store_method":"cumu"}
        structures["qual_power_2"] = {"data":0,"store_method":"cumu"}    
        structures["qual_N"] = {"data":0,"store_method":"cumu"}  

        stat_interface = parabam.command.stat.Interface(self._temp_dir)
        out_paths = stat_interface.run(
            input_bams= [sample_path],
            total_procs = self._total_procs,
            task_size = 10000,
            user_constants = {},
            user_engine = engine,
            user_struc_blueprint = structures,
            keep_in_temp=keep_in_temp)

        return out_paths["global"][0]

class ReadStatsFactory(object):

    def __init__(self,temp_dir,
                        weights=None,
                        total_procs=4,
                        task_size = 10000,
                        full_read_stats=True,
                        debug_print=False):

        self._temp_dir = temp_dir
        self._total_procs = total_procs
        self._task_size = task_size

        self._full_read_stats = full_read_stats
        self._debug_print = debug_print

        if weights is None:
            self._weights = {'prior': 0.42,
                             'prior_weight': 1000}

        else:
            self._weights = weights

    def get_read_counts(self,path,vital_stats):
        read_stat_paths = self.run_read_stat_engine(path, vital_stats)

        read_array = self.__path_to_read_array__(read_stat_paths)

        error_profile,thresh = self.__paths_to_error_profile__(read_stat_paths)

        return self.read_array_to_counts(read_array,error_profile)

    def __paths_to_error_profile__(self,read_stat_paths,thresh = None):
        random_counts = None
        read_counts = None

        for path in read_stat_paths:
            if "random_counts" in path:
                random_counts = pd.read_csv(path,header=None).values 
            elif "read_counts" in path:
                read_counts = pd.read_csv(path,header=None).values 

        return self.__array_to_profile__(read_counts, random_counts)

    def __array_to_profile__(self,read_counts,random_counts, thresh = None):
        dif_counts = read_counts - random_counts

        if thresh is None:
            mask = np.zeros(read_counts.shape)
            mask[20:,20:] = 1
            arg_max_index = (read_counts * mask).argmax()
            dif_loci_x,dif_loci_y = np.unravel_index(arg_max_index,dif_counts.shape)
            hi_thresh = sorted(dif_counts[dif_loci_x-10:dif_loci_x+10,
                                dif_loci_y-15:dif_loci_y+1].flatten())[::-1]

            hi_thresh = hi_thresh[:100]
            thresh = np.percentile(hi_thresh,80) 

        if self._debug_print:
            print thresh

        error_profile = (dif_counts * (dif_counts > 0))\
                                 > thresh

        error_profile[11:,15:] = 0
        error_profile[33:,0] = 0
        error_profile[40:,0:] = 0
    
        error_profile = self.__prune_error_profile__(error_profile)
        error_profile = self.__rationalise_error_profile__(error_profile)
        error_profile[:11,:] = 1

        self.__find_genuine_cutoff__(read_counts,error_profile)

        return error_profile,thresh

    def __find_genuine_cutoff__(self,read_counts,error_profile):
        frequency = []
        for mima_count in xrange(read_counts.shape[0]):
            err_for_mima = (error_profile[mima_count,:] == 0) * 1
            read_counts_for_mima = read_counts[mima_count,:]
            filtered_counts = err_for_mima * read_counts_for_mima
            frequency.append(sum(filtered_counts))

        frequency = np.array(frequency)
        prop_frequency = frequency / float(sum(frequency))
        self.__array_to_file__(prop_frequency, "prop_freq")
        pdb.set_trace()

    def __prune_error_profile__(self, error_profile):
        first_locis = self.__get_first_loci__(error_profile)
        prune_mask = np.ones(error_profile.shape)
        for row_i in xrange(1,error_profile.shape[0]):
            if first_locis[row_i] == -1:
                continue 
            else:
                for col_i in xrange(error_profile.shape[1]):
                    if (not error_profile[row_i,col_i]) or \
                        col_i == 0:
                        continue
                    elif self.__prune_decision__(row_i,col_i,error_profile):
                        prune_mask[row_i,col_i] = 0
        return error_profile * prune_mask

    def __prune_decision__(self, row_i, col_i, error_profile):
        try:
            return self.__get_neighbor_sum__(row_i,col_i,error_profile) < 4
        except IndexError:
            return False

    def __get_neighbor_sum__(self,row_i, col_i, error_profile):

        neighbours = [(row_i-1,col_i+1),
                      (row_i-1,col_i),
                      (row_i-1,col_i-1),
                      (row_i,col_i+1),
                      (row_i,col_i-1),
                      (row_i+1,col_i+1),
                      (row_i+1,col_i),
                      (row_i+1,col_i-1),]

        neighbours_sum = sum([ error_profile[r,c] for (r,c) in neighbours])
        return neighbours_sum

    def __get_first_loci__(self,error_profile):
        first_loci = []
        for row_i in xrange(error_profile.shape[0]):
            if any(error_profile[row_i,:]):
                for col_i in xrange(error_profile.shape[1]):
                    if error_profile[row_i,col_i]:
                        first_loci.append(col_i)
                        break
            else:
                first_loci.append(-1)
        return first_loci

    def __rationalise_error_profile__(self, error_profile):
        start_row = np.where(error_profile)[0].max()
        global_loci = 0
        for i in reversed(xrange(0,start_row+1)):
            error_bins_in_row = np.where(error_profile[i,:])[0]
            if len(error_bins_in_row) > 0:
                cur_loci = error_bins_in_row.max()
            else:
                cur_loci = 0

            if cur_loci > global_loci:
                global_loci = cur_loci
            error_profile[i,:global_loci+1] = True
        
        return error_profile

    def __array_to_file__(self,array,unique):
        df = pd.DataFrame(array)
        out_path = "./%s-tmctout.csv" % (unique)
        df.to_csv(out_path,index=False,header=False)
        return out_path

    def __path_to_read_array__(self,read_stat_paths):
        #This is a stupid way of doing this, but that is a current
        #limitation of parabam return types
        for path in read_stat_paths:
            if "pair_stats" in path:
                return pd.read_csv(path,header=None).values
        return np.array([]) #shouldn't get here

    def read_array_to_counts(self,read_array,error_profile):
        complete_reads,boundary_reads = \
                        self.__get_complete_status__(read_array,error_profile)

        f2a_count,f4_count,observed_ratio,observed_weight,corrected_ratio =\
                             self.__get_f2a_count__(boundary_reads)
        f1_count = self.__get_f1_count__(complete_reads)

        return_dat = {"F2a":int(f2a_count),
                       "F1":int(f1_count),
                       "F4":f4_count,
                       "F2b_F4":f4_count*2,
                       "observed_ratio":observed_ratio,
                       "observed_weight":observed_weight,
                       "corrected_ratio":corrected_ratio}

        return return_dat

    def __get_f1_count__(self,complete_reads):
        return float(complete_reads.shape[0]) / 2

    def __get_f2a_count__(self,boundary_reads):

        f2_count,f4_count,total_reads = \
                 self.__get_read_counts__(boundary_reads)

        observed_f2a_ratio = (f2_count-f4_count) / float(total_reads)
        observed_f2a_weight = f2_count

        corrected_f2a_ratio = self.__get_bayes_f2a__(observed_f2a_ratio,f2_count)
            
        return total_reads * corrected_f2a_ratio,\
                f4_count,\
                observed_f2a_ratio,\
                observed_f2a_weight,\
                corrected_f2a_ratio

    def __get_bayes_f2a__(self,observed_f2a_ratio,observed_f2a_weight):
         
        prior_f2a_ratio = self._weights["prior"]
        prior_f2a_weight = self._weights["prior_weight"]
         
        bayes_ratio = self.__get_bayes_ratio__(observed_f2a_ratio,
                                                observed_f2a_weight,
                                                prior_f2a_ratio,
                                                prior_f2a_weight)
         
        if self._debug_print:
            print "obsv_weight",observed_f2a_weight
            print "obsv_ratio",observed_f2a_ratio
            print "adju_ratio",bayes_ratio

        return bayes_ratio
    
    def __get_bayes_ratio__(self,observed,observed_weight,prior,prior_weight):
        bayes_ratio = (observed*observed_weight) + (prior*prior_weight)
        bayes_ratio = bayes_ratio / (prior_weight + observed_weight)
        return bayes_ratio

    def __get_score__(self,binned_dat,obs_col=2):
        obs = binned_dat[:,obs_col]
        if obs_col == 2:
            exp = np.linspace(min(obs),max(obs),len(obs))
        else:
            exp = np.linspace(max(obs),min(obs),len(obs))
        return (np.round(np.corrcoef(exp,obs)[0,1],3))

    def __get_binned_dat__(self,read_counts):
        binned_dat = []

        linear_space = np.round(np.linspace(0,read_counts.shape[0]-1,10))
        lower_bin_lim = linear_space[:len(linear_space)-1]
        upper_bin_lim = linear_space[1:]

        for lo,hi in izip(lower_bin_lim,upper_bin_lim):
            binned_count = sum(read_counts[int(lo):int(hi),:]).tolist()
            if binned_count[2] > 0:
                binned_ratio = binned_count[0] / binned_count[2]
            else:
                binned_ratio = 0
            binned_count.append(binned_ratio)
            binned_dat.append(binned_count)

        return np.array(binned_dat)

    def __get_ratio_weights__(self,ratios,counts):
        term_1 = ((ratios < .5) * abs(1 - ratios))*5
        term_2 = (1 - abs(ratios - np.mean(ratios)))

        weights = (term_2 -term_1)
        weights = [0 if w < 0 else w for w in weights]

        return weights
    
    def __get_read_counts__(self,boundary_reads):
        f2_count = sum(boundary_reads[:,3] == 1)
        f4_count = sum(boundary_reads[:,3] == 0)
        total_reads = boundary_reads.shape[0]
        return f2_count,f4_count,total_reads
        
    def __get_complete_status__(self,read_array,error_profile):
        boundary_indicies = []
        complete_indicies = []

        for i in xrange(int(read_array.shape[0])):
            read_info = map(int,read_array[i,[0,-2]])
            pair_info = map(int,read_array[i,[2,-1]])

            read = error_profile[read_info[0],read_info[1]] 
            pair = error_profile[pair_info[0],pair_info[1]]

            if read and pair:
                complete_indicies.append(i)
            elif (not read) and pair:
                boundary_indicies.append(i)

        return read_array[complete_indicies,:],\
                read_array[boundary_indicies,:]

    def run_read_stat_engine(self,path,
                                vital_stats,
                                keep_in_temp=True):

        simple_read_factory = SimpleReadFactory(vital_stats)
        phred_offset = vital_stats["phred_offset"]

        maxtrix_max = (vital_stats["max_qual"] - phred_offset)+1
        matrix_shape = (vital_stats["read_len"]+1,maxtrix_max)

        def get_return_stats(reads):

            return_stats = [len(reads[0].mima_loci),
                            int(reads[0].five_prime),
                            len(reads[1].mima_loci),
                            int(reads[1].five_prime),
                            reads[0].avg_qual,
                            reads[1].avg_qual]

            return return_stats

        def engine(reads,constants,master):
            simple_reads = [simple_read_factory.get_simple_read(read) \
                                                         for read in reads]
            return_dat = np.zeros((2,6))
            return_dat[0,:] = get_return_stats(simple_reads)
            return_dat[1,:] = get_return_stats(simple_reads[::-1])

            random_counts = np.zeros(matrix_shape)
            read_counts = np.zeros(matrix_shape)

            for read in simple_reads:
                read_counts[len(read.mima_loci),int(read.avg_qual)] += 1

                #sample_size = int(np.random.uniform(1,80))
                sample_size = len(read.mima_loci)
                if sample_size > 0:
                    rand_quals  = np.random.choice(list(read.qual),sample_size)
                    qual_bytes  = [ord(q) - phred_offset for q in rand_quals]
                    rand_avg = np.mean(qual_bytes)

                    random_counts[int(sample_size),int(rand_avg)] += 1

            return {"pair_stats":{"result":np.array(return_dat)},
                    "random_counts":{"result":random_counts},
                    "read_counts":{"result":read_counts}}

        structures = {"pair_stats":{"data":np.zeros((2,6)),
                                    "store_method":"vstack"},
                     "read_counts":{"data":np.zeros(matrix_shape),
                                    "store_method":"cumu"},
                     "random_counts":{"data":np.zeros(matrix_shape),
                                    "store_method":"cumu"}}

        stat_interface = parabam.command.stat.Interface(self._temp_dir)
        out_paths = stat_interface.run(
            input_bams= [path],
            total_procs = self._total_procs,
            task_size = self._task_size,
            user_constants = {},
            user_engine = engine,
            user_struc_blueprint = structures,
            pair_process = True,
            keep_in_temp=keep_in_temp,
            verbose=0)

        return out_paths[path]

class Interface(parabam.core.Interface):
    def __init__(self,temp_dir):
        super(Interface,self).__init__(temp_dir)
        self._compliments = {"A":"T","T":"A","C":"G","G":"C","N":"N"}

    def run_cmd(self,parser):
        cmd_args = parser.parse_args()
        self.run(input_paths = cmd_args.input,
            total_procs = cmd_args.p,
            task_size = cmd_args.s,
            reader_n = cmd_args.f,
            verbose = cmd_args.v,
            inserts_path=cmd_args.insert,
            output = cmd_args.out,
            announce=True)

    def run(self,input_paths,total_procs,task_size,verbose,
            output,reader_n,inserts_path=None,
            announce=False,keep_in_temp=False):
        
        if not verbose:
            announce = False
        self.verbose = verbose
        program_name = "telomerecat telbam2length"
        self.__introduce__(program_name,announce)

        names = map(lambda b: self.__get_basename__(b),input_paths)
        names = map(lambda nm: nm.replace("_telbam",""),names)

        output_csv_path = self.__create_output_file__(output)
        vital_stats_finder = VitalStatsFinder(self._temp_dir, 
                                        total_procs,
                                        task_size)
        
        insert_length_generator = self.__get_insert_generator__(inserts_path)

        self.__output__(" Results will be written to the following file:\n",1)
        self.__output__("\t./%s\n\n" % (os.path.basename(output_csv_path,)))

        for sample_path,sample_name, in izip(input_paths,names):
            sample_intro = " Estimating telomere length of sample: %s\n" \
                                                            % (sample_name)

            self.__output__(sample_intro,1)
            self.__output__("\t- Estimation started %s\n" \
                                    % (self.__get_date_time__(),),2)

            self.__output__("\t- Finding read error rates and insert size\n",2)
            vital_stats = vital_stats_finder.get_vital_stats(sample_path)
            self.__check_vital_stats_insert_size__(inserts_path,
                                                    insert_length_generator,
                                                    vital_stats)

            read_type_counts = self.__get_read_types__(sample_path,
                                                       vital_stats,
                                                       total_procs)

            simulation_results = self.__run_simulation__(vital_stats,
                                                         read_type_counts,
                                                         total_procs)

            read_type_counts.update(simulation_results)

            self.__write_to_csv__(read_type_counts,output_csv_path,sample_name)

            self.__output__("\t- Estimation finished %s\n\n" \
                                            % (self.__get_date_time__(),),2)
        
        self.__goodbye__(program_name,announce)
        if keep_in_temp:
            return output_csv_path
        else:
            self.__copy_out_of_temp__([output_csv_path])
            return os.path.join(".",os.path.split(output_csv_path)[1])

    def __get_insert_generator__(self,inserts_path):
        if inserts_path:
            with open(inserts_path,"r") as inserts_file:
                for line in inserts_file:
                    yield map(float,line.split(","))

    def __check_vital_stats_insert_size__(self,inserts_path,
                                        insert_length_generator,vital_stats):
        if inserts_path:
            insert_mean,insert_sd = insert_length_generator.next()
            vital_stats["insert_mean"] = insert_mean
            vital_stats["insert_sd"] = insert_sd
            self.__output__("\t\t+ Using user defined insert size: %d,%d\n" \
                                                    % (insert_mean,insert_sd),2)
        elif vital_stats["insert_mean"] == -1:
            default_mean,default_sd = 350,25
            vital_stats["insert_mean"] = 350
            vital_stats["insert_sd"] = 25
            self.__output__("\t\t+ Failed to estimate insert size. Using default: %d,%d\n"\
                                                % (default_mean,default_sd),2)

    def __get_read_types__(self,sample_path,vital_stats,total_procs,read_stats_factory=None):

        self.__output__("\t- Categorising reads into telomeric read types\n",2)


        if read_stats_factory is None:
            read_stats_factory = ReadStatsFactory(temp_dir=self._temp_dir,
                                                  total_procs=total_procs,
                                                  debug_print=False)
            
        read_type_counts = read_stats_factory.get_read_counts(sample_path,
                                                              vital_stats)

        self.__output__("\t\t+ F1:%d | F2a:%d | F2b+F4:%d\n" % \
                                                (read_type_counts["F1"],
                                                read_type_counts["F2a"],
                                                read_type_counts["F2b_F4"],),2)
        return read_type_counts 

    def __create_output_file__(self,output):
        if output:
            unqiue_file_ID = output
        else:
            unqiue_file_ID = "telomerecat_length_%d.csv" % (time.time(),)

        output_csv_path = os.path.join(self._temp_dir,unqiue_file_ID)
        with open(output_csv_path,"w") as total:
            header = "Sample,F1,F2a,F2b_F4,Uncertainty,Insert_mean,Insert_sd,obs_r,obs_w,cor_r,Length\n"
            total.write(header)
        return output_csv_path

    def __output__(self,outstr,level=-1):
        if self.verbose and (self.verbose >= level or level == -1):
            sys.stdout.write(outstr)
            sys.stdout.flush()

    def __write_to_csv__(self,read_type_counts,output_csv_path,name):
        with open(output_csv_path,"a") as counts:
            counts.write("%s,%d,%d,%d,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%d\n" %\
                (name,
                read_type_counts["F1"],
                read_type_counts["F2a"],
                read_type_counts["F2b_F4"],
                read_type_counts["uncertainty"],
                read_type_counts["insert_mean"],
                read_type_counts["insert_sd"],
                read_type_counts["observed_ratio"],
                read_type_counts["observed_weight"],
                read_type_counts["corrected_ratio"],
                read_type_counts["length"]))

    def __run_simulation__(self,vital_stats,read_type_counts,total_procs):
        self.__output__("\t- Using read counts to estimate length\n",2)
        total_F2 = read_type_counts["F2a"]
        total_f1 = read_type_counts["F1"]
        read_length = vital_stats["read_len"]
        insert_mean = vital_stats["insert_mean"]
        insert_sd =   vital_stats["insert_sd"]

        len_mean,len_std = simulator.run_simulator_par(insert_mean,insert_sd,
                                        total_f1,total_F2,
                                         total_procs,read_length,N=16)
        self.__output__("\t\t+ Length: %d\n" % (len_mean,),2)

        return {"insert_mean":insert_mean,
                "insert_sd":insert_sd,
                "length":len_mean,
                "uncertainty":len_std}

    def __copy_out_of_temp__(self,file_paths,copy_path="."):
        map(lambda fil: copy(fil,copy_path),file_paths)

    def get_parser(self):
        parser = self.default_parser()
        parser.description = textwrap.dedent(
        '''\
        telomerecat telbam2length
        ----------------------------------------------------------------------

            The telbam2length command allows the user to genereate a telomere
            length estimate from a previously generated TELBAM file.

            Example useage:

            telomerecat telbam2length /path/to/some_telbam.bam

            This will generate a .csv file with an telomere length estimate
            for the `some_telbam.bam` file.

        ----------------------------------------------------------------------
        ''')

        parser.add_argument('input',metavar='TELBAM(S)', nargs='+',
            help="The telbam(s) that we wish to analyse")
        parser.add_argument('--out',metavar='CSV',type=str,nargs='?',default=None,
            help='Specify output path for length estimation CSV.\n'+\
                'Automatically generated if left blank [Default: None]')
        parser.add_argument('--insert',metavar='CSV',nargs='?',type=str,default=None,
            help="A file specifying the insert length mean and std for\n"+\
                 "each input sample. If not present telomerecat will\n"+\
                 "automatically estimate insert length of sample [Default: None]")
        parser.add_argument('-x',action="store_true",default=False
            ,help="Include extra information regarding the sample in output .csv")
        parser.add_argument('-v',choices=[0,1,2],default=0,type=int,
            help="Verbosity. The amount of information output by the program:\n"\
            "\t0: Silent [Default]\n"\
            "\t1: Output\n"\
            "\t2: Detailed Output")

        return parser

if __name__ == "__main__":
    print "Do not run this script directly. Type `telomerecat` for help."
