import pandas as pd
import math
import itertools
from seldon.pipeline.util import Pipeline_wrapper
from sklearn.base import BaseEstimator
from sklearn.cross_validation import train_test_split
import logging
from seldon.pipeline import Seldon_KFold
import sys
import seldon.sklearn_estimator as ske
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDClassifier
from sklearn import metrics


logger = logging.getLogger(__name__)

class Blender(BaseEstimator):
    """
    simple blender of classifiers

    Parameters
    ----------

    """
    def __init__(self,clfs=[],blend_size=0.1,metric='accuracy'):
        self.clfs = clfs
        self.metric = metric
        self.blend_size=blend_size

    def get_scores(self):
        return self.scores

    def get_score(self):
        if len(self.scores) > 0:
            return sum(self.scores) / float(len(self.scores))
        else:
            return 0.0


    def fit(self,X,y=None):
        """

        Parameters
        ----------

        X : pandas dataframe 

        Returns
        -------
        self: object
        """

        blend_df = None
        scores = []
        pos = 1
        for clf in self.clfs:
            cv = Seldon_KFold(clf,5,metric=self.metric)
            cv.fit(X,y)
            logger.info("Classifier score %s%d %f",clf.__class__.__name__,pos,cv.get_score())
            scores.append(cv.get_score())
            b_preds = cv.predict_proba(X)
            df = pd.DataFrame({clf.__class__.__name__+str(pos):b_preds[:,1]})
            if blend_df is None:
                blend_df = df
            else:
                blend_df = pd.concat([blend_df,df],axis=1)

            pos += 1

        if y is None:
            y = X[self.clfs[0].get_target()].values
        blend_targets = pd.DataFrame({"target":y})
        blend_df = pd.concat([blend_df,blend_targets],axis=1)
        blend_clf = LogisticRegression()
        classifier = ske.SKLearnClassifier(clf=blend_clf,target="target")
        self.cv_blend = Seldon_KFold(classifier,5,metric=self.metric)
        self.cv_blend.fit(blend_df)


        logger.info("Individual scores %s",scores)
        logger.info("Cross validation score on blending %f",self.cv_blend.get_score())


        return self

    def transform(self,X):
        """
        Do nothing and pass input back
        """
        return X

    def predict_proba(self, X):
        blend_df = None
        pos = 1
        for clf in self.clfs:
            b_preds = clf.predict_proba(X)
            df = pd.DataFrame({clf.__class__.__name__+str(pos):b_preds[:,1]})
            if blend_df is None:
                blend_df = df
            else:
                blend_df = pd.concat([blend_df,df],axis=1)
            pos += 1

        pw = Pipeline_wrapper()
        pw.save_dataframe(blend_df,"./blend.csv",df_format="csv",csv_index=False)

        return self.cv_blend.predict_proba(blend_df)

    def get_class_id_map(self):
        return self.clfs[0].get_class_id_map()

