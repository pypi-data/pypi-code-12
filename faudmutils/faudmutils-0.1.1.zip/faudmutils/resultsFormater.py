import pandas as pd
import re
import sklearn
import numpy as np
from sklearn.externals import six


def format_results(dataset, classifier, scores, metric='roc_auc'):

    def mypp(params, offset=0, printer=repr):
        # Do a multi-line justified repr:
        options = np.get_printoptions()
        np.set_printoptions(precision=5, threshold=64, edgeitems=2)
        params_list = list()
        this_line_length = offset
        line_sep = ',\n' + (1 + offset // 2) * ' '
        for i, (k, v) in enumerate(sorted(six.iteritems(params))):
            if type(v) is float:
                # use str for representing floating point numbers
                # this way we get consistent representation across
                # architectures and versions.
                this_repr = '%s=%s' % (k, str(v))
            else:
                # use repr of the rest
                this_repr = '%s=%s' % (k, printer(v))
            if len(this_repr) > 500000000:
                this_repr = this_repr[:300] + '...' + this_repr[-100:]
            if i > 0:
                if (this_line_length + len(this_repr) >= 75 or '\n' in this_repr):
                    params_list.append(line_sep)
                    this_line_length = len(line_sep)
                else:
                    params_list.append(', ')
                    this_line_length += 2
            params_list.append(this_repr)
            this_line_length += len(this_repr)

        np.set_printoptions(**options)
        lines = ''.join(params_list)
        # Strip trailing space to avoid nightmare in doctests
        lines = '\n'.join(l.rstrip(' ') for l in lines.split('\n'))
        return lines

    sklearn.base._pprint = mypp

    results = pd.DataFrame({metric: scores})
    results['dataset'] = dataset
    clf = str(classifier)
    clf = re.sub(r"\n\s+", " ", clf)
    results['classifier'] = clf
    return results
