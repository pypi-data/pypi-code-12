from sets.core import Step, Dataset


class Split(Step):

    def __init__(self, *ratios):
        ratios = ratios or 0.66
        ratios = [0] + list(ratios) + [len(ratios)]
        if list(ratios) != sorted(ratios):
            raise ValueError('ratios must be in order')
        if len(ratios) != len(set(ratios)):
            raise ValueError('ratios must be unique')
        self._ratios = ratios

    def __call__(self, dataset):
        splits = [int(len(dataset) * x) for x in self._ratios]
        for start, end in zip(splits[:-1], splits[1:]):
            data = dataset.data[start:end]
            target = dataset.target[start:end]
            yield Dataset(data, target)
