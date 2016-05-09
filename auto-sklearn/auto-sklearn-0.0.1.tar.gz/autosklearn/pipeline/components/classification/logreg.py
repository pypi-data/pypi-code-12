from ConfigSpace.configuration_space import ConfigurationSpace
from ConfigSpace.hyperparameters import UniformFloatHyperparameter
from autosklearn.pipeline.components.base import \
    AutoSklearnClassificationAlgorithm
from autosklearn.pipeline.constants import *


class LogisticRegressionClassifier(object):#AutoSklearnClassificationAlgorithm):
    def __init__(self, C, tol, random_state=None):
        self.C = C
        self.tol = tol
        self.random_state = random_state
        self.estimator = None

    def fit(self, X, y):
        from sklearn.linear_model import LogisticRegression
        from sklearn.multiclass import OneVsRestClassifier

        self.C = float(self.C)
        self.tol = float(self.tol)
        self.estimator = LogisticRegression(C=self.C, tol=self.tol,
                                            solver='lbfgs',
                                            multi_class='multinomial')
        if len(y.shape) > 1 and y.shape[1] > 1:
            self.estimator = OneVsRestClassifier(self.estimator, n_jobs=1)
            self.estimator.fit(X, y)
        else:
            self.estimator.fit(X, y)

        return self

    def predict(self, X):
        if self.estimator is None:
            raise NotImplementedError()
        return self.estimator.predict(X)

    def predict_proba(self, X):
        if self.estimator is None:
            raise NotImplementedError()
        return self.estimator.predict_proba(X)

    @staticmethod
    def get_properties(dataset_properties=None):
        return {'shortname': 'LogReg',
                'name': 'Logistic Regression Classifier',
                'handles_regression': False,
                'handles_classification': True,
                'handles_multiclass': True,
                'handles_multilabel': True,
                'is_deterministic': True,
                'input': (DENSE, SPARSE, UNSIGNED_DATA),
                'output': (PREDICTIONS,)}

    @staticmethod
    def get_hyperparameter_search_space(dataset_properties=None):
        cs = ConfigurationSpace()

        C = cs.add_hyperparameter(UniformFloatHyperparameter(
            "C", 1e-4, 1e4, log=True, default=1.0))
        tol = cs.add_hyperparameter(UniformFloatHyperparameter(
            "tol", 1e-5, 1e-3, log=True, default=0.0001))

        return cs

