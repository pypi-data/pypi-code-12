from iacorpus.datasets.generic.dataset import Dataset

class ConVoteDataset(Dataset):
    pass


def load_dataset(name='convote', **kwargs):
    kwargs['name'] = name
    return ConVoteDataset(**kwargs)
