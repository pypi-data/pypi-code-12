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
import operator
import warnings
from scipy.stats import entropy


warnings.filterwarnings('ignore')


def menuMain(errorMessage=""):
        # Print the MAIN MENU
        print("\n"*50)
        print("\n Financial Analytics Final Project Group F")
        print("\n Algorithms Implementation")
        print("\n Main Menu:\n")
        print("1 - A1  Automated Data Cleaning")
        print("2 - A41 Automated Dummy Creation and Transformation with Automated Supervised Binning")
        print("3 - A6  Automated method comparison and choosing ")
        print("4 - H1   Human assisted Data Cleaning ")
        print("5 - H5   Human assisted method picking ")
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
            automated_data_cleaning(option)
            menuMessage = ""
        elif menu == "2":
            #main2()
            automated_dummy_creation(option)
            menuMessage = ""
        elif menu == "3":
            print("\n\n Configuracion de Parametros (Option %s):\n" % option)
            devfile = input("\n Input training filename and path (dev.csv): ")
            if devfile =="":
                devfile="dev.csv"
            ootfile = input("\n Input Out of time filename and path (oot0.csv): ")
            if ootfile =="":
                ootfile="oot0.csv"
            models(devfile,ootfile)
            menuMessage = ""
        elif menu == "4":
            #main4()
            human_assit_data_clean(option)
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
    '''
    Parameter configuration to execute the funtion :
    ** H5   Human assisted method picking
    model_selection(option, devfile, ootfile, RF_estimators, RF_depth, SVM_kernel, SVM_degree)
   
    '''
    print("\n"*50)
    print("\n Configuracion de Parametros (Option %s):\n" % option)
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

    if option == "4" or option in ["1","2"]:
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
    
    if option == "5" or option in ["1","2"]:
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


def models(devfile,ootfile):
       """
       A6  Automated method comparison and choosing
       This funtion select the best method base on Gini Score and the by the speed performance
       Uses the files dev.csv and oot0csv
       """
       ### LOAD DATASET

       #df= pd.read_csv('https://dl.dropboxusercontent.com/u/28535341/IE_MBD_FA_dataset_dev.csv')
       #df= pd.read_csv("IE_MBD_FA_dataset_dev.csv")

       #print "DOWNLOADING DATASETS..."
       #df = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/dev.csv") #DEV-SAMPLE
       #dfo = pd.read_csv("https://dl.dropboxusercontent.com/u/28535341/oot0.csv")#OUT-OF-TIME SAMPLE

       #df= pd.read_csv("dev.csv")
       #dfo = pd.read_csv("oot0.csv")#OUT-OF-TIME SAMPLE

       df= pd.read_csv(devfile)
       dfo = pd.read_csv(ootfile)#OUT-OF-TIME SAMPLE


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
       print("\n    Cross Validation\n")

       #CROSS VALIDATION

       #scoresLR = cross_validation.cross_val_score(modelLR, Xlm, ylm, cv = 10)
       #print("Acccuracy RF: %0.4f (+/- %.3f), or not... " % (scoresLR.mean(), scoresLR.std() * 2))

       scoresRF = cross_validation.cross_val_score(modelRF, X, y, cv = 10)
       scoresSVM = cross_validation.cross_val_score(modelSVM, X, y, cv = 10)

       print("\nAcccuracy RF: %0.4f (+/- %.3f), or not... " % (scoresRF.mean(), scoresRF.std() * 2))
       print("Acccuracy SVM: %0.4f (+/- %.3f), or not... " % (scoresSVM.mean(), scoresSVM.std() * 2))
       

       ## Algorithms Results Comparison
       print("\n****************************")
       print("\n    Model Summary \n")           
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

      ####### Predict Model
       dfo=dfo.fillna(0) ### Change all NA for 0
       if BA[0]=="GML":
           ## Predict GML
           Xo = dfo[list(set(in_model))]
           pred_score= resultGML.predict(Xo)
           dfo['pred'] = pred_score   ## GML
           dfo_tosend = dfo[list(['id','pred'])]
           dfo_tosend = dfo_tosend.sort_values('id')
           #print(dfo.head())
           #print(dfo_tosend.head())
           print("Prediction Generated with GML")
           dfo.to_csv("oot_predGML.csv")
           dfo_tosend.to_csv("oot_id_pred_GML.csv")
       elif BA[0]=="RF":
           ## Predict RF       
           XoRF = dfo[list(set(in_modelF))]
           #y_pred = resultRF.predict(X)
           yo_predRF = resultRF.predict(XoRF)
           yo_predPRF = resultRF.predict_proba(XoRF)
           yo_pred10RF = yo_predPRF.round()
           dfo['pred'] = yo_predPRF[0:,0]
           dfo_tosend = dfo[list(['id','pred'])]
           dfo_tosend = dfo_tosend.sort_values('id')
           #print(dfo.head())
           #print(dfo_tosend.head())
           print("Prediction Generated with RF")
           dfo.to_csv("oot_pred_RF.csv")
           dfo_tosend.to_csv("oot_id_pred_RF.csv")
       elif BA[0]=="SVM":
           ## Predict SVM       
           XoSVM = dfo[list(set(in_modelF))]
           #y_pred = resultRF.predict(X)
           yo_predSVM = resultSVM.predict(XoSVM)
           yo_predPSVM = resultSVM.predict_proba(XoSVM)
           yo_pred10SVM = yo_predPSVM.round()
           dfo['pred'] = yo_predPSVM[0:,0]
           dfo_tosend = dfo[list(['id','pred'])]
           dfo_tosend = dfo_tosend.sort_values('id')
           #print(dfo.head())
           #print(dfo_tosend.head())
           print("Prediction Generated with SVM")
           dfo.to_csv("oot_pred_SVM.csv")
           dfo_tosend.to_csv("oot_id_pred_SVM.csv")
       
       print("\n****************************")
       input(" \nPress enter to continue...")
       return "0"

