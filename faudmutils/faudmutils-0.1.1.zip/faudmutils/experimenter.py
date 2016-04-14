import os
import datetime
from sklearn.cross_validation import cross_val_score, StratifiedKFold
import pandas as pd
import numpy as np
import time

from resultsFormater import format_results


def n_cross_val_score(estimator, X, y=None, scoring='roc_auc', n_jobs=1,
                      verbose=0, fit_params=None, pre_dispatch='2*n_jobs', random_state=0,
                      runs=5, folds=5, dataset_name='data', output_path='results', reverse_cv=False):
    results = pd.DataFrame()
    tick = time.time()
    for i in range(random_state, random_state + runs):
        np.random.seed(i)
        cv = StratifiedKFold(y, n_folds=folds, shuffle=True)
        scores = cross_val_score(estimator=estimator, X=X, y=y, scoring=scoring, cv=cv, n_jobs=n_jobs, verbose=verbose,
                                 fit_params=fit_params, pre_dispatch=pre_dispatch)
        print str(i) + "\t" + str(np.mean(scores))
        results = pd.concat([results, format_results(dataset_name, estimator, scores)])
    if output_path is not None:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        runtime = int((time.time() - tick) / 60)
        timestamp = datetime.datetime.now().replace(microsecond=0).isoformat().replace(":", "_")
        results.to_csv(output_path + '/' + dataset_name + '-' + timestamp + '-' + str(runtime) + '.csv')
    return results
