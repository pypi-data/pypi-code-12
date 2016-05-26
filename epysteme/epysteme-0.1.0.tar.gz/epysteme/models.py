import numpy as np


class LinearRegressionModel(object):
    """Model for univariate multiple linear regression.

    The model supports ridge regression.
    """

    def __init__(self, data_set, features, target, lda=0):
        """Initialize a LinearRegressionModel object.

        Parameters
        ----------
        data_set : epysteme.DataSet
            The data set used to train and evaluate the model.
        features : iterable[str]
            Names of the features to use from the data set.
        target : str
            Name of the target feature in the data set.
        lda : optional[float]
            Lambda for ridge regression, default is 0.
        """
        self._data_set = data_set
        self._features = features
        self._target = target
        self._lambda = lda

        m = len(self._features) + 1
        self.beta_hat = np.zeros((m, 1))
        self.trained = False

    def train(self, subset=None):
        """Train the model.

        Training is done by finding the closed-form solution to the linear
        least squares problem (regularised if lambda is non-zero).

        Parameters
        ----------
        subset : optional[str]
            Name of the subset on which to train the model.
        """
        m = len(self._features) + 1
        xtx = np.zeros((m, m))
        xty = np.zeros((m, 1))

        if subset is None:
            w = self._data_set.windows(self._features, self._target, const=True)
        else:
            w = self._data_set[subset].windows(self._features,
                                               self._target,
                                               const=True)

        for x, y in w:
            xtx += np.dot(x.transpose(), x)
            xty += np.dot(x.transpose(), y)

        self.beta_hat = np.dot(np.linalg.inv(xtx + self._lambda * np.eye(m)),
                               xty)
        self.trained = True

    def predict(self, obs):
        """Predict value(s) of target feature for the given observation(s).

        Parameters
        ----------
        obs : array-like
            Observation(s) for which to predict the target feature.

        Returns
        -------
        float -or- numpy.ndarray
            Prediction(s) of the target feature.
        """
        return np.dot(self.beta_hat, obs)