def model_selection(option, devfile, ootfile, RF_estimators, RF_depth, SVM_kernel, SVM_degree):
       '''
       H5   Human assisted method picking
       ### Parameter documentation ###
       option values:
        1 - Best Algorith by GINI\n
        2 - Best Algorith by Speed Performance\n
        3 - GML\n
        4 - Random Forest\n
        5 - SVM\n
       devfile:
        file name path for the training dataset
       ootfile:
        file name and path for the out of time dataset
       RF_estimators:
        Number of estimators for the RF algorithm (50,1000,...)
       RF_depth:
        Number of depth trees for the RF algorithm (10,60,...)
       SVM_kernel:
        Type of kernel to use with SVM (default, linear, poly)
       SVM_degree:
        Degree to use with SVM (2,3)
       
       '''
       df= pd.read_csv(devfile)
       dfo = pd.read_csv(ootfile)
       

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

       ####### Predict Model
       dfo=dfo.fillna(0) ### Change all NA for 0
       if BA[0]=="GML":
           ## Predict GML
           Xo = dfo[list(set(in_model))]
           pred_score= resultGML.predict(Xo)
           dfo['pred'] = pred_score   ## GML
           dfo_tosend = dfo[list(['id','pred'])]
           dfo_tosend = dfo_tosend.sort_values('id')
           #print(dfo.head())
           #print(dfo_tosend.head())
           print("Prediction Generated with GML")
           dfo.to_csv("oot_predGML.csv")
           dfo_tosend.to_csv("oot_id_pred_GML.csv")
       elif BA[0]=="RF":
           ## Predict RF       
           XoRF = dfo[list(set(in_modelF))]
           #y_pred = resultRF.predict(X)
           yo_predRF = resultRF.predict(XoRF)
           yo_predPRF = resultRF.predict_proba(XoRF)
           yo_pred10RF = yo_predPRF.round()
           dfo['pred'] = yo_predPRF[0:,0]
           dfo_tosend = dfo[list(['id','pred'])]
           dfo_tosend = dfo_tosend.sort_values('id')
           #print(dfo.head())
           #print(dfo_tosend.head())
           print("Prediction Generated with RF")
           dfo.to_csv("oot_pred_RF.csv")
           dfo_tosend.to_csv("oot_id_pred_RF.csv")
       elif BA[0]=="SVM":
           ## Predict SVM       
           XoSVM = dfo[list(set(in_modelF))]
           #y_pred = resultRF.predict(X)
           yo_predSVM = resultSVM.predict(XoSVM)
           yo_predPSVM = resultSVM.predict_proba(XoSVM)
           yo_pred10SVM = yo_predPSVM.round()
           dfo['pred'] = yo_predPSVM[0:,0]
           dfo_tosend = dfo[list(['id','pred'])]
           dfo_tosend = dfo_tosend.sort_values('id')
           #print(dfo.head())
           #print(dfo_tosend.head())
           print("Prediction Generated with SVM")
           dfo.to_csv("oot_pred_SVM.csv")
           dfo_tosend.to_csv("oot_id_pred_SVM.csv")
       print("\n****************************")
       input(" \nPress enter to continue...")
       return "0"

