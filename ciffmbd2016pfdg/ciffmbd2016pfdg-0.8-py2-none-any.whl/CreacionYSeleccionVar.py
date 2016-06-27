### Creacion de ration nuevos: suma, resta, multiplicacion, division, cuadrado y relativo
### Calculo del PCA y Random Forest para la seleccion de las mejores variables

import pandas as pd
import numpy as np
import sklearn as sk 
from math import sqrt 
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor


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
