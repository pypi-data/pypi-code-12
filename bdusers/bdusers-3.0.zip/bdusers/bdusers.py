from __future__ import division

def maindos(my_data_train_cv,my_data_test_cv):
    import pandas as pd
    import numpy as np
    from scipy import stats
    from datacleaner import autoclean_cv
    addtarget = my_data_train_cv.ix[:,-1]
    my_data_train_cv.drop(my_data_train_cv.columns[[-1]], axis=1, inplace=True)
    my_data_train_cv.drop(my_data_train_cv.columns[[0]], axis=1, inplace=True)
    my_data_test_cv.drop(my_data_test_cv.columns[[0]], axis=1, inplace=True)
    list_train_float64 = set()  #input float64
    list_train_int64 = set() #input int64
    list_train_category = set() #input category
    list_train_object = set() #input object
    list_train_bool = set() #input bool
    for var_name in my_data_train_cv.columns:
        if my_data_train_cv[var_name].dtype == np.float64:
            list_train_float64.add(var_name)
            # print var_name,"Float64"
        elif my_data_train_cv[var_name].dtype == np.int64:
            list_train_int64.add(var_name)
            # print var_name,"Int64"
        elif my_data_train_cv[var_name].dtype == np.object:
            list_train_object.add(var_name)
            # print var_name,"Object"
        elif my_data_train_cv[var_name].dtype == np.category:
            list_train_category.add(var_name)
            # print var_name,"Category"
        elif my_data_train_cv[var_name].dtype == np.bool:
            list_train_bool.add(var_name)
            # print var_name,"Bool"
        else:
            print var_name,"No encontrada tipologia"
    list_test_float64 = set()  #input float64
    list_test_int64 = set() #input int64
    list_test_category = set() #input category
    list_test_object = set() #input object
    list_test_bool = set() #input bool
    for var_name in my_data_test_cv.columns:
        if my_data_test_cv[var_name].dtype == np.float64:
            list_test_float64.add(var_name)
            # print var_name,"Float64"
        elif my_data_test_cv[var_name].dtype == np.int64:
            list_test_int64.add(var_name)
            # print var_name,"Int64"
        elif my_data_test_cv[var_name].dtype == np.object:
            list_test_object.add(var_name)
            # print var_name,"Object"
        elif my_data_test_cv[var_name].dtype == np.category:
            list_test_category.add(var_name)
            # print var_name,"Category"
        elif my_data_test_cv[var_name].dtype == np.bool:
            list_test_bool.add(var_name)
            # print var_name,"Bool"
        else:
            print var_name,"No encontrada tipologia"    
    autoclean_cv(my_data_train_cv, my_data_test_cv)
    my_data_train_cv["target"] = addtarget
    my_data_train_cv  = my_data_train_cv._get_numeric_data()
    my_data_test_cv  = my_data_test_cv._get_numeric_data()
    list_cat_train = set()  #input categorica
    list_nonCat_train = set() #input no categorica
    for var_name in my_data_train_cv.columns:
        if len(my_data_train_cv[var_name].unique()) <= 30:
            list_cat_train.add(var_name)
            # print var_name,"Categorica"
        else:
            list_nonCat_train.add(var_name)
            # print var_name,"No categorica"
    list_cat_test = set()  #input categorica
    list_nonCat_test = set() #input no categorica
    for var_name in my_data_test_cv.columns:
        if len(my_data_test_cv[var_name].unique()) <= 30:
            list_cat_test.add(var_name)
            # print var_name,"Categorica"
        else:
            list_nonCat_test.add(var_name)
            # print var_name,"No categorica"
    for var_name in list_nonCat_train:
        if var_name in list_train_float64 or list_train_int64:
            my_data_train_cv[var_name] = my_data_train_cv[var_name][(np.abs(stats.zscore(my_data_train_cv[var_name])) < 3)]
            my_data_train_cv = my_data_train_cv.fillna(my_data_train_cv.mean())
    for var_name in list_nonCat_test:
        if var_name in list_test_float64 or list_test_int64:
            my_data_test_cv[var_name] = my_data_test_cv[var_name][(np.abs(stats.zscore(my_data_test_cv[var_name])) < 3)]
            my_data_test_cv = my_data_test_cv.fillna(my_data_test_cv.mean())
    print("La limpieza de datos ha finalizado correctamente")
    return;

