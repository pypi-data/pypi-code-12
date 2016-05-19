__all__ = (
    'RandomCV',
    'StratifiedCV',
    'GroupCV',
    'UserCV',
    'RandomTVH',
    'UserTVH',
    'DateTVH',
    'StratifiedTVH',
    'GroupTVH'
)


def get_class(cv_method, validation_type):
    if validation_type == 'CV':
        if cv_method == 'random':
            return RandomCV
        if cv_method == 'stratified':
            return StratifiedCV
        if cv_method == 'user':
            return UserCV
        if cv_method == 'group':
            return GroupCV
    elif validation_type == 'TVH':
        if cv_method == 'random':
            return RandomTVH
        if cv_method == 'stratified':
            return StratifiedTVH
        if cv_method == 'user':
            return UserTVH
        if cv_method == 'group':
            return GroupTVH
        if cv_method == 'date':
            return DateTVH
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
        if not self._data:
            data = {
                "cv_method": getattr(self, 'cv_method', None),
                "validation_type": getattr(self, 'validation_type', None),
                "reps": getattr(self, 'reps', None),
                "user_partition_col": getattr(self, 'user_partition_col', None),
                "training_level": getattr(self, 'training_level', None),
                "validation_level": getattr(self, 'validation_level', None),
                "holdout_level": getattr(self, 'holdout_level', None),
                "cv_holdout_level": getattr(self, 'cv_holdout_level', None),
                "seed": getattr(self, 'seed', None),
                "validation_pct": getattr(self, 'validation_pct', None),
                "holdout_pct": getattr(self, 'holdout_pct', None),
                "datetime_col": getattr(self, 'datetime_col', None),
                "partition_key_cols": getattr(self, 'partition_key_cols', None),
            }
            self._data = data

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
    cv_method = 'random'

    def __init__(self, holdout_pct, reps, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.seed = seed  # pragma: no cover


class StratifiedCV(BaseCrossValidation):
    cv_method = 'stratified'

    def __init__(self, holdout_pct, reps, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.seed = seed  # pragma: no cover


class GroupCV(BaseCrossValidation):
    cv_method = 'group'

    def __init__(self, holdout_pct, reps, partition_key_cols, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.partition_key_cols = partition_key_cols  # pragma: no cover
        self.seed = seed  # pragma: no cover


class UserCV(BaseCrossValidation):
    cv_method = 'user'

    def __init__(self, user_partition_col, cv_holdout_level, seed=0):
        self.user_partition_col = user_partition_col  # pragma: no cover
        self.cv_holdout_level = cv_holdout_level  # pragma: no cover
        self.seed = seed  # pragma: no cover


class RandomTVH(BaseTVH):
    cv_method = 'random'

    def __init__(self, holdout_pct, validation_pct, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.seed = seed  # pragma: no cover


class UserTVH(BaseTVH):
    cv_method = 'user'

    def __init__(self, user_partition_col, training_level, validation_level,
                 holdout_level, seed=0):
        self.user_partition_col = user_partition_col  # pragma: no cover
        self.training_level = training_level  # pragma: no cover
        self.validation_level = validation_level  # pragma: no cover
        self.holdout_level = holdout_level  # pragma: no cover
        self.seed = seed  # pragma: no cover


class DateTVH(BaseTVH):
    cv_method = 'date'

    def __init__(self, holdout_pct, validation_pct, datetime_col,
                 seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.datetime_col = datetime_col  # pragma: no cover
        self.seed = seed  # pragma: no cover


class StratifiedTVH(BaseTVH):
    cv_method = 'stratified'

    def __init__(self, holdout_pct, validation_pct, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.seed = seed  # pragma: no cover


class GroupTVH(BaseTVH):
    cv_method = 'group'

    def __init__(self, holdout_pct, validation_pct, partition_key_cols,
                 seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.partition_key_cols = partition_key_cols  # pragma: no cover
        self.seed = seed  # pragma: no cover
