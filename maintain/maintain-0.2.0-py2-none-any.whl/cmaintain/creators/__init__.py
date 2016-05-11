import os
from toposort import toposort_flatten
from maintain.creators.base import Creator, ValidationError
from maintain.creators.license import LicenseCreator
from maintain.creators.readme import ReadmeCreator
from maintain.creators.git import GitCreator
from maintain.creators.gitignore import GitIgnoreCreator
from maintain.creators.github import GitHubCreator
from maintain.creators.python import PythonCreator
from maintain.creators.hooks import HookCreator


class DirectoryCreator(Creator):
    name = 'directory'

    def validate(self):
        if os.path.exists(self.destination):
            raise ValidationError('The directory {} already exists.'.format(self.destination))

    def create(self):
        os.mkdir(self.destination)


def load_creators(config, name):
    use_creator = lambda cls: cls.name in config.keys() and bool(config[cls.name])
    creators_cls = filter(use_creator, Creator.__subclasses__())
    dependencies = reduce(lambda x, y: x + y, map(lambda cls: cls.dependencies(), creators_cls))
    creators_cls = sort_creators(list(set(creators_cls + dependencies)))
    creators = map(lambda cls: cls(config, name), [DirectoryCreator] + creators_cls)
    for creator in creators:
        creator.creators = filter(lambda c: c != creator, creators)

    return creators


def sort_creators(creators):
    # Sort creators so dependencies are met in order
    include_creator = lambda creator: creator in creators
    dependencies = lambda cls: set(cls.dependencies() + filter(include_creator, cls.after()))
    graph = dict([(cls, dependencies(cls)) for cls in creators])
    return toposort_flatten(graph)

