import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

def root_mean_squared_error(y, y_pred, **kwargs):
    return np.sqrt(abs(mean_squared_error(y, y_pred, **kwargs)))


def dashboard(df, df_name=None, cols=None, return_fig_axs=False):
    """Gives a quick overview of the variables.
    
    df : Pandas dataframe
    df_name : str, opt
        name of df
    cols: [str]
        list of columns to be plotted
    """
    
    if cols is None:
        cols = df.columns
    
    n_rows = 3
    n = int(np.ceil(len(cols)/n_rows))
    fig, axs = plt.subplots(n, n_rows, figsize=(20, 6 * n))
    fig.subplots_adjust(hspace=.2)
    axs = axs.flatten()
    
    for i, c in enumerate(cols):
        if df_name:
            axs[i].set_title(df_name + '\n' + c)
        else:
            axs[i].set_title(c)
        
        if df[c].dtype == np.float64 or df[c].dtype == np.int64:
            df_weights = np.ones_like(df[c].dropna().values)/float(len(df[c].dropna().values))
            df[c].dropna().hist(bins=20, ax=axs[i], weights=df_weights)

        else:
            df[c].value_counts(normalize=True)[:5].plot(kind='bar', ax=axs[i])
        
        axs[i].set_ylabel('Proportion')
    
    if return_fig_axs:
        return fig, axs


def how(df, model, n=10):
    """Returns feature importances for various sklearn models."""
    if hasattr(model, 'feature_importances_'):
        return sorted(zip(df.columns, model.feature_importances_), key = lambda x: x[-1], reverse=True)[:n]
    elif hasattr(model, 'coef_'):
        if model.coef_.ndim > 1:
            for c in model.coef_:
                return [sorted(zip(df.columns, model.coef_[c]), key = lambda x: abs(x[1]), reverse=True)[:n] for c in model_coef]
        else:
            return sorted(zip(df.columns, model.coef_), key = lambda x: abs(x[1]), reverse=True)[:n]
    else:
        return "Can't find feature importances."


def sample_weights(y):
    """Returns balanced sample weights."""
    class_weights = {k: 1./v for k, v in y.value_counts().iteritems()}
    sample_weights = y.map(class_weights).values
    return sample_weights