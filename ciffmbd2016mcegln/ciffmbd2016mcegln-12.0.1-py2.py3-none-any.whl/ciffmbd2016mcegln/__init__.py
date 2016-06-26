# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import statsmodels.api as stats
import re
import requests
import random
import math

import scipy.stats
from scipy import stats as scistats

from deap import creator, base, tools, algorithms
import urllib2
import os
import os.path
import time

from sklearn.metrics import roc_auc_score, explained_variance_score, mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_graphviz
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn import metrics

from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
from sklearn.datasets import make_classification
from sklearn.cross_validation import train_test_split

%matplotlib inline



def IdentificacionTipos (df, output_var):
    list_ib  = set() #input binary
    list_icn = set() #input categorical nominal
    list_ico = set() #input categorical ordinal
    list_if  = set() #input numerical continuos (input float)
    list_inputs = set()

    dfVars = pd.DataFrame(columns=('var_name', 'tipo', 'categoria', 'minimo', 'maximo', 'num_valores'))

    for i in range(1, len(df.columns)):
        var_name = df.columns[i]
        if (var_name != output_var):        
            list_inputs.add(var_name)         
            oUnique = df[var_name].unique()               
            iNumValores = len(oUnique)
            minimo = min(df[var_name])
            maximo = max(df[var_name])

            try:        
                sTipo = type(df[var_name][0])
                sCategoria = 'desconocido'

                if (iNumValores == 2 and ((oUnique == [0,1]).all() or (oUnique == [1,0]).all())):
                    list_ib.add(var_name)
                    sCategoria = 'ib'
                elif (iNumValores == 1 and ((oUnique == [1]).all() or (oUnique == [0]).all())):
                    list_ib.add(var_name)        
                    sCategoria = 'ib'        
                elif (sTipo == np.int64 and minimo < 5 and iNumValores < 30 and ((maximo - minimo)*0.8 < iNumValores) ):
                    list_icn.add(var_name)
                    sCategoria = 'ico'
                elif (sTipo == np.float64 or sTipo == np.int64):
                    list_if.add(var_name)
                    sCategoria = 'if'
                else:
                    sCategoria = 'desconocida'     
            except:
                sTipo = 'error'
                sCategoria = 'error'

            dfVars.loc[i] = [var_name, sTipo, sCategoria, minimo, maximo, iNumValores]

    return list_ib, list_icn, list_ico, list_if, list_inputs, dfVars


#LIMPIEZA DE DATOS: rellenar NaNs y valores fuera de rango
def LimpiezaDatos (df, dfo, output_var, list_inputs, list_if):    
    for var_name in df.columns:
        if (var_name in list_inputs):
            minimo = min(df[var_name])
            maximo = max(df[var_name])
            stddev = df[var_name].std()

            if (var_name in list_if):
                valormalo = df[df[output_var] == 1][var_name].mean()
                dfo.loc[dfo[var_name].isnull(), var_name] = valormalo
                dfo.loc[dfo[var_name] < (minimo - (stddev/10)), var_name] = valormalo            
                dfo.loc[dfo[var_name] > (maximo + (stddev/10)), var_name] = valormalo
            else:            
                valormalo = scistats.mode(df[df[output_var] == 1][var_name])[0][0]
                dfo.loc[dfo[var_name].isnull(), var_name] = valormalo
                dfo.loc[dfo[var_name] < minimo, var_name] = valormalo            
                dfo.loc[dfo[var_name] > maximo, var_name] = valormalo       
    
    return dfo



