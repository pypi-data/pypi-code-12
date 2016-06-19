# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 08:53:54 2016

@author: jparker
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import re
import requests
from requests.auth import HTTPBasicAuth
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm, metrics
#from sklearn.svm import SVC
from sklearn.metrics import roc_auc_score
import time
from sklearn import cross_validation, linear_model


def menuMain(errorMessage=""):
        # Print the MAIN MENU
        print("\n"*50)
        print("\n Financial Analytics Final Project Group F")
        print("\n Algorithms Implementation")
        print("\n Main Menu:\n")
        print("1 - A.1   Automated Data Cleaning")
        print("2 - A.4.1 Automated Dummy Creation and Transformation with Automated Supervised Binning")
        print("3 - A.6   Automated method comparison and choosing ")
        print("4 - H.1 Human assisted Data Cleaning ")
        print("5 - H.5 Human assisted method picking ")
        print("6 - Exit")
        print("\n",errorMessage)

def menuFive(errorMessage=""):
        # H.5 Human assisted method picking:
        print("\n"*50)
        print("\n Financial Analytics Final Project Group F")
        print(" Algorithms Implementation (Option 5)")
        print("\n ** H.5 Human assisted method picking:\n")
        print("1 - Best Algorith by GINI")
        print("2 - Best Algorith by Speed Performance")
        print("3 - GML")
        print("4 - Random Forest")
        print("5 - SVM")
        print("\n  R                     - Return Main Menu")
        print("\n",errorMessage)
        
def main():
        #This is the Main Menu that controls the aplication Menu
       menu = ""
       menuMessage = ""
       while menu !="Exit":
        menuMain(menuMessage)
        option = input("\n Select a valid menu option (1 to 6): ")
        menu = MenuOption(option)
        if menu == "1":
            #main1()
            print("1")
            menuMessage = ""
        elif menu == "2":
            #main2()
            print("2")
            menuMessage = ""
        elif menu == "3":
            models()
            menuMessage = ""
        elif menu == "4":
            #main4()
            print("4")
            menuMessage = ""
        elif menu == "5":
            #main5()
            main5()
            menuMessage = ""
        else:
            #Invalid menu option
            #menuMessage=getErrorMsg(menu)
            menuMessage = "** Invalid Menu Option"

def main5():
     # Control the Menu 3 for manage the reports
     menu3=""
     menuMessage=""
     status=0
     while menu3 !="R":
        #Print Report Menu
        menuFive(menuMessage)
        option = input("\n Input Valid Option 1 to 5 (press R for return to Main Menu): ")
        if option.lower() == "r":
            menu3 = "R"
        elif option in ["1","2","3","4","5"]:
            status = model_configuration(option)
            #status = model_selection(option)
            menuMessage=""
        else:
           #invalid Menu Option
           status = 1
           menuMessage="** Invalid Option"
     return(status)

def model_configuration(option):
    print("\n"*50)
    print("\n Configuracion de Parametros:\n")
    devfile = input("\n Input training filename and path (dev.csv): ")
    if devfile =="":
        devfile="dev.csv"
    ootfile = input("\n Input Out of time filename and path (oot0.csv): ")
    if ootfile =="":
        ootfile="oot0.csv"
    #default values
    RF_estimators=1000
    RF_depth=50
    SVM_kernel = "default" 
    SVM_degree = 1

    if option == "4":
        RF_est = input("\n RF # of estimators (1000): ")
        if RF_est == "":
            RF_estimators=1000
        else:
            RF_estimators=int(RF_est)
        RF_dpth = input("\n RF Max depth (50): ")
        if RF_dpth == "":
            RF_depth=50
        else:
            RF_depth = int(RF_dpth)
    
    if option == "5":
        SVM_krnl = input("\n SVM kernel to use [linear, poly] (default): ")
        if SVM_krnl == "":
            SVM_kernel = "default"
        elif SVM_krnl == "poly":
            SVM_kernel = SVM_krnl
            SVM_dgr = input("\n Poly Degree (2): ")
            if SVM_dgr == "":
                SVM_degree = 2
            else:
                SVM_degree = int(SVM_dgr)
        else:
            SVM_kernel = SVM_krnl
            
    # execute Model Selection 
    print("\n option, devfile, ootfile, RF_estimators, RF_depth, SVM_kernel, SVM_degree")
    print(option, devfile, ootfile, RF_estimators, RF_depth, SVM_kernel, SVM_degree)
    correct = input(" \nThe parameters are correct? Y/N (Y): ")
    if correct.upper() == "N":
        model_configuration(option)
    status = model_selection(option, devfile, ootfile, RF_estimators, RF_depth, SVM_kernel, SVM_degree)
    return(0)    
    
      
