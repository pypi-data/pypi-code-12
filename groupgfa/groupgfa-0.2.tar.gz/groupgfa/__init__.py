import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import KFold
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier as ADA
from sklearn.ensemble import GradientBoostingClassifier as GBC
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.linear_model import SGDClassifier as SGDC
import tkinter as tk
from tkinter.filedialog import askopenfilename
import pandas.core.algorithms as algos


class autoselectModel:
    def __init__(self, df):
        #Importing Dataset

        #all lowercase names
        df.columns = [x.lower() for x in df.columns]


        target = [col for col in df.columns if 'target' in col]
        target = ''.join(target)


        #Setting TARGET VARIABLE equal to y
        y = df[target]

        #Dropping ID and Target from varibales included in models
        to_drop = [target, 'id']
        in_model = df.drop(to_drop, axis=1)

        #setting x as a matrix including the selected variables in the dataset
        X = in_model.as_matrix().astype(np.float)

        #Scaling variables to be used in the models
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        #Running kfold cross validation function with 5 folds


        def run_cv(X, y, clf_class, **kwargs):
            kf = KFold(len(y), n_folds=5, shuffle=True)
            y_pred = y.copy()

            for train_index, test_index in kf:
                X_train, X_test = X[train_index], X[test_index]
                y_train = y[train_index]
                clf = clf_class(**kwargs)
                clf.fit(X_train,y_train)
                y_pred[test_index] = clf.predict(X_test)
            return y_pred


        def accuracy(y_true,y_pred):
            return np.mean(y_true == y_pred)

        #Adding Model names and model functions to lists
        MODEL_name = ["Support vector machines", "Random forest", "K-nearest-neighbors", "AdaBoost", "Gradient Boosting", "Stochastic Gradient Descent"]
        MODEL = [SVC, RF, KNN, ADA, GBC, SGDC]

        #number of elements in MODEL list to iterate based on list length
        index_num = len(MODEL)

        #Populating list d with accuracy for each model
        d = []
        for i in range(index_num):
                d.append({'Model': MODEL_name[i], 'Accuracy': accuracy(y, run_cv(X, y, MODEL[i]))})

        #creating dataframe from list d
        df = pd.DataFrame(d)

        #sorting values by accuracy
        top_models = df.sort_values(by='Accuracy', ascending=False)
        print(top_models, "\n\n")


        print("This Automated method comparison and choosing algorithm suggests you use the following algorithm:")
        print(top_models.iloc[0])

class humanClean:
    def __init__(self, df):

        #all lowercase names
        df.columns = [x.lower() for x in df.columns]

        target = [col for col in df.columns if 'target' in col]
        target = ''.join(target)


        #GIVE CHOICE TO drop ID & TARGET



        dfdropped = df[['id', target]]
        print(dfdropped)
        to_drop = ['id', target]
        dfc = df.drop(to_drop, axis=1)


        choice2 = str(input("\nTo replace NAs with mean enter M. To replace with 0s enter 0? (M/0) \n"))
        if choice2 == 'M':
            dfc.fillna(dfc.mean(),inplace=True)

        elif choice2 == '0':
            dfc = dfc.fillna(0)


        #GIVE CHOICE TO NORMALIZE ALL VARIABLES
        choice3 = str(input("\nWould you like to normalize all variables? (Y/N) \n"))

        if choice3 == 'Y':
            for var_name in dfc:
                dfc[var_name] = (dfc[var_name]- dfc[var_name].mean()) / (dfc[var_name].max() - dfc[var_name].min())

        clean = pd.concat([dfdropped, dfc], axis=1)
        clean.to_csv("cleaneddataset.csv")

