__all__ = (
    'RandomCV',
    'StratifiedCV',
    'GroupCV',
    'UserCV',
    'RandomTVH',
    'UserTVH',
    'StratifiedTVH',
    'GroupTVH'
)


def get_class(cv_method, validation_type):
    classes = {
        'CV': {
            'random': RandomCV,
            'stratified': StratifiedCV,
            'user': UserCV,
            'group': GroupCV,
        },
        'TVH': {
            'random': RandomTVH,
            'stratified': StratifiedTVH,
            'user': UserTVH,
            'group': GroupTVH,
        },
    }
    try:
        return classes[validation_type][cv_method]
    except KeyError:
        err_msg = 'Error in getting class for cv_method={} and validation_type={}'
        raise ValueError(err_msg.format(cv_method, validation_type))


class BasePartitioningMethod(object):

    """This is base class to describe partioning method
    with options"""

    cv_method = None
    validation_type = None
    seed = 0
    _data = None
    _static_fields = frozenset(['cv_method', 'validation_type'])

    def __init__(self, cv_method, validation_type, seed=0):
        self.cv_method = cv_method
        self.validation_type = validation_type
        self.seed = seed

    def collect_payload(self):
        """
        This method is should return dict that
        will be passed into request to datarobot cloud
        """
        keys = ('cv_method', 'validation_type', 'reps', 'user_partition_col',
                'training_level', 'validation_level', 'holdout_level', 'cv_holdout_level',
                'seed', 'validation_pct', 'holdout_pct', 'partition_key_cols')
        if not self._data:
            self._data = {key: getattr(self, key, None) for key in keys}
        return self._data

    def __repr__(self):
        if self._data:
            payload = {k: v for k, v in self._data.items()
                       if v is not None and k not in self._static_fields}
        else:
            self.collect_payload()
            return repr(self)
        return '{}({})'.format(self.__class__.__name__, payload)

    @classmethod
    def from_data(cls, data):
        """Can be used to instantiate the correct class of partitioning class
        based on the data
        """
        if data is None:
            return None
        cv_method = data.get('cv_method')
        validation_type = data.get('validation_type')
        other_params = {key: value for key, value in data.items()
                        if key not in ['cv_method', 'validation_type']}
        return get_class(cv_method, validation_type)(**other_params)


class BaseCrossValidation(BasePartitioningMethod):
    cv_method = None
    validation_type = 'CV'

    def __init__(self, cv_method, validation_type='CV'):
        self.cv_method = cv_method  # pragma: no cover
        self.validation_type = validation_type  # pragma: no cover


class BaseTVH(BasePartitioningMethod):
    cv_method = None
    validation_type = 'TVH'

    def __init__(self, cv_method, validation_type='TVH'):
        self.cv_method = cv_method  # pragma: no cover
        self.validation_type = validation_type  # pragma: no cover


class RandomCV(BaseCrossValidation):
    """A partition in which observations are randomly assigned to cross-validation groups
    and the holdout set.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    seed : int
        a seed to use for randomization
    """
    cv_method = 'random'

    def __init__(self, holdout_pct, reps, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.seed = seed  # pragma: no cover


class StratifiedCV(BaseCrossValidation):
    """A partition in which observations are randomly assigned to cross-validation groups
    and the holdout set, preserving in each group the same ratio of positive to negative cases as in
    the original data.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    seed : int
        a seed to use for randomization
    """
    cv_method = 'stratified'

    def __init__(self, holdout_pct, reps, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.seed = seed  # pragma: no cover


class GroupCV(BaseCrossValidation):
    """ A partition in which one column is specified, and rows sharing a common value
    for that column are guaranteed to stay together in the partitioning into cross-validation
    groups and the holdout set.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    partition_key_cols : list
        a list containing a single string, where the string is the name of the column whose
        values should remain together in partitioning
    seed : int
        a seed to use for randomization
    """
    cv_method = 'group'

    def __init__(self, holdout_pct, reps, partition_key_cols, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.partition_key_cols = partition_key_cols  # pragma: no cover
        self.seed = seed  # pragma: no cover


class UserCV(BaseCrossValidation):
    """ A partition where the cross-validation folds and the holdout set are specified by
    the user.

    Parameters
    ----------
    user_partition_col : string
        the name of the column containing the partition assignments
    cv_holdout_level
        the value of the partition column indicating a row is part of the holdout set
    seed : int
        a seed to use for randomization
    """
    cv_method = 'user'

    def __init__(self, user_partition_col, cv_holdout_level, seed=0):
        self.user_partition_col = user_partition_col  # pragma: no cover
        self.cv_holdout_level = cv_holdout_level  # pragma: no cover
        self.seed = seed  # pragma: no cover


class RandomTVH(BaseTVH):
    """Specifies a partitioning method in which rows are randomly assigned to training, validation,
    and holdout.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    seed : int
        a seed to use for randomization
    """
    cv_method = 'random'

    def __init__(self, holdout_pct, validation_pct, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.seed = seed  # pragma: no cover


class UserTVH(BaseTVH):
    """Specifies a partitioning method in which rows are assigned by the user to training,
    validation, and holdout sets.

    Parameters
    ----------
    user_partition_col : string
        the name of the column containing the partition assignments
    training_level
        the value of the partition column indicating a row is part of the training set
    validation_level
        the value of the partition column indicating a row is part of the validation set
    holdout_level
        the value of the partition column indicating a row is part of the holdout set (use
        None if you want no holdout set)
    seed : int
        a seed to use for randomization
    """
    cv_method = 'user'

    def __init__(self, user_partition_col, training_level, validation_level,
                 holdout_level, seed=0):
        self.user_partition_col = user_partition_col  # pragma: no cover
        self.training_level = training_level  # pragma: no cover
        self.validation_level = validation_level  # pragma: no cover
        self.holdout_level = holdout_level  # pragma: no cover
        self.seed = seed  # pragma: no cover


class StratifiedTVH(BaseTVH):
    """A partition in which observations are randomly assigned to train, validation, and
    holdout sets, preserving in each group the same ratio of positive to negative cases as in the
    original data.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    seed : int
        a seed to use for randomization
    """
    cv_method = 'stratified'

    def __init__(self, holdout_pct, validation_pct, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.seed = seed  # pragma: no cover


class GroupTVH(BaseTVH):
    """A partition in which one column is specified, and rows sharing a common value
    for that column are guaranteed to stay together in the partitioning into the training,
    validation, and holdout sets.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    partition_key_cols : list
        a list containing a single string, where the string is the name of the column whose
        values should remain together in partitioning
    seed : int
        a seed to use for randomization
    """
    cv_method = 'group'

    def __init__(self, holdout_pct, validation_pct, partition_key_cols,
                 seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.partition_key_cols = partition_key_cols  # pragma: no cover
        self.seed = seed  # pragma: no cover
