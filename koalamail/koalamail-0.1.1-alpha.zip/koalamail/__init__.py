# -*- coding: utf-8 -*-
"""
    koalaemailrenderer.__init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Generate an instance of the Jinja2 template engine and store it as a class attr. This can then be used to
    generate formatted HTML for a variety of uses in your API, the most common being emails

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""
import jinja2


__author__ = 'Matt Badger'


class Jinja2TemplateEngine(object):
    """Wrapper for Jinja2 environment. Based on webapp2_extras.jinja2
    """

    #: Loaded configuration.
    config = None

    def __init__(self, engine_config, global_vars=None, filters=None, tests=None):
        """Initializes the Jinja2 object.

        :param engine_config:
            A dictionary of configuration values. See
            the available keys in :data:`default_config`.
        """

        self.global_template_variables = global_vars

        env_config = engine_config['environment_args'].copy()
        env_config['loader'] = jinja2.FileSystemLoader(engine_config['theme_base_template_path'])

        # Initialize the environment.
        env = jinja2.Environment(**env_config)

        if global_vars:
            env.globals.update(global_vars)

        if filters:
            env.filters.update(filters)

        # TODO: implement i18n that doesn't rely on webapp2 - requests will not be available to the API
        # if engine_config['enable_i18n']:
        #     # Install i18n.
        #     from webapp2_extras import i18n
        #     env.install_gettext_callables(
        #         lambda x: i18n.gettext(x),
        #         lambda s, p, n: i18n.ngettext(s, p, n),
        #         newstyle=True)
        #     env.filters.update({
        #         'format_date':      i18n.format_date,
        #         'format_time':      i18n.format_time,
        #         'format_datetime':  i18n.format_datetime,
        #         'format_timedelta': i18n.format_timedelta,
        #     })

        self.environment = env

    def render_template(self, _filename, **context):
        """Renders a template and returns a response object.

        :param _filename:
            The template filename, related to the templates directory.
        :param context:
            Keyword arguments used as variables in the rendered template.
            These will override values set in the request context.
        :returns:
            A rendered template.
        """
        return self.environment.get_template(_filename).render(**context)

    def get_template_attribute(self, filename, attribute):
        """Loads a macro (or variable) a template exports.  This can be used to
        invoke a macro from within Python code.  If you for example have a
        template named `_foo.html` with the following contents:

        .. sourcecode:: html+jinja

           {% macro hello(name) %}Hello {{ name }}!{% endmacro %}

        You can access this from Python code like this::

            hello = get_template_attribute('_foo.html', 'hello')
            return hello('World')

        This function comes from `Flask`.

        :param filename:
            The template filename.
        :param attribute:
            The name of the variable of macro to acccess.
        """
        template = self.environment.get_template(filename)
        return getattr(template.module, attribute)


class EmailRenderer(object):
    _render_engine = None

    @classmethod
    def configure(cls, configuration):
        j = Jinja2TemplateEngine(engine_config=configuration['jinja2_engine_config'])
        j.environment.filters.update({
            # Set filters.
            # ...
        })
        j.environment.globals.update({'getattr': getattr})
        if 'global_renderer_vars' in configuration:
            j.environment.globals.update(configuration['global_renderer_vars'])
        j.environment.tests.update({
            # Set test.
            # ...
        })
        cls._render_engine = j

    @classmethod
    def render(cls, template_path, template_vars):
        if cls._render_engine is None:
            raise AttributeError('Please configure the renderer before use')

        return cls._render_engine.render_template(template_path, **template_vars)

