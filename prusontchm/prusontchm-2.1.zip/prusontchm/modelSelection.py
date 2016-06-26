def eleccionmodelo (df):
    import time
    from sklearn.metrics import roc_auc_score
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import svm, metrics,linear_model,tree
    import statsmodels.api as sm
    import pandas as pd
    
    metodo = []  #algorithm name
    gini = []    #algorithm gini
    tiempos = []    #algorithm time
     
    df.columns = [x.lower() for x in df.columns]
    objetivo = [col for col in df.columns if 'target' in col]
    objetivo = ''.join(objetivo)
    
    dfBorrar = df[['id', objetivo]]
    borrar = ['id', objetivo]
    dfaux = df.drop(borrar, axis=1)
    
    # Vamos a comaparar los siguientes modelos y elegir el que mejor funciona para el data frame de entrada
    # GML
      
    metodo.append('Generalized Linear Model (GML)')

    #Hora de inicio.
    start_time = time.time()  
    
    model= sm.GLM(df[objetivo],dfaux, family = sm.families.Binomial())
    resultGML = model.fit()
    
    # Tiempo transcurrido en la ejecución
    tiempo = time.time() - start_time  
    tiempos.append(tiempo)
    
    prediccion_GML= resultGML.predict(dfaux)     
    gini_GML= 2*roc_auc_score(df[objetivo], prediccion_GML)-1
    gini.append(gini_GML)
    
    # Logistic Regression 
    metodo.append('Logistic Regression')
    #Hora de inicio.
    start_time = time.time()
    
    modelo=linear_model.LogisticRegression()
    resultLR = model.fit()
    
    # Tiempo transcurrido en la ejecución
    tiempo = time.time() - start_time  
    tiempos.append(tiempo)
    
    pred_LR = resultLR.predict(dfaux) 
    gini_LR = 2*roc_auc_score(df[objetivo], pred_LR)-1
    gini.append(gini_LR)
    
    # Random Forest
    metodo.append('Random Forest')
                 
    #Hora de inicio.
    start_time = time.time()
    
    model= RandomForestClassifier(n_estimators=1000, max_depth=60, n_jobs=2 )
    resultRF = model.fit(dfaux, df[objetivo])
    
    # Tiempo transcurrido en la ejecución
    tiempo = time.time() - start_time  
    tiempos.append(tiempo)
    
    pred_RF = resultRF.predict(dfaux)
    gini_RF = 2*roc_auc_score(df[objetivo], pred_RF)-1
    gini.append(gini_RF)
    
    # Decision Tree
    metodo.append('Decision Tree (DT)')
                 
    #Hora de inicio.
    start_time = time.time()
    
    modelo = tree.DecisionTreeClassifier()
    resultDT = model.fit(dfaux, df[objetivo])
    
    # Tiempo transcurrido en la ejecución
    tiempo = time.time() - start_time  
    tiempos.append(tiempo)
    
    pred_DT = resultDT.predict(dfaux)
    gini_DT = 2*roc_auc_score(df[objetivo], pred_DT)-1
    gini.append(gini_DT)
    
    # SVM
    metodo.append('Support Vector Machine (SVM)')       
    
    #Hora de inicio.
    start_time = time.time()
      
    model = svm.SVC(probability=True, class_weight="auto")
    resultSVM = model.fit(dfaux, df[objetivo])
    
    # Tiempo transcurrido en la ejecución
    tiempo = time.time() - start_time  
    tiempos.append(tiempo)
    
    pred_SVM = resultSVM.predict(dfaux)
    gini_SVM = 2*roc_auc_score(df[objetivo], pred_SVM)-1
    gini.append(gini_SVM)
  
    ## Creación de un data frame con los resultados:
    resultados =  pd.DataFrame()
    
    resultados['Método']=metodo
    resultados['Velocidad']=tiempos
    resultados['Valoración (Gini)']=gini
    
    print
    print"Ranking de modelos"
    print(resultados.sort_values(by=['Valoración (Gini)','Velocidad'], ascending=[False,True]))
