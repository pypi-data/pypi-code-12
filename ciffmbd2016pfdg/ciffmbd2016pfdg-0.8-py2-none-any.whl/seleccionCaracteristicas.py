#  Elegimos el orden de importancia de las variables

import pandas as pd
import numpy as np
from math import sqrt
from sklearn.linear_model import LinearRegression


def algStepwise(x_train, x_test, y_train, y_test):

    # Modelo para realizar los ajustes
    model = LinearRegression()
    features = list(x_train.columns)
    
    # Variable para almecena los indices de la lista de atributos usados
    feature_order =  []
    feature_error = []

    # Iteracion sobre todas las variables
    for i in range(len(features)):
        idx_try = [val for val in range(len(features)) if val not in feature_order]

        iter_error = []

        for i_try in idx_try:
            useRow = feature_order[:]
            useRow.append(i_try)

            use_train = x_train[x_train.columns[useRow]]
            use_test = x_test[x_train.columns[useRow]]

            model.fit(use_train, y_train)
            rmsError = np.linalg.norm((y_test - model.predict(use_test)), 2)/sqrt(len(y_test))
            iter_error.append(rmsError)

        pos_best = np.argmin(iter_error)
        feature_order.append(idx_try[pos_best])
        feature_error.append(iter_error[pos_best])
    
    ratios = []
    
    for i in range(len(features)):
        ratios.append(features[feature_order[i]])
    
    return ratios
