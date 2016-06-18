# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 13:23:49 2016

@author: ab
"""


def ga(data):
    import pandas as pd
    import numpy as np
    import re
    from deap import creator, base, tools, algorithms 
    import random
    from sklearn import metrics, linear_model

    #df = pd.read_csv("dev.csv") #DEV-SAMPLE
    #dfo = pd.read_csv("oot0.csv")#OUT-OF-TIME SAMPLE
    #df = pd.read_csv("/home/ab/Documents/MBD/financial_analytics/variable_creation/data/data.csv")
    #len(df.columns)
    
    in_model = []
    list_ib = set()  #input binary
    list_icn = set() #input categorical nominal
    list_ico = set() #input categorical ordinal
    list_if = set()  #input numerical continuos (input float)
    list_inputs = set()
    output_var = 'ob_target'
    
    for var_name in data.columns:
        if re.search('^ib_',var_name):
            list_inputs.add(var_name)      
            list_ib.add(var_name)
        elif re.search('^icn_',var_name):
            list_inputs.add(var_name)      
            list_icn.add(var_name)
        elif re.search('^ico_',var_name):
            list_inputs.add(var_name)      
            list_ico.add(var_name)
        elif re.search('^if_',var_name):
            list_inputs.add(var_name)      
            list_if.add(var_name)
        elif re.search('^ob_',var_name):
            output_var = var_name
    
    #####
    #SETING UP THE GENETIC ALGORITHM and CALCULATING STARTING POOL (STARTING CANDIDATE POPULATION)
    #####
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
    
    NPOPSIZE = (len(data.columns) -2) #RANDOM STARTING POOL SIZE
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
                
        X_train=data[var_model]
        Y_train=data[output_var]
    
        ######
        # CHANGE_HERE - START: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
        #####             
        '''        
        rf = RandomForestClassifier(n_estimators=100, random_state=50)                
        rf1 = rf.fit(X_train, Y_train)
        Y_predict = rf1.predict_proba(X_train)
        Y_predict  = Y_predict[:,1]
        '''
        Fin_model = linear_model.LinearRegression()
        Fin_model.fit(X_train, Y_train)
        Y_predict = Fin_model.predict(X_train)
        ######
        # CHANGE_HERE - END: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
        #####             
    
    
        ######
        # CHANGE_HERE - START: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
        #####                
        fpr, tpr, thresholds = metrics.roc_curve(Y_train, Y_predict)
        auc = metrics.auc(fpr, tpr)
        gini_power = abs(2*auc-1)
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
                X_train=data[var_model]
                Y_train=data[output_var]
                
                ######
                # CHANGE_HERE - START: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
                #####         
                Fin_model = linear_model.LinearRegression()
                Fin_model.fit(X_train, Y_train)
                Y_predict = Fin_model.predict(X_train)
                '''                
                rf = RandomForestClassifier(n_estimators=100, random_state=50)                
                rf1 = rf.fit(X_train, Y_train)
                Y_predict = rf1.predict_proba(X_train)
                Y_predict  = Y_predict[:,1]
                '''
                ######
                # CHANGE_HERE - END: YOU ARE VERY LIKELY USING A DIFFERENT TECHNIQUE BY NOW. SO CHANGE TO YOURS.
                #####            
                           
                
                ######
                # CHANGE_HERE - START: HERE IT USES THE DEVELOPMENT GINI TO SELECT VARIABLES, YOU SHOULD A DIFFERENT GINI. EITHER THE OOT GINI OR THE SQRT(DEV_GINI*OOT_GINI)
                #####                       
                fpr, tpr, thresholds = metrics.roc_curve(Y_train, Y_predict)
                auc = metrics.auc(fpr, tpr)
                gini_power = abs(2*auc-1)
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
        #print ('sum_current_gini=', sum_current_gini, 'sum_current_gini_1=', sum_current_gini_1, 'sum_current_gini_2=', sum_current_gini_2)
        if(sum_current_gini>sum_current_gini_1+0.0001 or sum_current_gini>sum_current_gini_2+0.0001):
            OK=1
    #####
    #GENETIC ALGORITHM MAIN LOOP - END
    #####
    
    
    gini_max=list_gini[0]        
    gini=float(gini_max.split(';')[0])
    features=gini_max.split(';')[1]
    
    ####
    # PRINTING OUT THE LIST OF FEATURES
    #####
    
    use_these = []
    f=0
    for i in range(len(features)):
        if features[i]=='1':
            f+=1
            use_these.append(list(list_inputs)[i])

    X = data[use_these]
    Y = data[output_var]
    Fin_model = linear_model.LinearRegression()
    Fin_model.fit(X, Y)
    Y_predict = Fin_model.predict(X)
    cv_score = Fin_model.score(X, Y)

    '''    
    rf = RandomForestClassifier(n_estimators=100, random_state=50)                
    rf1 = rf.fit(X, Y)
    Y_predict = rf1.predict_proba(X)
    Y_predict  = Y_predict[:,1]
    
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size=0.2, random_state=10)    
    rfcv = Fin_model.fit(X_train, y_train)
    '''
    print("Genetic Algorithm Score", cv_score)
    print("Using", use_these) 
    return(cv_score)

# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 19:21:34 2016

Stepwise in Py
@author: Gaille
"""

