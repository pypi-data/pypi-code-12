# Limpieza automatizada de datos; identificar los valores y/o filas no validas y resolver automaticamente el problema, 
# sea el NaN, falta de datos, valores atipicos, valores poco fiables, fuera del rango.

import pandas as pd
import numpy as np
import sklearn as sk 
from math import sqrt 
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression



def limpiaDataFrame(dataFrame):
    columnas = len(dataFrame.columns)
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    for i in range(columnas):
        if dataFrame[[i]].dtypes[0] in numerics:
            dataFrame[dataFrame.columns.values[i]] = rellenarNulos(dataFrame[[i]])
            
    return dataFrame



def rellenarNulos(columnaDataFrame):
    # Si estoy por encima del rango pongo el maximo
    # Si estoy por debajo del rango o el valor en null, pongo el minimo
    # Para calcular el rango y dejar fuera los posibles outliers marco como min y max los cuartiles 1 y 3
    minimo = np.nanpercentile(columnaDataFrame, 25)
    maximo = np.nanpercentile(columnaDataFrame, 75)
    RIC = maximo - minimo
    minimo = max(minimo - RIC * 1.5, columnaDataFrame.min()[0])
    maximo = min(maximo + RIC * 1.5,columnaDataFrame.max()[0])
    columnaDataFrame = columnaDataFrame.fillna(minimo)
    columnaDataFrame.loc[columnaDataFrame[list(columnaDataFrame.columns.values)[0]] > maximo,columnaDataFrame.columns] = maximo
    columnaDataFrame.loc[columnaDataFrame[list(columnaDataFrame.columns.values)[0]] < minimo,columnaDataFrame.columns] = minimo

    return columnaDataFrame


def RatioSeleccion(entreno, entrenoTarget, testeo):
    estimador = len(entreno.columns)
    entrenar = crearRatios(entreno)
    testear = crearRatios(testeo)
    entrenar2, testeo2 = seleccionPCA(entrenar,testear,estimador)
    testeo3 = seleccionRFR(entrenar2,entrenoTarget,testeo2,estimador)
    
    return testeo3, entrenar2, testeo2



def seleccionPCA(entrenar,testear,estimadores):

    # Buscamos las variables principales del dataFrame
    X = entrenar.values
    X = scale(X)
    pca = PCA(n_components = estimadores).fit(X)
    transaformed_data = pca.transform(entrenar)
    transaformed_data_test = pca.transform(testear)
    transaformed_data = pd.DataFrame(transaformed_data, columns = entrenar.columns[0:estimadores])
    transaformed_data_test = pd.DataFrame(transaformed_data_test, columns = testear.columns[0:estimadores])
    
    return transaformed_data,transaformed_data_test


def seleccionRFR(entreno, entrenoTarget,testear,estimadores):    
    
    X = entreno
    y = entrenoTarget
    Xo = testear   
    
    model = sk.ensemble.RandomForestRegressor(n_estimators = estimadores)
    result = model.fit(X,y)
    yo_pred = result.predict(Xo)   
    
    return yo_pred
    
def crearRatios(dataFrame):
    df = dataFrame
    columnas = len(df.columns)
    nombreColumna = list(df.columns.values)
    for i in range(columnas):
        # X^2
        nombre = "SQRT_" + str(i)
        df[nombre] = df[nombreColumna[i]]+df[nombreColumna[i]]
        for j in range(i+1, columnas):
            # X+Y
            nombre = "Suma_" + str(i) + "_" + str(j)
            df[nombre] = df[nombreColumna[i]]+df[nombreColumna[j]]
            # X-Y
            nombreR = "Resta_" + str(i) + "_" + str(j)
            df[nombreR] = df[nombreColumna[i]]-df[nombreColumna[j]]
            # X*Y
            nombre = "Multi_" + str(i) + "_" + str(j)
            df[nombre] = df[nombreColumna[i]]*df[nombreColumna[j]]
            
            # Si el divisor es cero mantenemos el dividendo
            # X/Y
            nombre = "Div_" + str(i) + "_" + str(j)
            df[nombre] = np.where(df[nombreColumna[j]]==0,df[nombreColumna[i]],df[nombreColumna[i]]/df[nombreColumna[j]])
            # (X-Y)/Y
            nombre = "Propor_" + str(i) + "_" + str(j)
            df[nombre] = np.where(df[nombreColumna[j]]==0,df[nombreR],df[nombreR]/df[nombreColumna[j]])
            
    return df


def algStepwise(x_train, x_test, y_train, y_test):

    # Modelo para realizar los ajustes
    model = LinearRegression()
    features = list(x_train.columns)
    
    # Variable para almecena los indices de la lista de atributos usados
    feature_order =  []
    feature_error = []

    # Iteracion sobre todas las variables
    for i in range(len(features)):
        idx_try = [val for val in range(len(features)) if val not in feature_order]

        iter_error = []

        for i_try in idx_try:
            useRow = feature_order[:]
            useRow.append(i_try)

            use_train = x_train[x_train.columns[useRow]]
            use_test = x_test[x_train.columns[useRow]]

            model.fit(use_train, y_train)
            rmsError = np.linalg.norm((y_test - model.predict(use_test)), 2)/sqrt(len(y_test))
            iter_error.append(rmsError)

        pos_best = np.argmin(iter_error)
        feature_order.append(idx_try[pos_best])
        feature_error.append(iter_error[pos_best])
    
    ratios = []
    
    for i in range(len(features)):
        ratios.append(features[feature_order[i]])
    
    return ratios
