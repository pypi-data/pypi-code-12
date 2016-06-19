import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import KFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier as randfor
from sklearn.neighbors import KNeighborsClassifier as knneigh
from sklearn.linear_model import LogisticRegression as LR
from sklearn.tree import DecisionTreeClassifier as decision

class manumodel:

    def __init__(self, traindata, testdata, target):
        '''Constructor for this class'''
        self.traindata = pd.DataFrame(traindata)
        self.testdata = pd.DataFrame(testdata)
        self.target = target
        self.main()

    def main(self):
        y = self.traindata[self.target]

        to_drop = ['ob_target', 'id']
        in_model = self.traindata.drop(to_drop, axis=1)

        X = in_model.as_matrix().astype(np.float)
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        # Using K-Folds to partition the data between test and train
        def run_cv(X, y, clf_class, **kwargs):
            kf = KFold(len(y), n_folds=5, shuffle=True)
            y_pred = y.copy()

            for train_index, test_index in kf:
                X_train, X_test = X[train_index], X[test_index]
                y_train = y[train_index]
                clf = clf_class(**kwargs)
                clf.fit(X_train, y_train)
                y_pred[test_index] = clf.predict(X_test)
            return y_pred

        # Run Model
        def accuracy(y_true, y_pred):
            return np.mean(y_true == y_pred)

        # Create List of Models and Names of them
        functions_name_list = ["Support vector machines", "Random forest", "K-nearest-neighbors", "Logistic Regression","Decision Tree Classifier"]
        model_list = [accuracy(y, run_cv(X, y, SVC)),accuracy(y, run_cv(X, y, randfor)),accuracy(y, run_cv(X, y, knneigh)),accuracy(y, run_cv(X, y, LR)),accuracy(y, run_cv(X, y, decision))]

        # ASK THE USER WHAT ITS INTENDED TO DO :
        answer2 = str(input("Which Model do you want to use?\n K-nearest-neighbors(KNN)\n Logistic Regression(LG)\n Decision Tree(DT)\n Random Forest(RF)\n Support vector machines(SVMS)\n Enter abbreviation for each model  \n"))
        KNN = "knn"
        LG = "lg"
        DT = "dt"
        RF = "rf"
        SVMS = "svms"

        if answer2.lower() == SVMS.lower():
            print(functions_name_list[0], model_list[0])
        elif answer2.lower() == RF:
            print(functions_name_list[1], model_list[1])
        elif answer2.lower() == KNN:
            print(functions_name_list[2], model_list[2])
        elif answer2.lower() == LG:
            print(functions_name_list[3], model_list[3])
        elif answer2.lower() == DT:
            print(functions_name_list[4], model_list[4])

# dev = pd.read_csv("dev.csv")
# oot = pd.read_csv("oot0.csv")
# A = manumodel(dev,oot,'ob_target')
