def limpiezaDeDatos(df):
    import pandas as pd
    import numpy as np
    
    #Eliminamos la variable objetivo de los datos a limpiar, así como la variable ID
    df.columns = [x.lower() for x in df.columns]
    objetivo = [col for col in df.columns if 'target' in col]
    objetivo = ''.join(objetivo)

    dfBorrar = df[['id', objetivo]]
    borrar = ['id', objetivo]
    dfaux = df.drop(borrar, axis=1)
    
    for col in range(1,len(dfaux.columns)-1):
        # Sustituimos los valores NaN por la mediana
        dfaux.ix[:,col]=dfaux.ix[:,col].fillna(dfaux.ix[:,col].median())
        
    for column in dfaux.columns:
        #Sustituimos los valores fuera de rango por la mediana si la columna es numérica o con la moda

        if dfaux[column].dtypes == 'int64' or dfaux[column].dtypes == 'float64':
            media = dfaux[column].mean()
            desv = 1.5*dfaux[column].std()
            dfaux[column] = dfaux[column].apply(lambda y: dfaux[column].median() if(abs(y - media >desv)) else y)

            filas = len(dfaux.columns)
            negative_perc = np.sum((dfaux[column] < 0))/filas
            dfaux[column] = dfaux[column].apply(lambda y: -(y) if (y<0 and negative_perc >= 0.05) else y)

            # Transforma los string en numerico.
        if str(dfaux[column].values.dtype) == 'object':
            columna = LabelEncoder().fit(dfaux[column].values)
            dfaux[column] = columna.transform(dfaux[column].values)

    #Volvemos a añadir las columnas que habiamos eliminado.
    dfLimpio = pd.concat([dfBorrar, dfaux], axis=1)
    dfLimpio.to_csv("dfLimpio.csv")

    return dfLimpio
