import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import KFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.linear_model import LogisticRegression as LR
from sklearn.tree import DecisionTreeClassifier as DT

class automodel:

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
        functions_name_list = ["Support vector machines", "Random forest", "K-nearest-neighbors", "Logistic Regression",
                               "Decision Tree Classifier"]
        model_list = [accuracy(y, run_cv(X, y, SVC)), accuracy(y, run_cv(X, y, RF)), accuracy(y, run_cv(X, y, KNN)),
                      accuracy(y, run_cv(X, y, LR)), accuracy(y, run_cv(X, y, DT))]

        # PRINT MODELS BY BEST OPTION
        ratio_frame = pd.DataFrame()
        for i in range(0, len(functions_name_list)):
            ratio_frame = ratio_frame.append({"Model": functions_name_list[i], "Accuracy": model_list[i]},
                                             ignore_index=True)
        ratio_frame.sort_values(by="Accuracy", ascending=False)
        print(ratio_frame)

dev = pd.read_csv("dev.csv")
oot = pd.read_csv("oot0.csv")
A = automodel(dev,oot,'ob_target')
