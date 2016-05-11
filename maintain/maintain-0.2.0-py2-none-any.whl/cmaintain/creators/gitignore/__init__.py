import os
import six
from maintain.creators.base import Creator, ValidationError
from maintain.creators.git import GitCreator


class GitIgnoreCreator(Creator):
    name = 'gitignore'

    def __str__(self):
        return '{} ({})'.format(self.name, os.path.basename(self.ignore))

    @classmethod
    def dependencies(cls):
        return [GitCreator]

    @classmethod
    def after(cls):
        return [GitCreator]

    def validate(self):
        self.ignore = self.config['gitignore']

        if not isinstance(self.ignore, six.string_types):
            raise ValidationError('Improperly configured')

        if os.path.isfile(self.ignore):
            return

        relative = os.path.join(os.path.dirname(self.config.path), self.ignore)
        if os.path.isfile(relative):
            self.ignore = relative
            return

        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        match_template = lambda path: os.path.basename(path).lower() == '{}.gitignore'.format(self.ignore).lower()
        templates = filter(match_template, os.listdir(templates_dir))

        if len(templates) == 0:
            raise ValidationError('Template {} not found'.format(self.ignore))

        self.ignore = templates[0]


    def create(self):
        pass
