def mp(x, y, testSize=0.25, randomState=0, peceptronIteration = 20, perceptronLearningRate = 0.01, svmCost = 10, rfTrees = 10):

    from sklearn import cross_validation
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(x,y, test_size=testSize, random_state=randomState)

    from sklearn import linear_model
    perceptron = linear_model.Perceptron(n_iter = peceptronIteration, eta0=perceptronLearningRate)
    perceptron.fit(X_train, y_train)
    perceptronScore = perceptron.score(X_test, y_test)

    from sklearn.svm import SVC
    svm = SVC(kernel='rbf',C=svmCost)
    svm.fit(X_train, y_train)
    svmScore = svm.score(X_test, y_test)

    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier(n_estimators = rfTrees)
    rf.fit(X_train, y_train)
    rfScore = rf.score(X_test, y_test)

    print("The Accuracy on Test Set",
          "\n----------------------------")
    print("Perceptron    : %0.10f" %perceptronScore)
    print("SVM           : %0.10f" %svmScore)
    print("Random Forest : %0.10f" %rfScore)




''''
import pandas as pd
import numpy as np
data = pd.read_csv("/Users/timwang/Desktop/Term 3/Financial Analytics/Exercise 2/Material/MBD_FA_INDIVIDUAL_EXERCISE_CREATE_VARIABLE.csv", sep=',', decimal='.', header=0)
x = data.iloc[:, 2:-1]
y = np.squeeze(data.iloc[:, -1:].values)


data2 = pd.read_csv("/Users/timwang/Desktop/Term 3/Financial Analytics/Exercise 1/dev.csv", sep=',', decimal='.', header=0)
x2 = data2.iloc[:, 1:-1]
y2 = np.squeeze(data2.iloc[:, -1:].values)

mp(x2, y2)
'''