def CreacionRatios (df, dfo, output_var, list_inputs, list_if, iMaxRatios):
    print("Variable iniciales: " + str(len(df.columns)))
    iNumCols = len(df.columns)
    iNumRatios = 0

    for i in range(0, iNumCols):
        if (iNumRatios > iMaxRatios):
            break;
        vx = df.columns[i]

        if (vx in list_if and vx <> output_var):
            # x^2
            sNombre = 'ratioCuad#'+ vx
            df [sNombre] = df [vx] * df [vx]
            dfo[sNombre] = dfo[vx] * dfo[vx]
            list_inputs.add(sNombre)
            list_if.add(sNombre)
            iNumRatios = iNumRatios + 1

        for j in range(i+1, min(i+2, iNumCols)):
            vy = df.columns[j]    

            if (vx in list_if and vy in list_if):            
                # x+y
                sNombre = 'ratioSum#'+ vx + vy
                df [sNombre] = df [vx] + df [vy]
                dfo[sNombre] = dfo[vx] + dfo[vy]
                list_inputs.add(sNombre)
                list_if.add(sNombre)
                iNumRatios = iNumRatios + 1

                # (x-y)/y
                sNombre = 'ratioDif#'+ vx + vy
                df [sNombre] = np.where(df [vy]== 0, 0, (df [vx] - df [vy]) / df [vy])
                dfo[sNombre] = np.where(dfo[vy]== 0, 0, (dfo[vx] - dfo[vy]) / dfo[vy])
                list_inputs.add(sNombre)
                list_if.add(sNombre)
                iNumRatios = iNumRatios + 1

                # x*y
                sNombre = 'ratioMult#'+ vx + vy
                df [sNombre] = df [vx] * df [vy]
                dfo[sNombre] = dfo[vx] * dfo[vy]
                list_inputs.add(sNombre)
                list_if.add(sNombre)
                iNumRatios = iNumRatios + 1

                # x/y
                sNombre = 'ratioDiv#'+ vx + vy
                df [sNombre] = np.where(df [vy]== 0, 0, df [vx] / df [vy])
                dfo[sNombre] = np.where(dfo[vy]== 0, 0, dfo[vx] / dfo[vy])
                list_inputs.add(sNombre)
                list_if.add(sNombre)
                iNumRatios = iNumRatios + 1

                # x-y
                sNombre = 'ratioRest#'+ vx + vy
                df [sNombre] = df [vx] - df [vy]
                dfo[sNombre] = dfo[vx] - dfo[vy]
                list_inputs.add(sNombre)
                list_if.add(sNombre)
                iNumRatios = iNumRatios + 1

    print("Variable finales: " + str(len(df.columns)))
    
    return df, dfo, list_inputs, list_if



def Normalizacion (df, dfo, list_if):
    #NORMALIZACION DE VARIABLES
    for var_name in df.columns:
        if (var_name in list_if):
            media = df[df[var_name].notnull()][abs(df[var_name]) < np.inf][var_name].mean()
            desv  = df[df[var_name].notnull()][abs(df[var_name]) < np.inf][var_name].std()    

            if desv != 0:
                df [var_name] = (df [var_name] - media ) / desv               
                dfo[var_name] = (dfo[var_name] - media ) / desv     
                
    return df, dfo, list_if