def automated_data_cleaning(option):
    """
    A1  Automated Data Cleaning
    This algorithm automatically choose for the user the different actions 
    when dealing with NULL's, NaN's and Outliers.
    \nNULL values it changes for the high frequency values
    NaN values it changes by 0
    Finally for Outliers it changes with the corresponding upper or lower threshold
    It uses a file called "dev-sample.csv" which has dummy values to validate the algorithm
    """
    print("\n"*50)
    print("\n A1 Automated Data Cleaning (Option %s):\n" % option)
    devfile = input("\n Input training filename and path (dev-sample.csv): ")
    if devfile =="":
        devfile="dev-sample.csv"
    df_full= pd.read_csv(devfile)
    columns = ['ib_var_2','icn_var_22','ico_var_25','if_var_68','if_var_78','ob_target']
    df=df_full[list(columns)]
    print("\nINPUT Data Set")
    #df = pd.read_csv("dev-sample.csv")
    print(df.head(10))
    print("\nNumber of records:", len(df.index))
    print("number of variables:", len(df.columns))
    colnames = list(df.columns[0:len(df.columns)])
    print("columns name:", colnames)
    #print("data type:", dict(df.dtypes))
    for k,v in dict(df.dtypes).items():
        if v == 'O':
            #print(k)
            freq = dict(df.groupby(k)[k].count())
            sorted_freq = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
            #print(sorted_freq[0][0])
            for i in range(0,len(df.index)):
                if pd.isnull(df[k][i]):
                    df[k][i] = sorted_freq[0][0] #Replaced by highest frequency value
    
    for k,v in dict(df.dtypes).items():
        if v != 'object':
            for i in range(0,len(df.index)):
                if np.isnan(df[k][i]):
                    df[k][i] = 0
    
    for k,v in dict(df.dtypes).items():
        if v != 'object':
            #print(k)
            #print("mean:" ,np.average(df[k]))
            #print("stdev:" ,np.std(df[k]))
            total_pos = 0
            total_neg = 0
            for i in range(0,len(df.index)):
                if (df[k][i] >= 0):
                    total_pos += 1
                if (df[k][i] < 0):
                    total_neg += 1
            #print("total positive values:", total_pos)
            #print("total negative values:", total_neg)
            negSignMistake = total_neg / len(df.index)
            #print("percentage of negative values:", negSignMistake)
            for i in range(0,len(df.index)):
                if (negSignMistake < 0.05):
                    if (df[k][i] < 0):
                        df[k][i] = df[k][i] * -1
            upThreshold = np.nanmean(df[k]) + 3 * np.std(df[k])
            botThreshold = np.nanmean(df[k]) - 3 * np.std(df[k])
            outliers = 0
            for i in range(0,len(df.index)):
                if (df[k][i] < botThreshold) or (df[k][i] > upThreshold):
                    #print('outliers:', df[k][i])
                    outliers =+ 1
                    #print('outliers value:' ,df[k][i]) 
                    if (df[k][i] > upThreshold):
                        df[k][i] = upThreshold
                    if (df[k][i] < botThreshold):
                        df[k][i] = botThreshold
                    #print('new value:', df[k][i])
            #print("total outliers:", outliers)
            #print(df[k][0])
            
    print("\nOUTPUT Cleaned")
    print(df.head(10))
    input(" \nPress enter to continue...")
    return "0"
    
