
# coding: utf-8

# In[7]:

def ratios(df2):
    #LIBRARIES
    import numpy as np
    import pandas as pd
    
    a=len(df2.columns)
    #TRANSFORMACIONES X+Y
    for i in range(a):
        for j in range(i,a):
            df2.ix[:,str(1000+i)]=df2.ix[:,i]+df2.ix[:,j]   

    #TRANSFORMACIONES X-Y
    for i in range(a):
        for j in range(i,a):
            df2.ix[:,str(2000+i)]=df2.ix[:,i]-df2.ix[:,j]

    #TRANSFORMACIONES X*Y
    for i in range(a):
        for j in range(i,a):
            df2.ix[:,str(3000+i)]=df2.ix[:,i]*df2.ix[:,j]

    #TRANSFORMACIONES X/Y
    for i in range(a):
        for j in range(a):
            if i!=j:
                df2.ix[:,str(4000+i)]=np.where(df2[df2.columns[j]]==0,0,df2.ix[:,i]/df2.ix[:,j])

    #TRANSFORMACIONES (X-Y)/Y
    for i in range(a):
        for j in range(a):
            if i!=j:
                df2.ix[:,str(5000+i)]=np.where(df2[df2.columns[j]]==0,0,(df2.ix[:,i]-df2.ix[:,j])/df2.ix[:,j])

    #TRANSFORMACIONES X^2
    for i in range(a):
        df2[str(6000+i)]=df2[df2.columns[i]]**2

    df2.fillna(0)
    df2 = df2.replace([np.inf,-np.inf],0)
    return df2


# In[8]:

def dataframe_components(df2,lon,columns):

    import numpy as np
    import pandas as pd
    from sklearn import tree
    from sklearn import metrics
    from sklearn import cross_validation
    import matplotlib.pyplot as plt
    
    from sklearn.decomposition import PCA as sklearnPCA
    X=df2.values
    from sklearn.preprocessing import StandardScaler
    X_std = StandardScaler().fit_transform(X)
    pca=sklearnPCA(n_components=lon).fit_transform(X_std)
    list_comp_pca=[]


    # CREACCION DATAFRAME CON COMPONENTES PRINCIPALES

    for i in range(0,lon):
        v="Componente"+str(i)
        list_comp_pca.append(v)

    dd1=pd.DataFrame(X_std,columns=columns)
    dd2=pd.DataFrame(pca,columns=list_comp_pca)
    df3=pd.concat([dd1,dd2],axis=1)
    return df3


# In[9]:

def variables_exp_componente(prof_elegida,componente,df3,columns):

    import numpy as np
    import pandas as pd
    from sklearn import tree
    from sklearn import metrics
    from sklearn import cross_validation
    import matplotlib.pyplot as plt
    
    
    # semilla
    seed=120419
    
    clf1 = tree.DecisionTreeRegressor(max_depth=prof_elegida,random_state=seed)
    df3_train,df3_test=cross_validation.train_test_split(df3,train_size=0.63,random_state=seed)
    clf1.fit(df3_train.ix[:,0:215],df3_train[[componente]])
    importances=clf1.feature_importances_
    max1_pos=np.argmax(importances)
    importances[max1_pos]=-2732
    max2_pos=np.argmax(importances)
    importances[max2_pos]=-2732
    max3_pos=np.argmax(importances)
    importances[max3_pos]=-2732
    max4_pos=np.argmax(importances)

    print "Primera variable que mejor explica la componente es:",columns[max1_pos]
    print "Segunda variable que mejor explica la componente es:",columns[max2_pos]
    print "Tercera variable que mejor explica la componente es:",columns[max3_pos]


# In[15]:

def entrenamiento_error(df,componente_elegida):
    
    
    import numpy as np
    import pandas as pd
    from sklearn import tree
    from sklearn import metrics
    from sklearn import cross_validation
    import matplotlib.pyplot as plt
    
     
    
    if type(componente_elegida)!=str:
        print "componente_elegida debe de ser cadena"
    
    if componente_elegida=="1":
        componente=len(df.columns)
        print "IMPRIMIENDO PARA PRIMERA COMPONENTE"
    
    elif componente_elegida=="2":
        componente=(len(df.columns)+1)
        print "IMPRIMIENDO PARA SEGUNDA COMPONENTE"
    
    lon=len(df.columns)
    columns=df.columns
    df3=dataframe_components(df,lon,columns)
    
    # semilla
    seed=120419

    # Lista profundiades del arbol de decisión
    profundidades=[1,2,3]

    #inicializacion de vectores de error

    arr_error_train_fin=np.zeros(len(profundidades),dtype=float)
    arr_error_test_fin=np.zeros(len(profundidades),dtype=float)


    for r in range(0,75):

        print "Iteracción:",r
        df3_train,df3_test=cross_validation.train_test_split(df3,train_size=0.7)

        list_error_test=[]
        list_error_train=[]
        for d in profundidades:

            # ENTRENAMIENTO
            clf = tree.DecisionTreeRegressor(max_depth=d)
            clf.fit(df3_train.ix[:,0:componente],df3_train[[componente]])

            # PREDICTION EN EL TRAIN
            y_pred_train=clf.predict(df3_train.ix[:,0:componente])
            error=metrics.mean_squared_error(df3_train[[componente]],y_pred_train)
            list_error_train.append(error)

            # PREDICTION EN EL TEST
            y_pred_test=clf.predict(df3_test.ix[:,0:componente])
            error=metrics.mean_squared_error(df3_test[[componente]],y_pred_test)
            list_error_test.append(error)

        arr_error_train=np.array(list_error_train)
        arr_error_train_fin=(arr_error_train_fin+arr_error_train)/(r+1)

        arr_error_test=np.array(list_error_test)
        arr_error_test_fin=(arr_error_test_fin+arr_error_test)/(r+1)



    #PLOT DE ERRORES EN TRAIN Y TEST
    plt.subplot(121)
    plt.title("ERROR TEST")
    plt.xlabel('Profundidad')
    plt.ylabel('MSE')
    plt.plot(profundidades,arr_error_test_fin,color="r")

    plt.subplot(122)
    plt.title("ERROR TRAIN")
    plt.xlabel('Profundidad')
    plt.plot(profundidades,arr_error_train_fin,color="b")
    
    prof_elegida=np.argmin(arr_error_test_fin)+1
    print "La profundidad elegida es:",prof_elegida
    variables_exp_componente(prof_elegida,componente,df3,columns)