def sw(data):
    from sklearn import linear_model,metrics
    import numpy as np
    import pandas as pd
    
    
    def xattrSelect(x, idxset):
        """ Takes X matrix as list of list and returns subset containing columns in idxSet """
        xout = []
        for row in x:
            xout.append([row[i] for i in idxset])
        return xout
    
    
    #Read the data in: choose the first FA dataset OR the second FA dataset

    xLists = []
    labels = []
    names = pd.Series(data.columns) 
    firstline = True
    
    for line in data.values:
        row = list(line)
        # Populate labels list 
        labels.append(row[-1])
        # Remove headers
        row.pop()
        # Ensure everything is a float
        floatrow = [float(s) for s in row]
        xLists.append(floatrow)
    
    #Training and test data sets
    indices = range(len(xLists))
    
    xListtrain = [xLists[i] for i in indices if i % 3 != 0]
    xListtest = [xLists[i] for i in indices if i % 3 == 0]
    labeltest = [labels[i] for i in indices if i % 3 == 0]
    labeltrain = [labels[i] for i in indices if i % 3 != 0]
    
    #Stepwise Regression
    attributeList = []
    index = range(len(xLists[1])) 
    indexSet = set(index)
    indexSeq = []
    oosError = []
    
    for i in index:
        attSet = set(attributeList)
        # attributes not currently included
        attTryset = indexSet - attSet
        # form into list
        attTry = [o for o in attTryset]
        errorList = []
        attTemp = []
        # experiment with each feature 
        # select features with least oos error
        for j in attTry:
            attTemp = [] + attributeList
            attTemp.append(j)
    
            #Form training and testing sub matrixes lists of lists
            xTraintemp = xattrSelect(xListtrain, attTemp)
            xTesttemp = xattrSelect(xListtest, attTemp)
    
            #Convert into arrays because that is all the scikit learnregression can accept
            xTrain = np.array(xTraintemp)
            yTrain = np.array(labeltrain)
            xTest = np.array(xTesttemp)
            yTest = np.array(labeltest)
    
            # use scikitlearn linear regression
            Fin_model = linear_model.LinearRegression()
            Fin_model.fit(xTrain, yTrain)
            a = Fin_model.predict(xTrain)
            
            fpr, tpr, thresholds = metrics.roc_curve(yTrain, a)
            auc = metrics.auc(fpr, tpr)
            gini_power = abs(2*auc-1)
            errorList.append(gini_power)
            
    
            # Use trained model to generate prediction and calculate rmsError
            '''rmsError = np.linalg.norm((yTest - Fin_model.predict(xTest)), 2) / math.sqrt(len(yTest))
            errorList.append(rmsError)
            attTemp = []
            '''
        iBest = np.argmin(errorList)
        attributeList.append(attTry[iBest])
        oosError.append(errorList[iBest])
    
    #If you want the sample error 
    #print("Out of sample error versus attribute set size" )
    #print(oosError)
    
    #If you want the indices of the most useful attributes
    #print("\n" + "Best attribute indices")
    #print(attributeList)
    
    namesList = [names[i] for i in attributeList]
    
    x = data[namesList]
    y = data['ob_target']
    
    Fin_model = linear_model.LinearRegression()
    Fin_model.fit(x, y)
    sw_fin = Fin_model.score(x,y)
    print("Step Wise Score", sw_fin)
    print("Using", namesList)    
    return(sw_fin)


def compare_stepwise_genetic():
    data = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv") 
    ga(data)
    sw(data)
    
compare_stepwise_genetic()

