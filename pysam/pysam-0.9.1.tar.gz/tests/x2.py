# 7577625 is my position in the reference
import pysam
# inf = pysam.AlignmentFile("/ifs/home/andreas/Downloads/olingerc_assembly.bam")
inf = pysam.AlignmentFile("x.bam")

for chrom in inf.references:
    print chrom
    for column in inf.pileup(chrom, 7577600, 7577700):
        for pileupread in column.pileups:
            for alignment_tuple in enumerate(pileupread.alignment.get_aligned_pairs(with_seq=True)):
                if alignment_tuple[1][1] == 7577625:
                    print(alignment_tuple)
                    if alignment_tuple[1][2] == "A":
                        print pileupread.alignment.query_name
