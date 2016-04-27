#import pstats, cProfile
import pyximport
pyximport.install()
import correct
#cProfile.run('correctErrors.correct()')
file_names = ['FF0683_F_ATCACG_s_' + numbers + '_sequence' for numbers in ['5_1', '5_2', '2_1', '2_2', '3_1', '3_2', '4_1', '4_2']]
for file_name in file_names:
	correct.driver('/playpen/sgreens/rna_correction/' + file_name + '.txt', '/csbiodata/CEGS3x3BWT/FF0683_F', 100, 25, 2, False, '/playpen/sgreens/rna_correction/c_' + file_name + '.fastq', 4)
#correct.driver('/playpen/sgreens/ecoli/EAS20_8/cov20.fastq', '/playpen/sgreens/ecoli/msbwt20/bwt/', 100, 25, 2, False, '/playpen/sgreens/ecoli/msbwt20/corrected_newmus.fastq', 4)
#correct.correct('/playpen/sgreens/ecoli/EAS20_8/cov20.fastq', '/playpen/sgreens/ecoli/msbwt20/bwt/', 25, 2, 0, 1, 0)
