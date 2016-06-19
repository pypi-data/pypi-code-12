import pandas as pd
import numpy as np
import operator

df = pd.read_csv("dev.csv")
print("INPUT")
print(df.head(10))
print("number of records:", len(df.index))
print("number of variables:", len(df.columns))
colnames = list(df.columns[0:len(df.columns)])
print("columns name:", colnames)
#print("data type:", dict(df.dtypes))
for k,v in dict(df.dtypes).items():
    if v == 'O':
        print(k)
        freq = dict(df.groupby(k)[k].count())
        sorted_freq = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
        print(sorted_freq[0][0])
        for i in range(0,len(df.index)-835):
            if pd.isnull(df[k][i]):
                df[k][i] = sorted_freq[0][0] #Replaced by highest frequency value

for k,v in dict(df.dtypes).items():
    if v != 'object':
        for i in range(0,len(df.index)-839):
            if np.isnan(df[k][i]):
                df[k][i] = 0

for k,v in dict(df.dtypes).items():
    if v != 'object':
        print(k)
        print("mean:" ,np.average(df[k]))
        #print("stdev:" ,np.std(df[k]))
        total_pos = 0
        total_neg = 0
        for i in range(0,len(df.index)-820):
            if (df[k][i] >= 0):
                total_pos += 1
            if (df[k][i] < 0):
                total_neg += 1
        print("total positive values:", total_pos)
        print("total negative values:", total_neg)
        negSignMistake = total_neg / len(df.index)
        print("percentage of negative values:", negSignMistake)
        for i in range(0,len(df.index)-820):
            if (negSignMistake < 0.05):
                if (df[k][i] < 0):
                    df[k][i] = df[k][i] * -1
        outliers = 0
        for i in range(0,len(df.index)-820):
            if (df[k][i] < (np.average(df[k]) - 3 * np.std(df[k]))) or (df[k][i] > (np.average(df[k]) + 3 * np.std(df[k]))):
                #print('outliers:', df[k][i])
                outliers =+ 1
                print('outliers value:' ,df[k][i]) 
                df[k][i] = np.average(df[k])
                print('new value:', df[k][i])
        print("total outliers:", outliers)
        #print(df[k][0])
        
print("OUTPUT")
print(df.head(10))