def mainuno(my_data_train_cv):
    import pandas as pd
    import numpy as np
    from scipy import stats
    from datacleaner import autoclean
    my_data_train_cv.drop(my_data_train_cv.columns[[0]], axis=1, inplace=True)
    list_train_float64 = set()  #input float64
    list_train_int64 = set() #input int64
    list_train_category = set() #input category
    list_train_object = set() #input object
    list_train_bool = set() #input bool
    for var_name in my_data_train_cv.columns:
        if my_data_train_cv[var_name].dtype == np.float64:
            list_train_float64.add(var_name)
            # print var_name,"Float64"
        elif my_data_train_cv[var_name].dtype == np.int64:
            list_train_int64.add(var_name)
            # print var_name,"Int64"
        elif my_data_train_cv[var_name].dtype == np.object:
            list_train_object.add(var_name)
            # print var_name,"Object"
        elif my_data_train_cv[var_name].dtype == np.category:
            list_train_category.add(var_name)
            # print var_name,"Category"
        elif my_data_train_cv[var_name].dtype == np.bool:
            list_train_bool.add(var_name)
            # print var_name,"Bool"
        else:
            print var_name,"No encontrada tipologia" 
    autoclean(my_data_train_cv)
    my_data_train_cv  = my_data_train_cv._get_numeric_data()
    list_cat_train = set()  #input categorica
    list_nonCat_train = set() #input no categorica
    for var_name in my_data_train_cv.columns:
        if len(my_data_train_cv[var_name].unique()) <= 30:
            list_cat_train.add(var_name)
            # print var_name,"Categorica"
        else:
            list_nonCat_train.add(var_name)
            # print var_name,"No categorica"
    for var_name in list_nonCat_train:
        if var_name in list_train_float64 or list_train_int64:
            my_data_train_cv[var_name] = my_data_train_cv[var_name][(np.abs(stats.zscore(my_data_train_cv[var_name])) < 3)]
            my_data_train_cv = my_data_train_cv.fillna(my_data_train_cv.mean())
    print("La limpieza de datos ha finalizado correctamente")
    return;

