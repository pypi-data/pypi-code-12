from iacorpus.datasets.convinceme.convinceme import ConvinceMeDataset

def load_dataset(name='convinceme', **kwargs):
    kwargs['name'] = name
    return ConvinceMeDataset(**kwargs)