def PCAexpand (df, dfo, output_var, id_var, iNumComponentes):
    #PCA
    dfId  = df [id_var]
    dfoId = dfo[id_var]

    dfObj  = df [output_var]
    if (output_var in dfo.columns):
        dfoObj = dfo[output_var]

    df.drop([id_var, output_var], axis=1, inplace=True)
    if (output_var in dfo.columns):
        dfo.drop([id_var, output_var], axis=1, inplace=True)
    else:
        dfo.drop([id_var], axis=1, inplace=True)

    pca = PCA(n_components = min(iNumComponentes, len(df.columns)))
    pca = pca.fit(df)

    arrTrans  = pca.transform(df)
    arroTrans = pca.transform(dfo)

    dfTrans  = pd.DataFrame(arrTrans,  columns=range(pca.n_components_))
    dfoTrans = pd.DataFrame(arroTrans, columns=range(pca.n_components_))
    
    dfc = pd.DataFrame((pca.components_.T)[4:10], df.columns[4:10]).T
    ax = dfc.plot(kind="bar", figsize=(24,12))
    
    dfp = pd.DataFrame(data=zip(df.columns, pca.explained_variance_ratio_), columns=["Feature", "Explained Variance Ratio"]).set_index("Feature")
    ax = dfp.sort("Explained Variance Ratio", ascending=1).plot(kind="barh", figsize=(12,6), log=0, label="")
    ax.grid()
    ax.set_xlabel("Explained Variance Ratio")
    ax.set_xlim(0,1)
    ax.set_ylabel("Features")

    dfp2 = pd.merge(dfp, dfp.cumsum(), right_index=True, left_index=True).rename(columns={"Explained Variance Ratio_x":"Explained Variance Ratio", "Explained Variance Ratio_y":"Cumulative"})
    ax = dfp2.sort("Explained Variance Ratio", ascending=1).plot(kind="barh", figsize=(12,6), log=0, label="")
    ax.set_xlabel("Explained Variance Ratio")
    ax.set_xlim(0,1)
    ax.set_ylabel("Features")

    model_rf = RandomForestClassifier()
    model_rf.fit(dfTrans, dfObj)

    yo_pred = model_rf.predict_proba(dfoTrans)

    df[id_var] = dfId
    df[output_var] = dfObj

    dfo[id_var] = dfoId
    dfo[output_var] = dfoObj

    dfTrans[id_var] = dfId
    dfTrans[output_var] = dfObj

    dfoTrans[id_var] = dfoId
    dfoTrans[output_var] = dfoObj

    df  = pd.merge(df,  dfTrans)
    dfo = pd.merge(dfo, dfoTrans)
        
    return df, dfo


