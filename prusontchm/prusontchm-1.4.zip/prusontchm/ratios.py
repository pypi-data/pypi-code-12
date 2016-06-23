def div0( a, b ):
    import numpy as np
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide( a, b )
        c[ ~ np.isfinite( c )] = a.max()  # -inf inf NaN
    return c
	
def NuevosRatios (df):
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    from sklearn import decomposition

    # Eliminamos antes del cálculo de los ratios las columnas target e id.
    
    df.columns = [x.lower() for x in df.columns]
    objetivo = [col for col in df.columns if 'target' in col]
    objetivo = ''.join(objetivo)

    dfBorrar = df[['id', objetivo]]
    borrar = ['id', objetivo]
    dfaux = df.drop(borrar, axis=1)

    numColumnas = len(dfaux.columns)
    columnas= dfaux.columns
    for ind in range(0,numColumnas) :
        for ind2 in range(0,numColumnas) :
            if(ind==ind2):
                 dfaux[columnas[ind]+"^2"] = dfaux[columnas[ind]]**2
            else:
                dfaux[columnas[ind]+"-"+columnas[ind2]]=dfaux[columnas[ind]]-dfaux[columnas[ind2]]
                dfaux[columnas[ind]+"/"+columnas[ind2]] =  div0(dfaux[columnas[ind]],dfaux[columnas[ind2]])
                dfaux["("+columnas[ind]+"-"+columnas[ind2]+")"+"/"+columnas[ind2]] = div0((dfaux[columnas[ind]]-dfaux[columnas[ind2]]),dfaux[columnas[ind2]])
                
                if ind<ind2:
                    dfaux[columnas[ind]+"+"+columnas[ind2]]=dfaux[columnas[ind]]+dfaux[columnas[ind2]]
                    dfaux[columnas[ind]+"*"+columnas[ind2]]=dfaux[columnas[ind]]*dfaux[columnas[ind2]]
    list_inputs = dfaux.columns    
    
    # Una vez terminado el cálculo de los ratios se añaden de nuevo las columnas target e id.
    
    dfVar = pd.concat([dfBorrar, dfaux], axis=1)
    
    return dfVar