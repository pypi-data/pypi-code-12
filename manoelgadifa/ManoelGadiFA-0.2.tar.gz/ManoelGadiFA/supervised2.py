import numpy as np
import pandas as pd

path = "/Users/jonasbeullens/Documents/IE/Kaggle/babab/train 2.csv"
data = pd.read_csv(path)

#data = data.ix[1:200,1:50]

def calculateEntropy(prob):
		result = -1 * prob * np.log2(prob)
		return result

#bins=[2]

"""
bins= []
for i in range(1,100,1):
		print(i)
		bins.append(i)
"""
def binning1(x):
	bestEntropy = 1.0
	bestbin = 0
	for b in bins:
		try:
			newdataa = [x, data['TARGET']]
			newdata = pd.concat(newdataa, axis=1)
			
			#print(newdata.head())
			#print(newdata['TARGET'])
			#print(newdata.ix[:,0])
			try: 
				newdata['binneddata'] = pd.qcut(newdata.ix[:,0], b, labels=False)
			except: #when there is no differenciation
				newdata['binneddata'] = newdata.ix[:,0]
			
			#print(newdata.head())

			bindf = pd.DataFrame(index=range(round(float(newdata.shape[0])/(b+1))), columns=range(b)) #is rounding correct?
			bindf = bindf.fillna(0)
			#print(bindf.head())
			
			entropyList = []
			#newnewdata = pd.DataFrame(0, index= round(float(newdata.shape[0])/(b+1)), columns= range(b))

			total = newdata.shape[0]
			#print(newdata)

			for i in range(b):
				#print(newdata['binneddata'])
				#bindf.ix[:,i]= newdata[newdata['binneddata']==i].ix[:,0]
				
				#bindf.ix[:,i] = newdata[newdata['binneddata']==i][0]
				#print(bindf.head())

				#sumTarget= bindf.ix[:,i].sum()
				sumTarget = newdata[newdata['binneddata']==i].ix[:,1].sum()
				#print(sumTarget)
				prob=  sumTarget /total

				entropyList.append(calculateEntropy(prob))

			#print(entropyList)
			totEntropy= 0
			for i in entropyList:
				totEntropy = totEntropy + (i/len(entropyList))

			#print(totEntropy)
			
			if totEntropy < bestEntropy:
				print(totEntropy)
				bestEntropy = totEntropy
				bestbin = b
				
				print(bestbin)
				#print(bestbin)
			else:
				break
			"""
			if totEntropy < bestEntropy AND counter >2:
				bestEntropy = totEntropy
				bestbin = b
				b = b + 5
			elif totEntropy < bestEntropy AND counter <2:


			"""
		except:
			break
	#try:
	

	#print(pd.qcut(newdata.ix[:,0], bestbin, labels=False))
	global binned1 
	binned1[list(newdata.columns.values)[0]]  =(pd.qcut(newdata.ix[:,0], bestbin, labels=False))

	#except:
	#	print("auauauau")
	



	

	

	
"""
	
#totalEntropy = (entropy1 + entropy2 )  / 2

def binning2(x):
	newdataa = [x, data['TARGET']]
	newdata = pd.concat(newdataa)
	print(newdata.head())
"""
def main1(data): 
	try:
		data['TARGET']
	except:
		print("Hi there ! You need a variable called TARGET in your dataframe in order to perform the supervised binning!")

	#data= data.ix[1:200,1:50] #sample data

	global bins 
	bins = [2,5,10,25,50,75,100,150,200]

	data_num = data.select_dtypes(include=[np.float])
	data_int = data.select_dtypes(include=[np.int])
	data_string = list(data.select_dtypes(include=[object]))
	print(data_string)

	global binned1 
	binned1= pd.DataFrame()
	data_num.apply(binning1,axis =0)
	binned1 = binned1.ix[:, binned1.columns != 'TARGET']
	binned1['TARGET'] = data['TARGET']

	#print(binned1)
	#print('ja1')
	data_string = pd.get_dummies(data[data_string])
	#print("ja2")
	#print(data_string)

	datatemp= [binned1,data_string]
	#print('ja3')
	compData = pd.concat(datatemp, axis=1)
	#print('ja4')
	#print(compData)
	#print('ja5')

	#print(data_int)
	#print('ja6')

	datatemp2 = [data_int,compData]
	final = pd.concat(datatemp,axis=1)

	#print(final)
	final.to_csv("final.csv")

main1(data)