def human_assit_data_clean(option):
    """
    H1   Human assisted Data Cleaning
    This algorithm gives the user the option to choose different actions 
    when dealing with NULL's, NaN's and Outliers. These are the oprtions:
    \nHow do you want to treat the Null values?
     1.Replaced by highest frequency value
     2.Replaced by lowest frequency value
    \nHow do you want to treat the NaN values
     1.Replaced by zero (0)")
     2.Replaced by mean")
    \nHow do you want to treat the outliers
     1.Replaced by threshold
     2.Replaced by mean
     3.Replaced by median
    It uses a file called "dev-sample.csv" which has dummy values to validate the algorithm
    """
    pd.options.mode.chained_assignment = None  # default='warn'
    print("\n"*50)
    print("\n H1 Human Assited Data Cleaning (Option %s):\n" % option)
    devfile = input("\n Input training filename and path (dev-sample.csv): ")
    if devfile =="":
        devfile="dev-sample.csv"
    df_full= pd.read_csv(devfile)
    columns = ['ib_var_2','icn_var_22','ico_var_25','if_var_68','if_var_78','ob_target']
    df=df_full[list(columns)]
    
    #nullMethod = input("how do you want to treat null values? replaced by highest frequency or lowest?")
    #nanMethod = input("how do you want to treat nan values? replaced by 0 or mean?")
    #outlierMethod = input("how do you want to treat outliers? replaced by mean, median or threshold?")
    print("###########################################\n")
    print("\nHow do you want to treat the Null values?")
    print("1.Replaced by highest frequency value")
    print("2.Replaced by lowest frequency value")
    nullMethod = input("Choose your option (1 or 2):")
    
    print("###########################################\n")
    print("\nHow do you want to treat the NaN values?")
    print("1.Replaced by zero (0)")
    print("2.Replaced by mean")
    nanMethod = input("Choose your option (1 or 2):")
    
    print("###########################################\n")
    print("\nHow do you want to treat the outliers?")
    print("1.Replaced by threshold")
    print("2.Replaced by mean")
    print("3.Replaced by median")
    outlierMethod = input("Choose your option (1, 2, or 3):")
    
    #df = pd.read_csv("dev-sample.csv")
    print("\nINPUT Data Set")
    print(df.head(10))
    records = len(df.index)
    print("\nNumber of records:", records)
    colnames = list(df.columns[0:len(df.columns)])
    print("number of variables:", len(df.columns))
    print("\nColumns name:", colnames)
    #print("data type:", dict(df.dtypes))
    
    for k,v in dict(df.dtypes).items():
        if v == 'O':
            #print("Null Values Treatment for this column (%s): (replaced by highest frequency or lowest?)" % k)
            freq = dict(df.groupby(k)[k].count())
            sorted_freq_t = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
            sorted_freq_f = sorted(freq.items(), key=operator.itemgetter(1), reverse=False)
            #print(sorted_freq[0][0])
            for i in range(0,records):#-835):
                if pd.isnull(df[k][i]):
                    #nullMethod = input("Null Values Treatment for this column (%s): (replaced by highest frequency or lowest?)" %k)
                    if nullMethod == "2":
                        df[k][i] = sorted_freq_f[0][0]
                    else:
                        df[k][i] = sorted_freq_t[0][0] #Replaced by highest frequency value
    
    for k,v in dict(df.dtypes).items():
        if v != 'object':
            for i in range(0,records):#-839):
                if np.isnan(df[k][i]):
                    #nanMethod = input("NaN Values Treatment for this column (%s): (replaced by 0 or mean?)" %k)
                    if nanMethod == "2":
                        df[k][i] = np.nanmean(df[k])                    
                        #df[k].fillna(np.average(df[k]), inplace = True)
                    else:
                        df[k][i] = 0                    
                        #df.fillna(0, inplace = True)
                        
    for k,v in dict(df.dtypes).items():
        if v != 'object':
            #print(k)
            #print("mean:" ,np.nanmean(df[k]))
            #print("stdev:" ,np.std(df[k]))
            total_pos = 0
            total_neg = 0
            for i in range(0,records):#-820):
                if (df[k][i] >= 0):
                    total_pos += 1
                if (df[k][i] < 0):
                    total_neg += 1
            #print("total positive values:", total_pos)
            #print("total negative values:", total_neg)
            negSignMistake = total_neg / total_pos
            #print("percentage of negative values:", negSignMistake)
            for i in range(0,records):#-820):
                if (negSignMistake < 0.05):
                    if (df[k][i] < 0):
                        df[k][i] = df[k][i] * -1
            upThreshold = np.nanmean(df[k]) + 3 * np.std(df[k])
            botThreshold = np.nanmean(df[k]) - 3 * np.std(df[k])    
            outliers = 0
            for i in range(0,records):#-820):
                if (df[k][i] < botThreshold) or (df[k][i] > upThreshold):
                    #outlierMethod = input("Outlier Values Treatment for this column (%s): (replaced by mean or median?)" %k)               
                    #print('outliers:', df[k][i])
                    outliers += 1
                    #print('outliers value:' ,df[k][i]) 
                    #df[k][i] = np.average(df[k])
                    if outlierMethod == "2":
                        df[k][i] = np.nanmean(df[k])
                    if outlierMethod == "3":
                        df[k][i] = np.median(df[k])
                    else:
                        if (df[k][i] > upThreshold):
                            df[k][i] = upThreshold
                        if (df[k][i] < botThreshold):
                            df[k][i] = botThreshold
                        
                    #print('new value:', df[k][i])
            #print("total outliers:", outliers)
    print("\n Data Set Cleaned\n")
    print(df.head(10))
    input(" \nPress enter to continue...")
    return "0"

