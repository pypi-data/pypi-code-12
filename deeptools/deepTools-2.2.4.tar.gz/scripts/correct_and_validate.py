import sys
sys.path.append('/data/projects/ramirez/tools/utilities')
import os
import numpy as np
from utilities import *
import shutil

""" Simple script that corrects the GC bias of a bam file
    and then plots some images to verify the bias correction.
    This file simply calls other python programs.
"""

def execute_and_log( command ):
    global out_path
    try:
        readme = open(out_path + "README" , 'a+')
    except IOError:
        readme = open(out_path + "README" , 'w')
    readme.write(command + "\n\n" )
    readme.close()
    os.system( command )

def correct_and_validate(species, bam_file, genome_file, mappability_file, regions_file, fragmentLength, out_dir, label, outFormat='bam', windowWidth=50):
    correctGC_command = "python /data/projects/ramirez/tools/GC_bias/correctGCbias.py -b %s -g %s -m %s --outDir %s -l %s --species %s -bs 50 -f %s  > /tmp/out" 

    plotGCbias_command = "python /data/projects/ramirez/tools/GC_bias/plotGCbias.py -b %s -g %s -o %s -s 20000 > /tmp/out"

    heatmapper_command = "python /data/projects/ramirez/tools/heatmapper/hm_multiproc.py -S %s -R %s -b 1600 -m 2000 -a 1600 -w "+ str(windowWidth) +"  -F %s --averageType median --skipZeros yes --colorMap RdBu --outFileName %s --outFileNameData %s %s " 
#    heatmapper_command = "python /data/projects/ramirez/tools/heatmapper/hm_multiproc.py -S %s -R %s -b 1500 -m 2000 -a 1500 -w 100  -F %s --averageType median --skipZeros yes --minThreshold 3 --colorMap RdBu --outFileName %s --outFileNameData %s %s " 
    global out_path
    out_path = "%s/%s/" % ( out_dir, label )
    if os.path.exists( out_path + "GC_correction.png" ):
        return out_path + "GC_correction.png"

    print "making copies of files in memory to speed up computations"

    print "destination folder %s " % ( out_path ) 
    if not os.path.exists( out_path ):
        os.system ("mkdir %s" % (out_path) )

    f = open(out_path + "README" , 'a+')
    f.write("bam_file = " + bam_file + "\n")
    f.close()

#    genome_file = copyFileInMemory( genome_file, '.2bit' )
    bam_file_memory  = copyFileInMemory( bam_file, '.bam' )
    # copy the corresponging index file '.bai'
    shutil.copyfile( bam_file + ".bai", bam_file_memory + ".bai")
    bam_file = bam_file_memory

               

    print(correctGC_command % (bam_file,
                                genome_file,
                                mappability_file,
                                out_path,
                                fragmentLength,
                                species,
                                outFormat) )


    corrFile = out_path + "corrected_counts."
    corrFile += 'bam' if outFormat=='bam' else 'bw'
    if not os.path.exists( corrFile ):
        print "computing correction"
        execute_and_log (correctGC_command % (bam_file,
                                        genome_file,
                                         mappability_file,
                                        out_path,
                                        fragmentLength,
                                        species,
                                        outFormat) )



    print "plotting GC bias"
    if 2 == 2:
        execute_and_log (plotGCbias_command % (bam_file,
                                               genome_file,
                                               out_path + "GC_bias"
                                               ))


    execute_and_log (heatmapper_command % (bam_file,
                                     regions_file,
                                     'bam',
                                     out_path + "before.png",
                                     out_path + "before.tab",
                                     "--outFileSortedRegions " + out_path + "sorted_genes.bed") )

    
    before = np.loadtxt( out_path + "before.tab" )

    ymin = int( round( before[:,1].min() ) )
    ymax = int( round( before[:,1].max() ) )

    execute_and_log (heatmapper_command % (corrFile,
                                           out_path + "sorted_genes.bed",
                                           outFormat,
                                           out_path + "after.png",
                                           out_path + "after.tab",
                                           "--sortRegions no --yMin %s --yMax %s --zMin %s --zMax %s" % \
                                               (ymin, ymax, ymin, ymax) ) )


    execute_and_log("montage -label before %s/before.png -label after %s/after.png  -pointsize 24 -font Nimbus-Sans-Bold -tile x1 -geometry 300x\>  %s/_temp.png" % \
                  ( out_path,
                    out_path,
                    out_path))


    execute_and_log("montage %s/GC_bias.png  %s/_temp.png -tile x1 -geometry 700x\>  %s/GC_correction.png" % \
                  ( out_path,
                    out_path,
                    out_path))


    os.remove( "%s/_temp.png" % (out_path) )

    return out_path + "GC_correction.png"

if __name__ == "__main__":

    out_dir = "/tmp/"
    if sys.argv[1] == 'mm9':
        ### the following are just test lines
        genes_file   = "/data/projects/ramirez/Inti_seq/results/2012_17_02_bam_heatmaps/genes.bed"
        genome_file  = "/data/projects/ramirez/tools/data/mm9.2bit"
        bam_file = "/data/solexa_data/110705_HWUSI-EAS616_00016_FC/BOWTIE_2011-07-21.12.28.02/110705_HWUSI-EAS616_00016_FC_7.bam"
        #bam_file = "/data/solexa_data/110705_HWUSI-EAS616_00016_FC/BOWTIE_2011-07-21.12.28.02/110705_HWUSI-EAS616_00016_FC_%d.bam"
    elif sys.argv[1] == 'dm3':
    ### the following are just test lines
#        genes_file   = "/data/projects/muehlpfordt/2011-Autumn_NSL/data/bed-files/Dm530.genes.bed"
        genes_file   = "/data/projects/ramirez/NSL/results/10_04_2012_gc_corrected_vs_log2/NSL1_a/ten_genes.bed"
#        genes_file   = "/tmp/genes.bed"
        genome_file  = "/dev/shm/2bit/dm3.2bit"
        mappability_file = "/dev/shm/mappability/dm3_50bp.bw"

        bam_file = "/data/projects/akhtar/mapped/RNAPolII_KenLam/NSL1kd-Input.bam"
#        bam_file = "/data/projects/akhtar/mapped/RNAPolII_KenLam/NSL1kd-a-PolII.bam"
        fragmentLength = 200
    #bam_file = "/data/solexa_data/110705_HWUSI-EAS616_00016_FC/BOWTIE_2011-07-21.12.28.02/110705_HWUSI-EAS616_00016_FC_%d.bam"
        out_dir = "/data/projects/ramirez/NSL/results/10_04_2012_gc_corrected_vs_log2"

    correct_and_validate(sys.argv[1], bam_file, genome_file, mappability_file, genes_file, fragmentLength, out_dir, "NSL1_input", windowWidth=10)
