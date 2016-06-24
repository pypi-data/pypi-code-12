import os


class BaseGenerator(object):
    @classmethod
    def as_generator(cls):
        def generator(flourish, url):
            self = cls(flourish, url)
            return self.generate()

        return generator

    def __init__(self, flourish, url):
        self.flourish = flourish
        self.url = url

    def generate(self):
        for _filter in self.flourish.all_valid_filters_for_url(self.url.name):
            _objects = self.get_objects(_filter)
            _context = self.get_context_data(_objects)
            _template = self.get_template(_objects)
            _render = self.render_template(_template, _context)
            _path = self.url.resolve(**_filter)
            self.output_to_file(_path, _render)

    def get_template(self, objects):
        return self.flourish.jinja.get_template(
            self.get_template_name(objects)
        )

    def get_objects(self, filter):
        return self.flourish.sources.filter(**filter)

    def render_template(self, template, context_data):
        return template.render(context_data).encode('UTF-8')

    def output_to_file(self, path, render):
        _output_file = self.get_output_filename(path)
        with open(_output_file, 'w') as _output:
            _output.write(render)

    def get_template_name(self, objects):
        return self.template_name

    def get_output_filename(self, path):
        _destination = '%s%s' % (self.flourish.output_dir, path)
        if _destination.endswith('/'):
            _destination = _destination + 'index.html'
        if not _destination.endswith('.html'):
            _destination = _destination + '.html'

        _directory = os.path.dirname(_destination)
        if not os.path.isdir(_directory):
            os.makedirs(_directory)
        return _destination

    def get_context_data(self, objects):
        _context = {}
        _context['objects'] = objects
        return _context


class PageGenerator(BaseGenerator):
    def get_context_data(self, objects):
        _context = super(PageGenerator, self).get_context_data(objects)
        _context['page'] = objects[0]
        _context.update(objects[0]._config)
        return _context

    def get_template_name(self, objects):
        if 'template' in objects[0]:
            return objects[0]['template']
        if 'type' in objects[0]:
            return '%s.html' % objects[0]['type']
        return 'page.html'


class IndexGenerator(BaseGenerator):
    template_name = 'index.html'

    def get_context_data(self, objects):
        _context = super(IndexGenerator, self).get_context_data(objects)
        _context['pages'] = objects
        return _context