def MenuOption(value):
        # Validate if you Really want to exit the program
    if value == "6":
        exit = input("\n Are you sure you want to exit? (Y/N): ").lower()
        if exit == 'y':
            print("\n     Hasta la vista Baby!!\n")
            return("Exit")
        else:
            return("0")
    elif value in ("1","2","3","4","5"):
        return(value)
    else:
        # invalid menu option
        return(1)


def models():
    
       ### LOAD DATASET

       #df= pd.read_csv('https://dl.dropboxusercontent.com/u/28535341/IE_MBD_FA_dataset_dev.csv')
       #df= pd.read_csv("IE_MBD_FA_dataset_dev.csv")

       #print "DOWNLOADING DATASETS..."
       #df = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv") #DEV-SAMPLE
       #dfo = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/oot0.csv")#OUT-OF-TIME SAMPLE

       df= pd.read_csv("dev.csv")
       #dfo = pd.read_csv("oot0test.csv")#OUT-OF-TIME SAMPLE
       #df = pd.read_csv("dev2max.csv") #DEV-SAMPLE
       dfo = pd.read_csv("oot0.csv")#OUT-OF-TIME SAMPLE

       


       #df = pd.read_csv("dev2max.csv") #DEV-SAMPLE
       #dfo = pd.read_csv("oot02max.csv")#OUT-OF-TIME SAMPLE

       print ("IDENTIFYING TYPES...")

       in_model = []
       list_ib = set()  #input binary
       list_icn = set() #input categorical nominal
       list_ico = set() #input categorical ordinal
       list_if = set()  #input numerical continuos (input float)
       list_inputs = set()
       list_features = set()
       output_var = 'ob_target'
       algorithm = []  #algorithm name
       giniAlg = []    #algorithm gini
       timeAlg = []       #algorithm time

       '''
       df.info()
       df.dtypes
       df.describe()
       df.head()
       df.tail(5)
       dfo.fillna(0)
       '''
       for var_name in df.columns:
               if re.search('^i',var_name):
                   list_inputs.add(var_name)
                   list_features.add(var_name)
                   print (var_name,"is input")
               if re.search('^ib_',var_name):
                   list_ib.add(var_name)
                   #print (var_name,"is input binary")
               elif re.search('^icn_',var_name):
                   list_icn.add(var_name)
                   #print (var_name,"is input categorical nominal")
               elif re.search('^ico_',var_name):
                   list_ico.add(var_name)
                   #print (var_name,"is input categorical ordinal")
               elif re.search('^if_',var_name):
                   list_if.add(var_name)
                   #print (var_name,"is input numerical continuos (input float)")
               elif re.search('^ob_',var_name):
                   output_var = var_name
               else:
                   print ("ERROR: unable to identify the type of:", var_name)
    
       '''
       # CAPTURING ALL INPUT VARIABLES AND THE OUTPUT VARIABLE
       list_inputs= set()
       for var_name in df.columns:
         if re.search('^i',var_name):
           list_inputs.add(var_name)
           print (var_name,"isinput binary")
         elif re.search('^o',var_name):
           output_var= var_name
           print (var_name,"isoutput (target) binary")
       # CAPTURING ALL INPUT VARIABLES AND THE OUTPUT VARIABLE
       '''



       # FITTING A MODEL WITH ALL INPUT VARIABLE ON THE DEVELOPMENT DATASET
       ### GML
       algorithm.append('GML')
       in_model = list_inputs
       start_time = time.time()  #start time to calculate speed
       logit= sm.GLM(df[output_var],df[list(set(list_inputs))], family = sm.families.Binomial())
       resultGML = logit.fit()
       elapsed_timeGML = time.time() - start_time   # end time for Algorithm
       pred_score= resultGML.predict(df[list(set(list_inputs))])
       timeAlg.append(elapsed_timeGML)
       pred_score10 = pred_score.round()
       #print (result.summary())
       gini_score_GML= 2*roc_auc_score(df[output_var], pred_score)-1
       giniAlg.append(gini_score_GML)
       print ("\nGLM Elapsed time= ",elapsed_timeGML) 
       print ("GINI DEVELOPMENT GLM=", gini_score_GML)
       print("Confusion matrix GML:\n%s" % metrics.confusion_matrix(df[output_var], pred_score10))

       
       '''### Linear Model
       #algorithm.append('RF')
       Xlm = df[list(in_model)]
       ylm = df[output_var]
       start_time = time.time() #start time to calculate speed
       modelLR  = linear_model.LinearRegression()
       resultLR = modelLR.fit(Xlm,ylm)
       elapsed_timeLR = time.time() - start_time  # end time for Algorithm
       pred_LR = resultLR.predict(Xlm)
       pred_LR10 = pred_LR.round()
       #timeAlg.append(elapsed_timeLR)
       gini_score_LR = 2*roc_auc_score(df[output_var], pred_LR)-1
       #giniAlg.append(gini_score_LR)
       print ("\nLineat Regression Elapsed time= ",elapsed_timeLR) 
       print ("GINI DEVELOPMENT LR=", gini_score_LR)
       print("Confusion matrix LR:\n%s" % metrics.confusion_matrix(df[output_var], pred_LR10))'''

       ### Random Forest
       algorithm.append('RF')
       list_features.discard('id')
       in_modelF = list_features
       
       X = df[list(in_modelF)]
       y = df[output_var]
       start_time = time.time() #start time to calculate speed
       #modelRF= RandomForestClassifier(n_estimators=1000, max_depth=60, class_weight = {0:0.1, 1:0.9} )
       modelRF= RandomForestClassifier(n_estimators=1000, max_depth=60 )
       resultRF = modelRF.fit(X, y)
       elapsed_timeRF = time.time() - start_time  # end time for Algorithm
       pred_RF = resultRF.predict(X)
       pred_RFprob = resultRF.predict_proba(X)
       timeAlg.append(elapsed_timeRF)

       gini_score_RF = 2*roc_auc_score(df[output_var], pred_RF)-1
       giniAlg.append(gini_score_RF)
       print ("\nRandom Forest Elapsed time= ",elapsed_timeRF) 
       print ("GINI DEVELOPMENT RF=", gini_score_RF)
       print("Confusion matrix RF:\n%s" % metrics.confusion_matrix(df[output_var], pred_RF))


       ### SVM
       algorithm.append('SVM')       
       #in_model = list_ib
       in_model = list_inputs
       list_features.discard('id')
       in_modelF = list_features
       #X = df[list(in_model)]
       X = df[list(in_modelF)]   # exclude 'id'
       y = df[output_var]
       start_time = time.time() #start time to calculate speed
       modelSVM = svm.SVC(probability=True, class_weight="auto")
       #kernel='poly', degree=3, C=1.0  #kernel='rbf', gamma=0.7, C=1.0
       #modelSVM = svm.SVC(kernel='poly', degree=3, C=1.0,probability=True, class_weight="balanced")
       #modelSVM = svm.SVC(kernel='linear')
       #modelSVM = svm.SVC(probability=True, class_weight="auto")
       #modelSVM = svm.SVC(probability=True)
       resultSVM = modelSVM.fit(X, y) 
       elapsed_timeSVM = time.time() - start_time  # end time for Algorithm
       pred_SVM = resultSVM.predict(X)
       timeAlg.append(elapsed_timeSVM)
       gini_score_SVM = 2*roc_auc_score(df[output_var], pred_SVM)-1
       giniAlg.append(gini_score_SVM)

       print ("\nSVM Elapsed time= ",elapsed_timeSVM)
       print ("GINI DEVELOPMENT SVM=", gini_score_SVM)
       print("Confusion matrix SVM:\n%s" % metrics.confusion_matrix(df[output_var], pred_SVM))

       print("\n****************************")
       print("\n    Model Comparison\n")

       #CROSS VALIDATION

       #scoresLR = cross_validation.cross_val_score(modelLR, Xlm, ylm, cv = 10)
       #print("Acccuracy RF: %0.4f (+/- %.3f), or not... " % (scoresLR.mean(), scoresLR.std() * 2))

       scoresRF = cross_validation.cross_val_score(modelRF, X, y, cv = 10)
       print("Acccuracy RF: %0.4f (+/- %.3f), or not... " % (scoresRF.mean(), scoresRF.std() * 2))

       scoresSVM = cross_validation.cross_val_score(modelSVM, X, y, cv = 10)
       print("Acccuracy SVM: %0.4f (+/- %.3f), or not... " % (scoresSVM.mean(), scoresSVM.std() * 2))
       

       ## Algorithms Results Comparison
       resultAlg = pd.DataFrame()
       resultAlg['Algorithm']=algorithm
       resultAlg['Gini_Score']=giniAlg
       resultAlg['Speed']=timeAlg
       BestAlg = resultAlg.sort_values(by=['Gini_Score','Speed'], ascending=[False,True])
       print(BestAlg)
       BA = list(BestAlg.Algorithm)
       print("\n Best Algorithm: ", BA[0] )       # This is the best algorithm
       
       print("\n****************************")
       input(" \nPress enter to continue...")
       #return "0"       IF 