def DummyTransform(InputDataFrame,ColumnsToTransform=None):
    """
    A41 Automated Dummy Creation and Transformation with Automated Supervised Binning
    This function is used to transform categorial or nominal variables in a data frame to dummy variables\n
    for example: Animal column will have 3 values (dog, cat, rat), then this function will return data frame
    with additional 3 columns Animal_dog, Animal_cat, Animal_rat but without the original Animal column\n
    
    Parameters
    ----------
    param InputDataFrame: Dataframe
        Input Data Frame\n
    
    ColumnsToTransform: optional list of strings
        list of the columns to tranform, if None then function will assume that each categorial column is preceded with 'ico_' and each nominal varible is preceded with 'icn_'
    """
    if ColumnsToTransform==None:
        List_Categorial_n_Nominal=list()
        for var_name in InputDataFrame.columns:
            if re.search('^icn_',var_name):
                List_Categorial_n_Nominal.append(var_name)
            elif re.search('^ico_',var_name):
                List_Categorial_n_Nominal.append(var_name)
        ColumnsToTransform=List_Categorial_n_Nominal
    return pd.get_dummies(InputDataFrame,columns=ColumnsToTransform)

    #==============================================================================
    # ## Example how to use
    # df = pd.read_csv("D:/IE Masters/Third Semester/Financial Analytics/dev.csv")
    #
    # ## you can specify some columns only
    # new_df=DummyTransform(df,['ico_var_61', 'ico_var_62', 'ico_var_63'])
    #
    #
    # ## you can transform all the categgorial and nominal variables at once, if categorial is 
    # ## is preceded with 'ico_' and each nominal varible is preceded with 'icn_'
    # all_df=DummyTransform(df)
    #
    #==============================================================================

def GetEntropy(data,ColumnName,AssociatedColumnName,Separator_value):
    lower_band_count=len(data[(data[ColumnName]<=Separator_value)])
    Fraud_lower_band_count=len(data[(data[ColumnName]<=Separator_value) & (data[AssociatedColumnName]==1)])
    NonFraud_lower_band_count=len(data[(data[ColumnName]<=Separator_value) & (data[AssociatedColumnName]==0)])
    upper_band_count=len(data[(data[ColumnName]>Separator_value)])
    Fraud_upper_band_count=len(data[(data[ColumnName]>Separator_value) & (data[AssociatedColumnName]==1)])
    NonFraud_upper_band_count=len(data[(data[ColumnName]>Separator_value) & (data[AssociatedColumnName]==0)])
    if lower_band_count>0:
        entropy_low_band=entropy([NonFraud_lower_band_count/lower_band_count,Fraud_lower_band_count/lower_band_count],None,2)
    else:
        entropy_low_band=0
    if upper_band_count>0:
        entropy_upper_band=entropy([NonFraud_upper_band_count/upper_band_count,Fraud_upper_band_count/upper_band_count],None,2)
    else:
        entropy_upper_band=0
    inf_entropy=entropy_low_band+entropy_upper_band
    return inf_entropy

def MinEntropySplit(CutPoints):
    min_val=10
    for k,v in CutPoints.items():
        min_val=min(min_val,k)
    return CutPoints[min_val]
    

def selectBin(data,ColumnName,AssociatedColumnName):
    tempdf=data[[ColumnName,AssociatedColumnName]]
    Bin_Number=min(10,int(round(np.sqrt( int(round(max(tempdf[ColumnName]),0))),0)))
    BinPoints=Binning(tempdf,ColumnName,AssociatedColumnName,Bin_Number)
    #print("Last Number of bins now ",len(BinPoints)," Bin Points",BinPoints )
    newbin = []
    length = len(BinPoints)
    value = np.array(tempdf[ColumnName])
    for i in range(0, len(tempdf)):
        if value[i] <= BinPoints[0]:
            newbin.append("<= "+str(BinPoints[0]))
        for j in range(length-1):
            if value[i] > BinPoints[j] and value[i] <= BinPoints[j+1]:
                newbin.append(str(BinPoints[j])+" - "+str(BinPoints[j+1]))
        if value[i] > BinPoints[length-1]:
            newbin.append("> "+str(BinPoints[length-1]))
    data[ColumnName+'_bin']= pd.Series(newbin,data.index)
    return data
    
