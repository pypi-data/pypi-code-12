from __future__ import absolute_import

def load(path):
    '''
    from baiji.util import yaml
    foo = yaml.load('foo.yaml')
    '''
    import yaml
    with open(path, 'r') as f:
        return yaml.load(f)