def GeneticFeatureSelection (df, dfo, output_var, list_inputs, iNumEstimators):
    #####
    #SETING UP THE GENETIC ALGORITHM and CALCULATING STARTING POOL (STARTING CANDIDATE POPULATION)
    #####
    in_model = []
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=len(list_inputs))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    def evalOneMax(individual):
        return sum(individual),

    toolbox.register("evaluate", evalOneMax)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    NPOPSIZE = 30 #RANDOM STARTING POOL SIZE
    population = toolbox.population(n=NPOPSIZE)


    #####
    #ASSESSING GINI ON THE STARTING POOL
    #####
    dic_gini={}
    for i in range(np.shape(population)[0]): 

        # TRASLATING DNA INTO LIST OF VARIABLES (1-81)
        var_model = []    
        for j in range(np.shape(population)[0]): 
            if (population[i])[j]==1:
                var_model.append(list(list_inputs)[j])

        # ASSESSING GINI INDEX FOR EACH INVIVIDUAL IN THE INITIAL POOL 
        X_train = df[var_model]
        Y_train = df[output_var]

        if (output_var in dfo.columns):
            Xo_train = dfo[var_model]
            Yo_train = dfo[output_var]

        ######
        # CHANGE_HERE - START: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
        #####             
        model = RandomForestRegressor(n_estimators=iNumEstimators, max_depth=None).fit(X_train, Y_train)
        Y_predict  = model.predict(X_train)
        if (output_var in dfo.columns):
            Yo_predict = model.predict(Xo_train)

        ######
        # CHANGE_HERE - END: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
        #####             


        ######
        # CHANGE_HERE - START: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
        #####                
        fpr, tpr, thresholds = metrics.roc_curve(Y_train, Y_predict)
        auc = metrics.auc(fpr, tpr)
        gini_power_dev = abs(2*auc-1)

        if (output_var in dfo.columns):
            fpr, tpr, thresholds = metrics.roc_curve(Yo_train, Yo_predict)
            auc = metrics.auc(fpr, tpr)
            gini_power_oot = abs(2*auc-1)

            gini_power = math.sqrt(gini_power_dev * gini_power_oot)
        else:
            gini_power = gini_power_dev

        ######
        # CHANGE_HERE - END: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
        #####                

        gini=str(gini_power)+";"+str(population[j]).replace('[','').replace(', ','').replace(']','')
        dic_gini[gini]=population[j]   
    list_gini=sorted(dic_gini.keys(),reverse=True)



    #####
    #GENETIC ALGORITHM MAIN LOOP - START
    # - ITERATING MANY TIMES UNTIL NO IMPROVMENT HAPPENS IN ORDER TO FIND THE OPTIMAL SET OF CHARACTERISTICS (VARIABLES)
    #####
    sum_current_gini=0.0
    sum_current_gini_1=0.0
    sum_current_gini_2=0.0
    first=0    
    OK = 1
    a=0
    while OK:  #REPEAT UNTIL IT DO NOT IMPROVE, AT LEAST A LITLE, THE GINI IN 2 GENERATIONS
        a=a+1
        print 'loop ', a
        OK=0

        ####
        # GENERATING OFFSPRING - START
        ####
        offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1) #CROSS-X PROBABILITY = 50%, MUTATION PROBABILITY=10%
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population =toolbox.select(offspring, k=len(population))
        ####
        # GENERATING OFFSPRING - END
        ####

        sum_current_gini_2=sum_current_gini_1
        sum_current_gini_1=sum_current_gini
        sum_current_gini=0.0

        #####
        #ASSESSING GINI ON THE OFFSPRING - START
        #####
        for j in range(np.shape(population)[0]): 
            if population[j] not in dic_gini.values(): 
                var_model = [] 
                for i in range(np.shape(population)[0]): 
                    if (population[j])[i]==1:
                        var_model.append(list(list_inputs)[i])

                X_train = df[var_model]
                Y_train = df[output_var]

                if (output_var in dfo.columns):
                    Xo_train = dfo[var_model]
                    Yo_train = dfo[output_var]

                ######
                # CHANGE_HERE - START: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
                #####            
                model = RandomForestRegressor(n_estimators=iNumEstimators, max_depth=None).fit(X_train, Y_train)

                Y_predict  = model.predict(X_train)
                if (output_var in dfo.columns):
                    Yo_predict = model.predict(Xo_train)

                ######
                # CHANGE_HERE - END: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
                #####            


                ######
                # CHANGE_HERE - START: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
                #####                       
                fpr, tpr, thresholds = metrics.roc_curve(Y_train, Y_predict)
                auc = metrics.auc(fpr, tpr)
                gini_power_dev = abs(2*auc-1)

                if (output_var in dfo.columns):
                    fpr, tpr, thresholds = metrics.roc_curve(Yo_train, Yo_predict)
                    auc = metrics.auc(fpr, tpr)
                    gini_power_oot = abs(2*auc-1)

                    gini_power = math.sqrt(gini_power_dev * gini_power_oot)
                else:
                    gini_power = gini_power_dev

                ######
                # CHANGE_HERE - END: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
                #####                       

                gini=str(gini_power)+";"+str(population[j]).replace('[','').replace(', ','').replace(']','')
                dic_gini[gini]=population[j]  
        #####
        #ASSESSING GINI ON THE OFFSPRING - END
        #####

        #####
        #SELECTING THE BEST FITTED AMONG ALL EVER CREATED POPULATION AND CURRENT OFFSPRING - START
        #####           
        list_gini=sorted(dic_gini.keys(),reverse=True)
        population=[]
        for i in list_gini[:NPOPSIZE]:
            population.append(dic_gini[i])
            gini=float(i.split(';')[0])
            sum_current_gini+=gini
        #####
        #SELECTING THE BEST FITTED AMONG ALL EVER CREATED POPULATION AND CURRENT OFFSPRING - END
        #####           

        #HAS IT IMPROVED AT LEAST A LITLE THE GINI IN THE LAST 2 GENERATIONS
        print 'sum_current_gini=', sum_current_gini, 'sum_current_gini_1=', sum_current_gini_1, 'sum_current_gini_2=', sum_current_gini_2
        if(sum_current_gini>sum_current_gini_1+0.0001 or sum_current_gini>sum_current_gini_2+0.0001):
            OK=1
    #####
    #GENETIC ALGORITHM MAIN LOOP - END
    #####

    gini_max=list_gini[0]        
    gini=float(gini_max.split(';')[0])
    features=gini_max.split(';')[1]

    
    listFeatures = set()
    f=0
    for i in range(len(features)):
        if features[i]=='1':
            f+=1
            listFeatures.add(list(list_inputs)[i])

    return gini, listFeatures

