# Limpieza automatizada de datos; identificar los valores y/o filas no validas y resolver automaticamente el problema, 
# sea el NaN, falta de datos, valores atipicos, valores poco fiables, fuera del rango.

import pandas as pd
import numpy as np

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
