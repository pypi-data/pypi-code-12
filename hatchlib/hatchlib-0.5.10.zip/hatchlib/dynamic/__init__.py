
def lcs(str1,str2):
	from hatchlib.dynamic.lcs_ext import __build_lengths_matrix,__read_from_matrix
	lengths=__build_lengths_matrix(str1,str2)
	return __read_from_matrix(lengths,str1,str2)