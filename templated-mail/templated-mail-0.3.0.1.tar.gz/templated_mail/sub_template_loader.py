import contextlib
import jinja2


class SubTemplateLoader(jinja2.ChoiceLoader):

    """
    A subclass of ChoiceLoader that takes a
    directory where templates can be found,
    as well as providing a contextmanager
    for adding a dict of extra string
    templates.

    """

    def __init__(self, search_path):
        self.search_path = search_path
        super(SubTemplateLoader, self).__init__([
            jinja2.FileSystemLoader(search_path),
            jinja2.DictLoader({}),
        ])

    @property
    def extra(self):
        return self.loaders[1].mapping

    @extra.setter
    def extra(self, extra):
        self.loaders[1].mapping = extra

    @contextlib.contextmanager
    def add_templates(self, templates):
        try:
            self.extra = templates
            yield self
        finally:
            self.extra = {}
