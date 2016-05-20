from ..core import Task


class jinja2(Task):
    def __init__(self, **context):
        try:
            from jinja2 import Template
        except ImportError as e:
            raise ImportError('To use jinja2() install Jinja2 first: pip install jinja2') from e
        self.template_cls = Template
        self.context = context

    def lazy_replace(self, c):
        text = b''.join(c).decode('utf-8')
        template = self.template_cls(text)
        output_text = template.render(**self.context)
        yield output_text.encode('utf-8')

    def process(self, inputs):
        for t, c, m in inputs:
            t = t.with_name(t.name.replace('.jinja2', ''))  # strip off any Jinja2 extension
            yield t, self.lazy_replace(c), m
