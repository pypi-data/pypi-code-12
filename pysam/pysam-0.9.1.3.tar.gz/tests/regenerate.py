import pysam
input_datasource = pysam.AlignmentFile("pysam_ex1.bam", 'rb')
output_datasource = pysam.AlignmentFile(
    "pysam_ex1_regen.bam", 'wb', header=input_datasource.header)
iter = input_datasource.fetch()
for read in iter:
    output_datasource.write(read)

output_datasource.close()

pysam.index("pysam_ex1_regen.bam")
