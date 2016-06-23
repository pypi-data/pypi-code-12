def Seleccion_Ratios(df):

    import numpy as np
    import pandas as pd
    
    from sklearn import tree
    #from sklearn import metrics
    from sklearn import cross_validation
    from sklearn.decomposition import PCA as sklearnPCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    
    # Eliminamos antes del cálculo de las PCAs las columnas target e id.
    
    df.columns = [x.lower() for x in df.columns]
    objetivo = [col for col in df.columns if 'target' in col]
    objetivo = ''.join(objetivo)

    dfBorrar = df[['id', objetivo]]
    borrar = ['id', objetivo]
    dfaux = df.drop(borrar, axis=1)
    
    ListaColumnas= dfaux.columns
    tamDf = len(dfaux.columns)
    X_std = StandardScaler().fit_transform(dfaux.values)
    pca=sklearnPCA(n_components=tamDf).fit_transform(X_std)
    columnas_pca=[]
   
    for i in range(0,pca.shape[0]):
        v="VAR_PCA_"+str(i)
        columnas_pca.append(v)

    df1=pd.DataFrame(X_std,columns=ListaColumnas)
    df2=pd.DataFrame(pca,columns=columnas_pca)
    
   
    df_PCA=pd.concat([df1,df2],axis=1)
    
    y = df[objetivo]
   
    
    forest = RandomForestClassifier(n_estimators=250, random_state=0)
    forest.fit(df_PCA, y)
    importances = forest.feature_importances_
    std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
    indices = np.argsort(importances)[::-1]

    # Obtenemos el ranking de los mejores 30
    print("TOP 30:")
    
    for f in range(30):
        print("%d. Ratio %s (%f) " % (f + 1, df_PCA.columns[indices[f]], importances[indices[f]] ))
    