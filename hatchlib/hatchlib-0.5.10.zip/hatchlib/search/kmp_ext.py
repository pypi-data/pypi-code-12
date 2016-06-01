def prefix(word):
	prefix,k=[0]*len(word),''
	
	for q in range(1,len(word)):
		while k>0 and word[k]!=word[q]:
			k=prefix[k-1]

		if word[k+1]==word[q]: k+=1
		prefix[q]=k

	return prefix