"""
WELCOME TO GROUP'S E SUPERVISED PCA
This file contains the function PCAfunction that performs PCA on a data frame

Inputs:
    - df: DATA FRAME subject of the PCA analysis
    - colstodiscard: LIST of columns of df excluded from PCA analysis
    - accuracy: NUMERIC value to indicate the selected accuracy of PCA
Output: 
    - df2: DATA FRANE that combines the output of the PCA analysis with the
    columns that were discarded from the analysis

"""

"""
Necessary imports
"""
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

"""
PCA function. It works by:
    1) extracting the name of the columns from the data frame
    2) using those names to filter the data frame by the columns to be 
    analyzed and generating another one with the columns to be discarded
    (e.g. the TARGET variable)
    3) Run PCA on the selected data frame
    4) Identify the number of columns required to achieve the desired accuracy
    and run PCA again only with those columns as output
    5) Concatenate the result of PCA analysis and data frame with filtered
    columns and return it
"""
def PCAfunction(df, colstodiscard, accuracy):
    #local variable to count optimal number for PCA
    counter=0                       #count output columns from PCA
    dfnames=df.columns.values       #obtain column names from data frame
    dfnames = [ x for x in dfnames if x not in colstodiscard ]
    
    #Create output DF dtry with filtered columns and DF for the PCA analysis
    dftry=df
    for i in range(len(colstodiscard)):
        df = df.drop(colstodiscard[i], axis=1)
    for i in range(len(dfnames)):
        dftry = dftry.drop(dfnames[i], axis=1)

    #Converting and scaling the DF where the PCA will run     
    dfasmatrix= df.as_matrix()      #to matrix
    data=scale(dfasmatrix)          #scaled
    
    #running PCA, obtaining the maximum number of variables
    pca = PCA(n_components=(len(dfnames)))
    pca.fit(data)
    var1=np.cumsum(np.round(pca.explained_variance_ratio_, decimals=4)*100)
    print(var1)
    #Use the ACCURACY parameter to draw the line of when to stop PCA
    for i in range(len(var1)):
        if(var1[i-1]<accuracy):
            counter+=1

    #Rerun PCA only selecting the n_components determined above
    pca = PCA(n_components=counter)
    pca.fit(data)
    var1=np.cumsum(np.round(pca.explained_variance_ratio_, decimals=4)*100)
    print(var1)
    
    #Perform the PCA transformation
    output=pca.fit_transform(data)
    
    #Reshape back to DF
    df2=pd.DataFrame(data=output[0:,0:])

    #Merge the two DFs again       
    for i in range(len(colstodiscard)):
        df2[colstodiscard[i]] = dftry[colstodiscard[i]]

    #return DF resulting from PCA analysis
    return df2