def create_good_2var(my_data_train_cv,my_data_test_cv):
##Insertamos las librerias que necesitamos:
    import pandas
    import scipy.stats
    from sklearn import metrics
    import math
    import os
    import itertools
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import scale
    import pandas as pd
    import numpy as np
    from scipy import stats
    #from __future__ import division
    #from datacleaner import autoclean_cv
    from sklearn.ensemble import RandomForestClassifier
    from deap import creator, base, tools, algorithms
    
    ##Una vez leemos el csv quitamos la columna id y la target, que será la última columna del dataset
    df1 = my_data_train_cv
    df1o = my_data_test_cv
    print("Se han asignado correctamente las variables")
    addtarget = my_data_train_cv[[-1]]
    id_train = my_data_train_cv[[0]]
    id_test = my_data_test_cv[[0]]
    df = my_data_train_cv.drop(my_data_train_cv.columns[[-1]], axis=1)
    df = my_data_train_cv.drop(my_data_train_cv.columns[[0]], axis=1)
    dfo = my_data_test_cv.drop(my_data_test_cv.columns[[0]], axis=1)
    print("Se han eliminado la primera y ultima columna para crear variables")
    
    var_names = list(df.columns.values)
    longitud = len(df.columns)
    var_nameso = list(dfo.columns.values)
    longitudo = len(dfo.columns)

    ####Vamos a crear las todas las variables posibles:
    #otra forma de plantear los bucles:  X+Y
    for i in range(longitud):
        for j in range(i,longitud):
            df[var_names[i]+'+'+var_names[j]]=df.ix[:,i]+df.ix[:,j]
            
    #X*Y
    for i in range(0,longitud):
        for j in range(0,longitud):
            df[var_names[i]+'*'+var_names[j]]= df[df.columns[i]] * df[df.columns[j]]
            

    #X-Y
    for i in range(0,longitud):
        for j in range(0,longitud):
            df[var_names[i]+'-'+var_names[j]]= df[df.columns[i]] - df[df.columns[j]]
            

    #X/Y
    for i in range(0,longitud):
        for j in range(0,longitud):
            if i!=j:
                df[var_names[i]+'/'+var_names[j]] = np.where(df[df.columns[j]] == 0,0, df[df.columns[i]]/df[df.columns[j]])        

    #(X-Y)/Y
    for i in range(0,longitud):
        for j in range(0,longitud):
            if i!=j:
                df['('+var_names[i]+'-'+var_names[j]+')/'+var_names[j]] = np.where(df[df.columns[j]] == 0,0, (df[df.columns[i]]-df[df.columns[j]])/df[df.columns[j]])        

                
    #X^2
    for i in range(longitud):
        df[var_names[i]+'^2']= df[df.columns[i]] * df[df.columns[i]]
        
    ###############creamos las variables para el conjunto de test:
    ####Vamos a crear las todas las variables posibles:
    #otra forma de plantear los bucles:  X+Y
    for i in range(longitudo):
        for j in range(i,longitudo):
            dfo[var_nameso[i]+'+'+var_nameso[j]]=dfo.ix[:,i]+dfo.ix[:,j]
            
    #X*Y
    for i in range(0,longitudo):
        for j in range(0,longitudo):
            dfo[var_nameso[i]+'*'+var_nameso[j]]= dfo[dfo.columns[i]] * dfo[dfo.columns[j]]
            

    #X-Y
    for i in range(0,longitudo):
        for j in range(0,longitudo):
            dfo[var_nameso[i]+'-'+var_nameso[j]]= dfo[dfo.columns[i]] - dfo[dfo.columns[j]]
            

    #X/Y
    for i in range(0,longitudo):
        for j in range(0,longitudo):
            if i!=j:
                dfo[var_nameso[i]+'/'+var_nameso[j]] = np.where(dfo[dfo.columns[j]] == 0,0, dfo[dfo.columns[i]]/dfo[dfo.columns[j]])        

    #(X-Y)/Y
    for i in range(0,longitudo):
        for j in range(0,longitudo):
            if i!=j:
                dfo['('+var_nameso[i]+'-'+var_nameso[j]+')/'+var_nameso[j]] = np.where(dfo[dfo.columns[j]] == 0,0, (dfo[dfo.columns[i]]-dfo[dfo.columns[j]])/dfo[dfo.columns[j]])        

                
    #X^2
    for i in range(longitudo):
        dfo[var_nameso[i]+'^2']= dfo[dfo.columns[i]] * dfo[dfo.columns[i]]
    
    len(df.columns)
    
    print 'CREADAS', len(df.columns), 'VARIABLES'

    #####limpiamos los nan que se creen en las divisiones:
    df.fillna(df.mean(),inplace = True)
    df = df.replace([np.inf,-np.inf],0)

    dfo.fillna(dfo.mean(),inplace = True)
    dfo = dfo.replace([np.inf,-np.inf],0)
    ##Procedemos a aplicar PCA a las variables construidas para agruparlas según informen.
    X=df.values
    X = scale(X)
    pca=PCA(n_components=len(df.columns)).fit_transform(X)
    #n=len(pca)

    df_pca= pd.DataFrame(data = pca[::], index=list(range(0,len(pca))))
    print("Aplicamos PCA a las variables creadas anteriormente")
    
    X = df[df.columns]
    y = df_pca

    # Calculamos el número de componentes:
    num_pca = len(df_pca)
    n = int(num_pca/100)

    # Aplicamos el arbol de decisión donde X = Dataframe con los ratios creados e Y = Componentes Principales:
    # Generamos un árbol por cada uno de los componentes principales. Para cada uno de ellos obtenemos las principales
    # ratios

    list_features = []
    ###se deberían hacer para todas las componentes pero es muy costoso computacionalmente
    for i in range(0,n):
        dt = DecisionTreeRegressor(max_depth=3)
        dt_fit = dt.fit(X, df_pca[i])
        feature = dt_fit.tree_.feature
        feature = feature.tolist()
        list_features.append(feature)

    print("Se aplica Decision Tree sobre las componentes seleccionadas")
   
    # Transformamos la lista de listas en una única lista que contiene los números de los RATIOS importantes.
    # Eliminamos los duplicados y los valores negativos. Finalmente ordenamos la lista de menor a mayor:
    import itertools
    list_features = list(itertools.chain.from_iterable(list_features))
    list_unicos = list(set(list_features))
    list_pos = [x for x in list_unicos if x >= 0 ]
    list_pos.sort()

    print 'SELECCIONADOS', len(list_pos), 'RATIOS'

    # Creamos el df con los ratios buenos. A partir del número de ratios lo buscamos en el df de ratios.
    # Para ello creamos una lista donde almancenamos los nombres de los ratios que queremos.
    # A partir de esa lista generamos un df con los ratios buenos.
    # Finalmente extraemos la variable target y la incluimos en el df junto con los ratios:

    list_names = []
    list_nameso = []

    for i in range(0, len(list_pos)):
        list_names.append(df.columns[list_pos[i]])
    for i in range(0, len(list_pos)):
        list_nameso.append(dfo.columns[list_pos[i]])

        
    df_ratios_sel = df[list_names]
    df_ratios_selo = dfo[list_names]
    df_target = addtarget
    df_id = id_train
    df_ido = id_test
    df_final = pd.concat([df_id,df_ratios_sel,df_target], axis=1)
    df_final_o = pd.concat([df_ido,df_ratios_selo],axis=1)
    print 'MODIFICADO DATAFRAME CON LOS RATIOS SELECCIONADOS'
    df_final
    df_final_o
    
    print 'Se han generado los dataset'

    #print my_data_test_cv.head()
    #print my_data_train_cv.head()
    return df_final, df_final_o ;

