from sets.core import Step, Dataset


class Normalize(Step):

    def __init__(self, fit_dataset):
        self._mean = fit_dataset.data.mean(axis=0)
        self._std = fit_dataset.data.std(axis=0)
        self._shape = fit_dataset.data.shape[1:]

    def __call__(self, dataset):
        if dataset.data.shape[1:] != self._shape:
            raise ValueError('examples must have the same vector size')
        data = (dataset.data - self._mean) / self._std
        return Dataset(data, dataset.target)