class autoClean:
    def __init__(self, df):

        #all lowercase names
        df.columns = [x.lower() for x in df.columns]

        target = [col for col in df.columns if 'target' in col]
        target = ''.join(target)


        #GIVE CHOICE TO drop ID & TARGET



        dfdropped = df[['id', target]]
        print(dfdropped)
        to_drop = ['id', target]
        dfc = df.drop(to_drop, axis=1)


        for column in dfc.columns:
            print(dfc[column])
            # Replace NaNs with the median or mode of the column depending on the column type


            if dfc[column].dtypes == 'int64' or dfc[column].dtypes == 'float64':

                mean = dfc[column].mean()
                std = 1.5*dfc[column].std()
                dfc[column] = dfc[column].apply(lambda y: dfc[column].median() if(abs(y - mean >std)) else y)

                n_rows = len(dfc.columns)
                negative_perc = np.sum((dfc[column] < 0))/n_rows
                dfc[column] = dfc[column].apply(lambda y: -(y) if (y<0 and negative_perc >= 0.05) else y)

            # Encode all strings with numerical equivalents
            if str(dfc[column].values.dtype) == 'object':
                column_encoder = LabelEncoder().fit(dfc[column].values)

                dfc[column] = column_encoder.transform(dfc[column].values)
            print(dfc[column].dtype)


        clean = pd.concat([dfdropped, dfc], axis=1)
        clean.to_csv("autocleaneddataset.csv")

class humanVariableCreate:
    def __init__(self, df):

        df.columns = [x.lower() for x in df.columns]

        target = [col for col in df.columns if 'target' in col]
        target = ''.join(target)


        #GIVE CHOICE TO drop ID & TARGET



        dfdropped = df[['id', target]]
        print(dfdropped)
        to_drop = ['id', target]
        dfc = df.drop(to_drop, axis=1)






        # In[4]:

        createVarQues = input('Would you like to continue to create your own variables? (Y/N)\n')


        # In[5]:

        ######################Variables Creations##################################
        while createVarQues == 'Y':
            ################Sum + ############################
            sumQues = input('Would you like to make a summation? (Y/N)\n')
            while sumQues == 'Y':
                print(dfc.columns.values)
                VarSumList = input("Input variables that you want to sum, delimiter ',' \n")
                VarSumList = VarSumList.replace(" ", "")
                #LongTermDebt_DeudasLargoPlazo_2012,ShortTermDebt_DeudasCortoPlazo_2012
                VarSumList = VarSumList.split(",")
                columnName = input('Enter new column name')
                dfc[columnName] = 0
                print(len(VarSumList))
                for i in range(len(VarSumList)):
                    dfc[columnName] += dfc[VarSumList[i]]
                    i+=1
                sumQues = input('Would you like to make another summation? (Y/N)\n')
            ##############division for ration########################
            RatioQues = input('Would you like to make a division/ratio calculation?(Y/N)\n')
            while RatioQues == 'Y':
                print(dfc.columns.values)
                RatioVarList = input("Input variables that you want to divide, delimiter ','\n")
                RatioVarList = RatioVarList.replace(" ", "")
                RatioVarList = RatioVarList.split(",")
                columnName = input('Enter new column name\n')
                dfc[columnName] = 1
                for i in range(len(RatioVarList)):
                    if i == 0:
                        dfc[columnName] = dfc[RatioVarList[i]] / dfc[columnName]
                    else:
                        dfc[columnName] = dfc[columnName] / dfc[RatioVarList[i]]
                RatioQues = input('Would you like to make a new division/ratio calculation?(Y/N)\n')
            ##################substraction#################################
            substractionQues = input('Would you like to make a Substraction calculation?(Y/N)\n')
            while substractionQues == 'Y':
                print(dfc.columns.values)
                SubstractionVarList = input("Input variables that you want to substract, delimiter ','\n")
                SubstractionVarList = SubstractionVarList.replace(" ", "")
                SubstractionVarList = SubstractionVarList.split(",")
                columnName = input('Enter new column name\n')
                dfc[columnName] = 0
                for i in range(len(SubstractionVarList)):
                    if i == 0:
                        dfc[columnName] = dfc[SubstractionVarList[i]] - dfc[columnName]
                    else:
                        dfc[columnName] = dfc[columnName] - dfc[SubstractionVarList[i]]
                substractionQues = input('Would you like to make a new substraction calculation?(Y/N)\n')
            #################Multiplication###################################
            MultiplicationQues = input('Would you like to make a multiplication calculation? (Y/N)\n')
            while MultiplicationQues == 'Y':
                print(dfc.columns.values)
                MultiplicationVarList = input("Input variables that you want to multiply, delimiter ','\n")
                MultiplicationVarList = MultiplicationVarList.replace(" ", "")
                MultiplicationVarList = MultiplicationVarList.split(",")
                MultiplicationVarList = MultiplicationVarList.replace("'", "")
                columnName = input('Enter new column name')
                dfc[columnName] = 1
                for i in range(len(MultiplicationVarList)):
                    dfc[columnName] = df[MultiplicationVarList[i]] * dfc[columnName]
                MultiplicationQues = input('would you like to make a new multiplication calculation?(Y/N)\n')
            #################Modulus##########################################
            ModulusQues = input('Would you like to make a modulus calculation? (Y/N)\n')
            while ModulusQues == 'Y':
                print(dfc.columns.values)
                ModulusVarList = input("Input variables that you want to apply modulus on, delimiter ','\n")
                ModulusVarList = ModulusVarList.replace(" ", "")
                ModulusVarList = ModulusVarList.split(",")
                ModulusVarList = ModulusVarList.replace("'", "")
                columnName = input('Enter new column name\n')
                dfc[columnName] = 1
                for i in range(len(ModulusVarList)):
                    if i == 0:
                        dfc[columnName] = dfc[ModulusVarList[i]] / dfc[columnName]
                    else:
                        dfc[columnName] = dfc[columnName] / dfc[ModulusVarList[i]]
                ModulusQues = input('Would you like to make a new modulus calculation?(Y/N)\n')

            print('Here are the dataframe you creates to run a classification decision tree\n')
            print(dfc.columns.values)
            createVarQues = input('Would you like to go through the process of creating your own variables again? (Y/N)\n')


        # In[36]:
        #dfc = dfc.fillna(0)
        created = pd.concat([dfdropped, dfc], axis=1)
        created.to_csv("createdvariablesdataset.csv")

