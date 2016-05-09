from __future__ import absolute_import
# encoding: UTF-8
import six
from json import dumps
from datetime import datetime
from time import mktime
from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.filters import do_mark_safe
from jinja2.utils import contextfunction
from tml import full_version
from tml.config import CONFIG
from tml.logger import get_logger
from tml.session_vars import get_current_context
from tml.tokenizers.dom import DomTokenizer


__author__ = 'xepa4ep'


def ts():
    return int(mktime(datetime.utcnow().timetuple()))


def _make_new_callable(fn):

    def inner(*args, **kwargs):
        return fn(*args, **kwargs)
    return inner


def dummy_tr(label, data=None, description=None, options=None):
    logger = get_logger()
    logger.warning("You forget to install `tr(label, data=None, description=None, options=None)` helper for the following arguments: `label=%s`, `description=%s`", label, description)
    return None, label, None


SYSTEM_TEMPLATES = {
    'inline': """
    {% if data.caller == "middleware" or not data.force_injection %}
    <script>
      (function() {
        var script = window.document.createElement('script');
        script.setAttribute('id', 'tml-agent');
        script.setAttribute('type', 'application/javascript');
        script.setAttribute('src', '{{ data.agent_host }}');
        script.setAttribute('charset', 'UTF-8');

        script.onload = function() {
           Trex.init('{{ data.application_key }}', {{ data.agent_config|safe }});
        };
        window.document.getElementsByTagName('head')[0].appendChild(script);

      })();
    </script>
    {% endif %}
""",
    'language_selector': '<div data-tml-language-selector="{{ type }}" {{ opts }}></div>',
    'stylesheet_link': '<link href="{{ link }}" rel="stylesheet">'
}


class TMLExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['trs', 'tr', 'tropts', 'tml_inline', 'tml_language_selector', 'tml_stylesheet_link', 'trh'])

    def __init__(self, environment):
        super(TMLExtension, self).__init__(environment)
        self.environment.filters.update(trs=self.trs_filter)
        self.environment.globals.update(
            tr=dummy_tr,
            translate_trs=self._translate_trs,
            translate_tr=self._translate_tr
        )
        environment.extend(
            install_tr_callables=self._install_callables
        )

    def _install_callables(self, **callables):
        new_callables = {fn_key : _make_new_callable(fn) for fn_key, fn in six.iteritems(callables)}
        self.environment.globals.update(new_callables)

    def _fetch_tr(self):
        return self.environment.globals['tr']

    def parse(self, parser):
        """
        {% trs "Hello" %}
        {% tropts with source="" target_locale="" %}
        {% trs user.name, description="Hello" source="" target_locale="" %}
        ...
        {% endtropts %}
        """
        token = next(parser.stream)
        lineno = token.lineno
        fn_name = 'parse_{}'.format(token.value)
        if not hasattr(self, fn_name) or not callable(getattr(self, fn_name)):
            raise Exception("`%s` method does not exist. Add it to your extension" % fn_name)
        fn = getattr(self, fn_name)
        output = fn(parser=parser, lineno=lineno)
        return output


    def parse_tr(self, parser, lineno):
        node = nodes.Scope(lineno=lineno)
        assignments = []
        while parser.stream.current.type != 'block_end':
            lineno = parser.stream.current.lineno
            if assignments:
                parser.stream.expect('comma')
            target = parser.parse_assign_target(name_only=True)
            parser.stream.expect('assign')
            expr = parser.parse_expression()
            assignments.append(nodes.Keyword(target.name, expr, lineno=lineno))
        body = parser.parse_statements(('name:endtr',),
                                         drop_needle=True)
        return nodes.CallBlock(nodes.Call(
            nodes.Name('translate_tr', 'load'), [], assignments, None, None),
            [], [], body).set_lineno(lineno)

    def parse_trs(self, parser, lineno):
        lineno = lineno
        args = [parser.parse_expression()]
        variables = {}

        while parser.stream.current.type != 'block_end':
            parser.stream.expect('comma')
            name = parser.stream.expect('name')
            if name.value in variables:
                parser.fail('translatable variable %r defined twice.' %
                            name.value, name.lineno,
                            exc=TemplateAssertionError)
            if parser.stream.current.type == 'assign':
                next(parser.stream)
                variables[name.value] = var = parser.parse_expression()
            else:
                variables[name.value] = var = nodes.Name(name.value, 'load')
        kwargs =[]
        if 'description' in variables:
            kwargs = [
                nodes.Keyword('description', variables.get('description', ''))]

        return nodes.Output([nodes.Call(nodes.Name('translate_trs', 'load'), args, kwargs, None, None)]).set_lineno(lineno)

    def parse_trh(self, parser, lineno):
        node = nodes.Scope(lineno=lineno)
        assignments = []
        while parser.stream.current.type != 'block_end':
            lineno = parser.stream.current.lineno
            if assignments:
                parser.stream.expect('comma')
            target = parser.parse_assign_target(name_only=True)
            parser.stream.expect('assign')
            expr = parser.parse_expression()
            assignments.append(nodes.Keyword(target.name, expr, lineno=lineno))
        body = parser.parse_statements(('name:endtrh',),
                                         drop_needle=True)
        return nodes.CallBlock(nodes.Call(
            nodes.Name('translate_trh', 'load'), [], assignments, None, None),
            [], [], body).set_lineno(lineno)

    def parse_tropts(self, parser, lineno):
        """
        {% tropts source="index" %}
        {% tr %} {% endtr %}
        {% tr %} {% endtr %}
        {% tr %} {% endtr %}
        {% endtropts %}
        """
        node = nodes.Scope(lineno=lineno)
        assignments = []
        while parser.stream.current.type != 'block_end':
            lineno = parser.stream.current.lineno
            if assignments:
                parser.stream.expect('comma')
            key = parser.parse_assign_target()   # a=b (a is key)
            parser.stream.expect('assign')
            value = parser.parse_expression()  # a=b (b is expression)
            assignments.append(nodes.Keyword(key.name, value))


        node.body = parser.parse_statements(('name:endtropts',), drop_needle=True)
        for item in node.body:
            if isinstance(item, (nodes.Call, nodes.CallBlock)) and item.call.node.name in ('_translate_trs', '_translate_tr'):
                used_keys = set(arg.key for arg in item.call.args)
                allowed_assignments = [assign for assign in assignments
                                       if not assign.key in used_keys]
                item.call.args += allowed_assignments
        return node

    def parse_tml_inline(self, parser, lineno):
        caller="";
        while parser.stream.current.type != 'block_end':
            caller = parser.parse_expression().value

        context = get_current_context()
        agent_config = dict((k, v) for k, v in six.iteritems(CONFIG.get('agent', {})))
        agent_host = agent_config.get('host', CONFIG.agent_host())
        if agent_config.get('cache', None):
            t = ts()
            t -= (t % agent_config['cache'])
            agent_host += "?ts=%s" % t
        agent_config['locale'] = context.locale
        agent_config['source'] = context.source
        agent_config['css'] = context.application.css
        agent_config['sdk'] = full_version()
        languages = agent_config.setdefault('languages', [])
        for language in context.application.languages:
            languages.append({
                'locale': language.locale,
                'native_name': language.native_name,
                'english_name': language.english_name,
                'flag_url': language.flag_url})
        data = {
            'agent_config': dumps(agent_config),
            'agent_host': agent_host,
            'application_key': context.application.key,
            'caller': caller,
            'force_injection': agent_config.get('force_injection', False)
        }

        output = self.environment.from_string(SYSTEM_TEMPLATES['inline']).render(data=data)

        return nodes.Output([nodes.Const(do_mark_safe(output))]).set_lineno(lineno)

    def parse_tml_language_selector(self, parser, lineno):
        args = parser.parse_expression()
        variables = {}

        while parser.stream.current.type != 'block_end':
            parser.stream.expect('comma')
            name = parser.stream.expect('name')
            if name.value in variables:
                parser.fail('translatable variable %r defined twice.' %
                            name.value, name.lineno,
                            exc=TemplateAssertionError)
            if parser.stream.current.type == 'assign':
                next(parser.stream)
                variables[name.value] = var = parser.parse_expression()
            else:
                variables[name.value] = var = nodes.Name(name.value, 'load')


        data = {
            'type': args.value
        }
        if 'opts' in variables:
            data['opts'] = variables.get('opts', '').value
        else:
            data['opts'] = ""

        output = self.environment.from_string(SYSTEM_TEMPLATES['language_selector']).render(type=data['type'], opts=data['opts'])
        return nodes.Output([nodes.Const(do_mark_safe(output))]).set_lineno(lineno)

    def parse_tml_stylesheet_link(self,parser,lineno):
        ltr = parser.parse_expression()

        while parser.stream.current.type != 'block_end':
            parser.stream.expect('comma')
            rtl = parser.parse_expression()

        context = get_current_context()

        link = ltr.value
        if context.language.right_to_left:
            link = rtl.value

        output = self.environment.from_string(SYSTEM_TEMPLATES['stylesheet_link']).render(link=link)

        return nodes.Output([nodes.Const(do_mark_safe(output))]).set_lineno(lineno)

    def _translate_trs(self, value, description=None, **kwargs):
        opts = self._filter_options(kwargs)
        tr = self._fetch_tr()
        _, value, _err = tr(value, description=description, options=opts)
        return do_mark_safe(value)

    def _translate_tr(self, **kwargs):
        body = kwargs.pop('caller',)()
        description = kwargs.pop('description', '')
        options = kwargs.pop('options', {})
        options.update(self._filter_options(kwargs))
        tr = self._fetch_tr()
        _, value, _err = tr(body, data=kwargs, description=description, options=options)
        return do_mark_safe(value)

    def _translate_trh(self, **kwargs):
        body = kwargs.pop('caller',)()
        options = kwargs.pop('options', {})
        options.update(self._filter_options(kwargs))
        tokenizer = DomTokenizer(kwargs, options)
        value = tokenizer.translate(body)
        return do_mark_safe(value)

    def _filter_options(self, options):
        return {k: options[k] for k in
                CONFIG['supported_tr_opts'] if k in options}

    def trs_filter(self, value, *args):
        argc = len(args)
        data, description, options = {}, '', {}

        if argc > 0:
            description = args[0]
            if argc > 1:
                options = args[1]
                # if argc > 2:
                #     data = args[2]
        try:
            tr = self._fetch_tr()
            _, trans_value, _ = tr(
                value, data=data, description=description, options=options)
            return trans_value
        except Exception as e:
            get_logger().exception(e)
            return value