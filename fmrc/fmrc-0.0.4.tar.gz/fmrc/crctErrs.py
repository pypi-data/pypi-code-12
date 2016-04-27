#import pstats, cProfile
import pyximport
pyximport.install()
import correct
#cProfile.run('correctErrors.correct()')
#correct.driver('/playpen/sgreens/fq_celegans/srr065388.fastq', '/playpen/sgreens/fq_celegans/msbwt60/bwt/', 100, 25, 2, False, '/playpen/sgreens/fq_celegans/msbwt60/corrected_newmus.fastq', 4)
correct.driver('/playpen/sgreens/ecoli/EAS20_8/cov20.fastq', '/playpen/sgreens/ecoli/msbwt20/bwt/', 100, 25, 3, False, '/playpen/sgreens/ecoli/msbwt20/corrected_newfp.fastq', 4)
#correct.driver('/playpen/sgreens/ecoli/EAS20_8/cov20.fastq', '/playpen/sgreens/ecoli/msbwt20/bwt/', 100, 25, 2, False, '/playpen/sgreens/ecoli/msbwt20/corrected_oneproc.fastq', 1)
#correct.correct('/playpen/sgreens/ecoli/EAS20_8/cov20.fastq', '/playpen/sgreens/ecoli/msbwt20/bwt/', 25, 2, 0, 1, 0)
