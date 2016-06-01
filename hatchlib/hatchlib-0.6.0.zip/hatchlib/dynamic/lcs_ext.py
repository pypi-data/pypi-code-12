def __build_lengths_matrix(str1,str2):
	matrix=[[0 for j in range(len(str2)+1)] for i in range(len(str1)+1)]
	for i,x in enumerate(str1):
		for j,y in enumerate(str2):
			if x==y: matrix[i+1][j+1]=matrix[i][j]+1
			else: matrix[i+1][j+1]=max(matrix[i+1][j],matrix[i][j+1])
	return matrix


def __read_from_matrix(matrix,str1,str2):
	result,i,j='',len(str1),len(str2)
	while i!=0 and j!=0:
		if matrix[i][j]==matrix[i-1][j]: i-=1
		elif matrix[i][j]==matrix[i][j-1]: j-=1
		else:
			result+=str1[i-1]
			i-=1
			j-=1
			
	return result[::-1]