class autoVariableCreate:
    def __init__(self, df):



        df.columns = [x.lower() for x in df.columns]

        target = [col for col in df.columns if 'target' in col]
        target = ''.join(target)

        dfdropped = df[['id', target]]
        to_drop = ['id', target]
        dfc = df.drop(to_drop, axis=1)

        #num_variables = len(dfc.columns.tolist()) - 5
        #r = random.randint(0, num_variables)
        #print(r, r+5)

        dfc_subset = pd.DataFrame()
        col_names = dfc.columns.tolist()
        print(col_names)
        print(type(col_names))
        for i in range(len(col_names)):
            if dfc[col_names[i]].max() - dfc[col_names[i]].min() > 5:
                dfc_subset[col_names[i]] = df[col_names[i]]
        print(dfc_subset)



        df_names = dfc_subset.columns.values
        index = len(df_names) - 1

        #CREATION OF VARIABLES
        for i in np.delete(df_names, index):
            for j in np.delete(df_names, index):
                dfc[i+"/"+j] = np.where(dfc[j]==0,0,dfc[i]/dfc[j])
                dfc[i+"*"+j] = dfc[i]*dfc[j]
                dfc[i+"-"+j] = dfc[i]+dfc[j]
                dfc[i+"+"+j] = dfc[i]+dfc[j]

        #DUMMY AND BINNING
        col_names_subset = dfc_subset.columns.tolist()
        dfc_bins = pd.DataFrame()
        for col in range(len(col_names_subset)):
            bins = algos.quantile(np.unique(dfc_subset[col_names_subset[col]]), np.linspace(0, 1, 11))
            result = pd.tools.tile._bins_to_cuts(dfc_subset[col_names_subset[col]], bins, include_lowest=True)
            dfc_bins[col_names_subset[col]] = result
            #dfc_bins = pd.qcut(dfc_subset[col_names_subset[col]], 5)



        print("\n Exported csv file with variables created from all possible ratios, binning, and created dummy variables for a subset of variables")


        autocreated = pd.concat([dfdropped, dfc, dfc_bins], axis=1)
        autocreated.to_csv("autocreatedvariablesdataset.csv")