def model_selection(option, devfile, ootfile, RF_estimators, RF_depth, SVM_kernel, SVM_degree):
       '''       
       ### Parameter documentation ###
       option values:
        1 - Best Algorith by GINI
        2 - Best Algorith by Speed Performance
        3 - GML
        4 - Random Forest
        5 - SVM
       devfile:
        file name path for the training dataset
       ootfile:
        file name and path for the out of time dataset
       RF_estimators:
        Number of estimators for the RF algorithm (50,1000,...)
       RF_depth=60
        Number of depth trees for the RF algorithm (10,60,...)
       SVM_kernel:
        Type of kernel to use with SVM (default, linear, poly)
       SVM_degree:
        Degree to use with SVM (2,3)
       
       '''
       df= pd.read_csv(devfile)

       in_model = []
       list_ib = set()  #input binary
       list_icn = set() #input categorical nominal
       list_ico = set() #input categorical ordinal
       list_if = set()  #input numerical continuos (input float)
       list_inputs = set()
       list_features = set()
       output_var = 'ob_target'
       algorithm = []  #algorithm name
       giniAlg = []    #algorithm gini
       timeAlg = []       #algorithm time
       #print(df.head())
       for var_name in df.columns:
               if re.search('^i',var_name):
                   list_inputs.add(var_name)
                   list_features.add(var_name)
                   #print (var_name,"is input")
               if re.search('^ib_',var_name):
                   list_ib.add(var_name)
                   #print (var_name,"is input binary")
               elif re.search('^icn_',var_name):
                   list_icn.add(var_name)
                   #print (var_name,"is input categorical nominal")
               elif re.search('^ico_',var_name):
                   list_ico.add(var_name)
                   #print (var_name,"is input categorical ordinal")
               elif re.search('^if_',var_name):
                   list_if.add(var_name)
                   #print (var_name,"is input numerical continuos (input float)")
               elif re.search('^ob_',var_name):
                   output_var = var_name
               #else:
                   #print ("ERROR: unable to identify the type of:", var_name)
       
       if option=="3" or option in ["1","2"]: 
           ## GML
           print("\nGML")
           algorithm.append('GML')
           in_model = list_inputs
           start_time = time.time()  #start time to calculate speed
           logit= sm.GLM(df[output_var],df[list(set(list_inputs))], family = sm.families.Binomial())
           resultGML = logit.fit()
           elapsed_timeGML = time.time() - start_time   # end time for Algorithm
           pred_score= resultGML.predict(df[list(set(list_inputs))])
           timeAlg.append(elapsed_timeGML)
           pred_score10 = pred_score.round()
           #print (result.summary())
           gini_score_GML= 2*roc_auc_score(df[output_var], pred_score)-1
           giniAlg.append(gini_score_GML)
           print ("\nGLM Elapsed time= ",elapsed_timeGML) 
           print ("GINI DEVELOPMENT GLM=", gini_score_GML)
           print("Confusion matrix GML:\n%s" % metrics.confusion_matrix(df[output_var], pred_score10))
        
       if option=="4" or option in ["1","2"]:
           ## Random Forest
           print("\nRF")
           algorithm.append('RF')
           list_features.discard('id')
           in_modelF = list_features
       
           X = df[list(in_modelF)]
           y = df[output_var]
           start_time = time.time() #start time to calculate speed
           #modelRF= RandomForestClassifier(n_estimators=1000, max_depth=60, class_weight = {0:0.1, 1:0.9} )
           modelRF= RandomForestClassifier(n_estimators=RF_estimators, max_depth=RF_depth )
           resultRF = modelRF.fit(X, y)
           elapsed_timeRF = time.time() - start_time  # end time for Algorithm
           pred_RF = resultRF.predict(X)
           pred_RFprob = resultRF.predict_proba(X)
           timeAlg.append(elapsed_timeRF)

           gini_score_RF = 2*roc_auc_score(df[output_var], pred_RF)-1
           giniAlg.append(gini_score_RF)
           print ("\nRandom Forest Elapsed time= ",elapsed_timeRF) 
           print ("GINI DEVELOPMENT RF=", gini_score_RF)
           print("Confusion matrix RF:\n%s" % metrics.confusion_matrix(df[output_var], pred_RF))           

       if option=="5" or option in ["1","2"]:
           ## SVM
           print("\nSVM")
           algorithm.append('SVM')       
           #in_model = list_ib
           in_model = list_inputs
           list_features.discard('id')
           in_modelF = list_features
           #X = df[list(in_model)]
           X = df[list(in_modelF)]   # exclude 'id'
           y = df[output_var]
           start_time = time.time() #start time to calculate speed
           modelSVM = svm.SVC(probability=True, class_weight="auto")
           #kernel='poly', degree=3, C=1.0  #kernel='rbf', gamma=0.7, C=1.0
           #modelSVM = svm.SVC(kernel='poly', degree=3, C=1.0,probability=True, class_weight="balanced")
           #modelSVM = svm.SVC(kernel='linear')
           #modelSVM = svm.SVC(probability=True, class_weight="auto")
           #modelSVM = svm.SVC(probability=True)
           resultSVM = modelSVM.fit(X, y) 
           elapsed_timeSVM = time.time() - start_time  # end time for Algorithm
           pred_SVM = resultSVM.predict(X)
           timeAlg.append(elapsed_timeSVM)
           gini_score_SVM = 2*roc_auc_score(df[output_var], pred_SVM)-1
           giniAlg.append(gini_score_SVM)

           print ("\nSVM Elapsed time= ",elapsed_timeSVM)
           print ("GINI DEVELOPMENT SVM=", gini_score_SVM)
           print("Confusion matrix SVM:\n%s" % metrics.confusion_matrix(df[output_var], pred_SVM))

           
       ## Algorithms Results Comparison
       print("\n****************************")
       print("\n    Model Summary \n")           
       resultAlg = pd.DataFrame()
       resultAlg['Algorithm']=algorithm
       resultAlg['Gini_Score']=giniAlg
       resultAlg['Speed']=timeAlg
       if option=="2":
           # Order by Speed
           BestAlg = resultAlg.sort_values(by=['Speed','Gini_Score'], ascending=[True,False])
           print(BestAlg[['Algorithm','Speed','Gini_Score']])
       else:
           #order by Gini
           BestAlg = resultAlg.sort_values(by=['Gini_Score','Speed'], ascending=[False,True])
           print(BestAlg)
       BA = list(BestAlg.Algorithm)
       if option=="1":
           print("\n Best Algorithm by Gini Score: ", BA[0] )
       elif option=="2":
           print("\n Best Algorithm by Speed: ", BA[0] )
       else:
           print("\n Algorithm Selected: ", BA[0] )       # This is the best algorithm

           
       input(" \nPress enter to continue...")
       return "0"


### Inicia Programa
if __name__ == "__main__":
    main()