def create_good_1var(my_data_train_cv):
##Insertamos las librerias que necesitamos:
    import pandas
    import scipy.stats
    from sklearn import metrics
    import math
    import os
    import itertools
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import scale
    import pandas as pd
    import numpy as np
    from scipy import stats
    #from __future__ import division
    #from datacleaner import autoclean_cv
    from sklearn.ensemble import RandomForestClassifier
    from deap import creator, base, tools, algorithms
    
    ##Una vez leemos el csv quitamos la columna id y la target, que será la última columna del dataset
    df1 = my_data_train_cv
    print("Se han asignado correctamente las variables")
    addtarget = my_data_train_cv[[-1]]
    id_train = my_data_train_cv[[0]]
    df = my_data_train_cv.drop(my_data_train_cv.columns[[-1]], axis=1)
    df = my_data_train_cv.drop(my_data_train_cv.columns[[0]], axis=1)
    print("Se han eliminado la primera y ultima columna para crear variables")
    
    var_names = list(df.columns.values)
    longitud = len(df.columns)
    
    ####Vamos a crear las todas las variables posibles:
    #otra forma de plantear los bucles:  X+Y
    for i in range(longitud):
        for j in range(i,longitud):
            df[var_names[i]+'+'+var_names[j]]=df.ix[:,i]+df.ix[:,j]
            
    #X*Y
    for i in range(0,longitud):
        for j in range(0,longitud):
            df[var_names[i]+'*'+var_names[j]]= df[df.columns[i]] * df[df.columns[j]]
            

    #X-Y
    for i in range(0,longitud):
        for j in range(0,longitud):
            df[var_names[i]+'-'+var_names[j]]= df[df.columns[i]] - df[df.columns[j]]
            

    #X/Y
    for i in range(0,longitud):
        for j in range(0,longitud):
            if i!=j:
                df[var_names[i]+'/'+var_names[j]] = np.where(df[df.columns[j]] == 0,0, df[df.columns[i]]/df[df.columns[j]])        

    #(X-Y)/Y
    for i in range(0,longitud):
        for j in range(0,longitud):
            if i!=j:
                df['('+var_names[i]+'-'+var_names[j]+')/'+var_names[j]] = np.where(df[df.columns[j]] == 0,0, (df[df.columns[i]]-df[df.columns[j]])/df[df.columns[j]])        

                
    #X^2
    for i in range(longitud):
        df[var_names[i]+'^2']= df[df.columns[i]] * df[df.columns[i]]
        
    
    len(df.columns)
    
    print 'CREADAS', len(df.columns), 'VARIABLES'

    #####limpiamos los nan que se creen en las divisiones:
    df.fillna(df.mean(),inplace = True)
    df = df.replace([np.inf,-np.inf],0)

    ##Procedemos a aplicar PCA a las variables construidas para agruparlas según informen.
    X=df.values
    X = scale(X)
    pca=PCA(n_components=len(df.columns)).fit_transform(X)
    #n=len(pca)

    df_pca= pd.DataFrame(data = pca[::], index=list(range(0,len(pca))))
    print("Aplicamos PCA a las variables creadas anteriormente")
    
    X = df[df.columns]
    y = df_pca

    # Calculamos el número de componentes:
    num_pca = len(df_pca)
    n = int(num_pca/100)

    # Aplicamos el arbol de decisión donde X = Dataframe con los ratios creados e Y = Componentes Principales:
    # Generamos un árbol por cada uno de los componentes principales. Para cada uno de ellos obtenemos las principales
    # ratios

    list_features = []
    ###se deberían hacer para todas las componentes pero es muy costoso computacionalmente
    for i in range(0,n):
        dt = DecisionTreeRegressor(max_depth=3)
        dt_fit = dt.fit(X, df_pca[i])
        feature = dt_fit.tree_.feature
        feature = feature.tolist()
        list_features.append(feature)

    print("Se aplica Decision Tree sobre las componentes seleccionadas")
   
    # Transformamos la lista de listas en una única lista que contiene los números de los RATIOS importantes.
    # Eliminamos los duplicados y los valores negativos. Finalmente ordenamos la lista de menor a mayor:
    import itertools
    list_features = list(itertools.chain.from_iterable(list_features))
    list_unicos = list(set(list_features))
    list_pos = [x for x in list_unicos if x >= 0 ]
    list_pos.sort()

    print 'SELECCIONADOS', len(list_pos), 'RATIOS'

    # Creamos el df con los ratios buenos. A partir del número de ratios lo buscamos en el df de ratios.
    # Para ello creamos una lista donde almancenamos los nombres de los ratios que queremos.
    # A partir de esa lista generamos un df con los ratios buenos.
    # Finalmente extraemos la variable target y la incluimos en el df junto con los ratios:

    list_names = []
    

    for i in range(0, len(list_pos)):
        list_names.append(df.columns[list_pos[i]])
    
        
    df_ratios_sel = df[list_names]
    
    df_target = addtarget
    df_id = id_train
    
    df_final = pd.concat([df_id,df_ratios_sel,df_target], axis=1)
    
    print 'MODIFICADO DATAFRAME CON LOS RATIOS SELECCIONADOS'
    df_final
    
    
    print 'Se ha generado el dataset'

    return df_final;