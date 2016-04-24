import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


class SampleClass(object):
    def __init__(self, random_state=0):
        self.random_state = random_state
        self.fill = None

    def fit(self, X, y):
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X)
            y = pd.Series(y)

        X = self.imputer(X)
        self.scaler = StandardScaler().fit(X)
        X = self.scaler.transform(X)

        self.clf = SVC(
            kernel='rbf',
            C=10,
            gamma=0.1,
            random_state=self.random_state
        )

        self.clf.fit(X, y)

    def predict(self, X):
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X)

        X = self.imputer(X)
        X = self.scaler.transform(X)
        return self.clf.predict(X)

    def imputer(self, X):
        if self.fill is None:
            self.fill = pd.Series([X[c].value_counts().index[0]
                                   if X[c].dtype == np.dtype('O')
                                   else X[c].median()
                                   if X[c].dtype == np.dtype('int')
                                   else X[c].mean()
                                   for c in X],
                                  index=X.columns)
        return X.fillna(self.fill)
