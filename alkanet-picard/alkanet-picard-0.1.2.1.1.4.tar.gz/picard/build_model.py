'''Utilities for parsing model configurations to keras models'''

import importlib

def get_layer(config):

    '''returns a layer matching the layer configuration'''

    package, name = config['type'].split('.')

    return getattr(
        importlib.import_module(
            'keras.layers.' + package
        ),
        name
    )(**config['options'])


def build_model(model_config):

    '''Returns a keras model matching the configuration'''

    from keras.models import Sequential

    model = Sequential()

    for layer in model_config['layers']:
        model.add(get_layer(layer))

    return model
