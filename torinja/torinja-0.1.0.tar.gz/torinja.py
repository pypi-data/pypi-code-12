import logging

import jinja2


logger = logging.getLogger(__name__)


__version__ = '0.1.0'


class LazyMarkup:

    __slots__ = '_callable'

    def __init__(self, callable):
        self._callable = callable

    def __html__(self):
        return self._callable()


class TornadoCompatibleJinja2Template(jinja2.Template):

    def generate(self, **kwargs):
        try:
            kwargs['xsrf_form_html'] = LazyMarkup(kwargs['xsrf_form_html'])
        except KeyError:
            pass
        return self.render(**kwargs)


class Jinja2Env(jinja2.Environment):

    template_class = TornadoCompatibleJinja2Template

    def __init__(self, **kwargs):
        kwargs.setdefault('autoescape', True)
        super(Jinja2Env, self).__init__(**kwargs)

    def reset(self):
        logger.warn('%s.reset is not implemented', self.__class__.__name__)

    @property
    def load(self):
        return self.get_template
