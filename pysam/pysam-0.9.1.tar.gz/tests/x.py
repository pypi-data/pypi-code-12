import pysam
import os

DATADIR = "pysam_data"

retvals = pysam.depth(os.path.join(DATADIR, "ex1.bam"))
print retvals

