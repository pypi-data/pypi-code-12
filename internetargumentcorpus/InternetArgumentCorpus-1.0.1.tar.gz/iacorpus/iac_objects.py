import importlib
import os


def load_dataset(name: str, **kwargs):
    """This is a factory method, it merely calls 
    datasets.<dataset_name>.load_dataset()
    """
    kwargs['name'] = name
    assert name.isalnum()
    dataset_module = importlib.import_module("iacorpus.datasets."+name)
    dataset = dataset_module.load_dataset(**kwargs)
    return dataset


def load_connection(name: str, **kwargs):
    """This is mostly for legacy reasons"""
    dataset = load_dataset(name, **kwargs)
    return dataset.connection