def GetBin(min_value,max_value,tempdf,ColumnName,AssociatedColumnName):
    CutPoints={}
    Middle_Point=(max_value+min_value)/2
    First_Quarter=(Middle_Point-min_value)/2
    Third_Quarter=First_Quarter+Middle_Point
    separators=[First_Quarter,Middle_Point,Third_Quarter]
    tempdf=tempdf[(tempdf[ColumnName]<=max_value) & (tempdf[ColumnName]>min_value)]
    for separator in separators:
        inf_entropy=GetEntropy(tempdf,ColumnName,AssociatedColumnName,int(round(separator,0)))
        CutPoints[inf_entropy]=separator
    return int(MinEntropySplit(CutPoints))
    
def Binning(tempdf,ColumnName,AssociatedColumnName,Bin_Number):
    BinPoints=list()
    #print("Number of bins now ",len(BinPoints)," Bin Points",BinPoints )
    min_value=int(round(min(tempdf[ColumnName])))
    max_value=int(round(max(tempdf[ColumnName]),0))
    Chosen_Separator=GetBin(min_value,max_value,tempdf,ColumnName,AssociatedColumnName)
    BinPoints.append(Chosen_Separator)
    Ben_length=len(BinPoints)
    while Ben_length<=Bin_Number/2:
        for i in range(0,Ben_length+1):
            if (i==0):
                min_value=int(round(min(tempdf[ColumnName])))
                max_value=BinPoints[i]
                #low_df=tempdf[(tempdf[ColumnName]<=Chosen_Separator)]
                Chosen_Separator=GetBin(min_value,max_value,tempdf,ColumnName,AssociatedColumnName)
                BinPoints.append(Chosen_Separator)
            elif(i==Ben_length):
                min_value=BinPoints[i-1]
                max_value=int(round(max(tempdf[ColumnName]),0))
                #high_df=tempdf[(tempdf[ColumnName]>Chosen_Separator)]
                Chosen_Separator=GetBin(min_value,max_value,tempdf,ColumnName,AssociatedColumnName)
                BinPoints.append(Chosen_Separator)
            else:
                min_value=BinPoints[i-1]
                max_value=BinPoints[i]
                #high_df=tempdf[(tempdf[ColumnName]>Chosen_Separator)]
                Chosen_Separator=GetBin(min_value,max_value,tempdf,ColumnName,AssociatedColumnName)
                BinPoints.append(Chosen_Separator)
        BinPoints=set(BinPoints)
        BinPoints=list(BinPoints)
        BinPoints=sorted(BinPoints)
        Ben_length=len(BinPoints)
    return BinPoints

def automated_dummy_creation(option):
    print("\n"*50)
    print("\n A41 Automated Dummy Creation and Transformation with Automated Supervised Binning\n (Option %s):\n" % option)
    devfile = input("\n Input training filename and path (dev.csv): ")
    if devfile =="":
        devfile="dev.csv"
    df= pd.read_csv(devfile)
    
    new_df_dummy=DummyTransform(df,['ico_var_61', 'ico_var_62', 'ico_var_63'])
   
    print("\n Data Set Dummy Creation\n")
    print(" This create new columns with the values that was dummy \ntransformed from the given columns")
    print(new_df_dummy.head(10))
    print("\nThis create new columns with the values that was dummy \ntransformed from the given columns")
    input(" \nPress enter to continue...")
    
    ColumnName='if_var_68'
    AssociatedColumnName='ob_target'
    #df = pd.read_csv("D:/IE Masters/Third Semester/Financial Analytics/dev.csv")
    new_df=selectBin(df,ColumnName,AssociatedColumnName)
    new_df.columns[len(new_df.columns)-1]
    print("\n Showing the selected column with its supervised binning \nthat was done in association of the Target variable")
    print(new_df[['if_var_68',new_df.columns[len(new_df.columns)-1]]])
    print("\n Showing the selected column with its supervised binning \nthat was done in association of the Target variable")
    input(" \nPress enter to continue...")
    return "0"   



### Inicia Programa
if __name__ == "__main__":
    main()
