from iacorpus.datasets.generic.dataset import Dataset

class FourForumsDataset(Dataset):
    pass


def load_dataset(name='fourforums', **kwargs):
    kwargs['name'] = name
    return FourForumsDataset(**kwargs)
