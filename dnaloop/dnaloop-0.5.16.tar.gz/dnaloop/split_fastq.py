# source /apps/lab/aryee/pyenv/versions/venv-2.7.10/bin/activate

import HTSeq
import re
import itertools

#fa1 = "/data/rivera/Data/07.31.15.Nextseq/tmp.r1.fasta"
#fa2 = "/data/rivera/Data/07.31.15.Nextseq/tmp.r2.fasta"


fq = "/data/rivera/Data/07.31.15.Nextseq/SKNMC.cohesin.chiapet.test.fastq"
fa1 = "/data/rivera/Data/07.31.15.Nextseq/SKNMC.cohesin.chiapet.test.extracted.r1.fasta"
fa2 = "/data/rivera/Data/07.31.15.Nextseq/SKNMC.cohesin.chiapet.test.extracted.r2.fasta"

fq = "/data/rivera/Data/07.31.15.Nextseq/SKNMC.FLI1.chiapet.test.fastq"
fa1 = "/data/rivera/Data/07.31.15.Nextseq/SKNMC.FLI1.chiapet.test.extracted.r1.fasta"
fa2 = "/data/rivera/Data/07.31.15.Nextseq/SKNMC.FLI1.chiapet.test.extracted.r2.fasta"


fastq_file = HTSeq.FastqReader(fq)
out_fasta_file1 = open(fa1, 'w')
out_fasta_file2 = open(fa2, 'w')

red = 0
blue = 0
nomatch = 0

#for read in itertools.islice( fastq_file, 10):
for read in fastq_file:
    #print read.name
    #print read.seq
    m_blue = re.search('(.+)GTTGGATAAGATATCGCGGCCGCGATATCTTATCCAAC(.{18}).*', read.seq)
    m_red = re.search('(.+)GTTGGAATGTATATCGCGGCCGCGATATACATTCCAAC(.{18}).*', read.seq)
    m = None
    if m_blue:
        #print "Blue"
        blue = blue + 1
        m = m_blue
    elif m_red:
        #print "Red"
        red = red + 1        
        m = m_red
    else:
        #print "No match"
        nomatch = nomatch + 1
    if m:
        #print m.group(1)
        #print m.group(2)
        read.seq = m.group(1)
        read.write_to_fasta_file( out_fasta_file1 )
        read.seq = m.group(2)        
        read.write_to_fasta_file( out_fasta_file2 )    



out_fasta_file1.close()
out_fasta_file2.close()

print red + blue + nomatch, "total reads"
print red, "red reads"
print blue, "blue reads"
print nomatch, "no match reads"




