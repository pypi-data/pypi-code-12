

def limpieza(df):
    
    import numpy as np
    import pandas as pd
    import math
    print "------------------------------------------------------------------------------------------"
    print "------------------------------VALORES DE LAS VARIABLES------------------------------------"
    print "------------------------------------------------------------------------------------------"
    print "\n"
    columna=0
    for i in df.columns:
        print "------------------VALORES DE",i,", columna",columna,"---------------------------------"
        print np.unique(df[i],return_counts=True)
        valores=np.unique(df[i],return_counts=True)[0]
        repeticiones=np.unique(df[i],return_counts=True)[1]
        maximo_registro=valores[np.argmax(repeticiones)]
        print "\n"
        print "máximo registro",maximo_registro
        columna+=1
        print "------------------------------------------------------------------------------------"
    print "\n"
    print "----------------------------------------------------------------------------------------"
    print "----------------------------------------------------------------------------------------"
    print "----------------------------------------------------------------------------------------"
    print "\n"
        
    ### Valores NAN
    #Eliminar filas sin registros y sustituir NaNs por máximos registros
    print "----------------------------------------------------------------------------------------"
    print "-----------------------Localización y tratamiento de NANs-------------------------------"
    print "----------------------------------------------------------------------------------------"
    print "\n"
    
    filas1=np.shape(df)[0]
    df.dropna(axis=0,thresh=0)
    filas2=np.shape(df)[0]
    print "Se han eliminado",filas1-filas2,"filas con todos sus registros nan"
    print "------------------------------------------------------------------"

    df=df.fillna(value=-500)
    for i in range(0,np.shape(df)[1]):
        a=df[df.ix[:,i]==-500]
        print "En la variable",a.columns[i],"existen nans en las filas \n",a.ix[:,i]
        print "En total son",len(a.ix[:,i]),"nans"
        print "-------------------------------------------------------------------------\n"

    columna=0
    for i in df.columns:
        print "------------------VALORES DE",i,", columna",columna,"---------------------------------"
        valores=np.unique(df[i],return_counts=True)[0]
        repeticiones=np.unique(df[i],return_counts=True)[1]
        print "valores",valores
        print "repeticiones",repeticiones
        maximo_registro=valores[np.argmax(repeticiones)]
        print "máximo registro",maximo_registro
        a=df.ix[:,i]
        a=a.replace(-500,maximo_registro)
        df.ix[:,i]=a

        columna+=1
        print "------------------------------------------------------------------------------------"
    
    print "\n"
    print "----------------------------------------------------------------------------------------"
    print "------------------IDENTIFICACIÓN DE VALORES ATÍPICOS O FUERA DE RANGO-------------------"
    print "----------------------------------------------------------------------------------------"
    print "\n"

    for i in range(len(df.columns)):
        if type(df.ix[0,i])!=str:       
            q3=np.percentile(df.ix[:,i],75)
            q1=np.percentile(df.ix[:,i],25)
            iqr=q3-q1
            li=q1-1.5*iqr
            ls=q3+1.5*iqr
            print "Rango intercuartílico de",df.columns[i],iqr,"con li",li,"y ls",ls
            a=df[df.ix[:,i]>ls]
            print "ELEMENTOS POR ENCIMA DE ls:",len(a[[i]]),"\n","Los valores",np.unique(a[[i]],return_counts=True)[0],"repetidos",np.unique(a[[i]],return_counts=True)[1],"veces \n"
            b=df[df.ix[:,i]<li]
            print "ELEMENTOS POR DEBAJO DE li:",len(b[[i]]),"\n","Los valores",np.unique(b[[i]],return_counts=True)[0],"repetidos",np.unique(b[[i]],return_counts=True)[1],"veces \n"   
            print "---------------------------------------------------------------------------------------------------"

