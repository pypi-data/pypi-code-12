# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path
import pkgutil
import re
import operator
import pydoc
import inspect
import sys

import docutils.core

from django.conf import settings
from django.conf.urls import patterns, url
from django.views import generic
from django import http
from django.db import models, router
from django.utils.importlib import import_module
from django.core.exceptions import ViewDoesNotExist


class MyHtmlDoc(pydoc.HTMLDoc):
    def page(self, title, contents):
        raise RuntimeError()

    def document(self, object, name=None, *args):
        args = (object, name) + args

        if (hasattr(object, "__get__") and not hasattr(object, "__set__")):
            # method (aa used memoize)
            return self.docroutine(*args)
        else:
            return pydoc.HTMLDoc.document(self, *args)

my_html = MyHtmlDoc()


def get_fn_argspec(object):
    if inspect.ismethod(object):
        object = object.im_func

    if inspect.isfunction(object):
        args, varargs, varkw, defaults = inspect.getargspec(object)
        argspec = inspect.formatargspec(
            args, varargs, varkw, defaults)
    else:
        argspec = '(...)'
    return argspec


def get_method_flag(kind):
    if kind == 'class method':
        return 'C'
    elif kind == 'static method':
        return 'S'
    else:
        return ''


def get_cls_methods(object, name_prefix=''):
    """ return [{
        name:,
        doc:,
        argspec:,
        flag:,
        is_property:,
    }]
    """

    def make_obj(name, kind, cls, value, val):
        is_property = isinstance(val, property)

        return dict(
            name=name_prefix + name,
            doc=pydoc.getdoc(val),
            argspec=get_fn_argspec(val),
            flag='P' if is_property else get_method_flag(kind),
            is_property=is_property
        )

    # (name, kind, cls, value)
    methods = []
    for name, kind, cls, value in pydoc.classify_class_attrs(object):
        if cls is object and kind.endswith('method') and not name.startswith('_'):
            val = getattr(cls, name)
            if isinstance(val, models.Manager):
                if val.__class__ is not models.Manager:
                    methods.extend(get_cls_methods(val.__class__, name_prefix='{}.'.format(name)))
            else:
                methods.append(make_obj(name, kind, cls, value, val))

    return methods


class Index(generic.TemplateView):
    template_name = 'xray/index.html'


class DocBase(generic.TemplateView):
    page = None
    request = None
    args = None
    kwargs = None
    page_routings = None
    name = None

    '''
    page_routings = (
        (r'^$', 'index'),
    )
    '''

    @classmethod
    def get_urls(cls):
        if not cls.page_routings:
            raise RuntimeError('Must impl get_urls or setup page_routings')

        urls = [
            url(
                re_,
                cls.as_view(page=page),
                name='xray.{}.{}'.format(cls.name, page)
            )
            for re_, page in cls.page_routings
        ]
        return patterns('', *urls)

    def bad_request(self, request, *args, **kwargs):
        return http.HttpResponseBadRequest()

    def get_handler(self):
        if self.page is None:
            return None

        if self.request.method.lower() not in self.http_method_names:
            return self.http_method_not_allowed

        method_name = '{}_{}'.format(self.request.method.lower(), self.page)
        return getattr(self, method_name, self.bad_request)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        handler = self.get_handler()

        self.template_name = self._get_template_name()

        return handler(request, *args, **kwargs)

    def _get_template_name(self):
        return None

    def get_context_data(self, **kwargs):
        ctx = super(DocBase, self).get_context_data(**kwargs)

        return ctx

    def render_with_ctx(self, *args, **kwargs):
        ctx = self.get_context_data(**self.kwargs)

        for arg in args:
            ctx.update(arg)

        ctx.update(kwargs)

        return self.render_to_response(ctx)


class ModelsDoc(DocBase):
    name = 'models'
    page_routings = (
        (r'^$', 'index'),
    )

    def _get_template_name(self):
        return 'xray/models/index.html'

    def get_index(self, req, *args, **kwargs):
        ctx = {}
        ctx['models'] = sorted(self._get_all_models(), key=operator.itemgetter('group_name', 'name'))

        return self.render_with_ctx(ctx)

    @classmethod
    def _register_rs_role(cls):
        from django.contrib.admindocs.utils import ROLES, create_reference_role

        MY_ROLES = {
            'xraymodel': '%s/models/#%s',
        }

        _rs_registered_flag_key = '_rs_registered_flag'

        if not getattr(cls, _rs_registered_flag_key, False):
            setattr(cls, _rs_registered_flag_key, True)
            for name, urlbase in MY_ROLES.items():
                create_reference_role(name, urlbase)
            ROLES.update(MY_ROLES)

    @classmethod
    def _get_all_models(cls):
        """
        :return:
        [{
            'cls': ..,
            'name': ..,
            'group_name': ..,
            'module': ..,
            'doc': ..,
            'fields': ..,
            'methods': ..,
        }]
        """

        from django.contrib.admindocs.views import get_readable_field_data_type
        from django.contrib.admindocs.views import get_return_data_type
        from django.utils.encoding import smart_str
        from django.utils.safestring import mark_safe

        MODEL_METHODS_EXCLUDE = ('_', 'add_', 'delete', 'save', 'set_')
        _ = lambda x: x

        def parse_model_rst(text, default_reference_context, thing_being_parsed=None):
            """
            Convert the string from reST to an XHTML fragment.
            """
            overrides = {
                'doctitle_xform': True,
                'inital_header_level': 3,
                "default_reference_context": default_reference_context,
                "link_base": '/_aadoc',
                }
            if thing_being_parsed:
                thing_being_parsed = smart_str("<%s>" % thing_being_parsed)
            parts = docutils.core.publish_parts(text, source_path=thing_being_parsed,
                                                destination_path=None, writer_name='html',
                                                settings_overrides=overrides)
            return mark_safe(parts['fragment'])

        def get_fields(model):
            opts = model._meta

            # Gather fields/field descriptions.
            fields = []
            for field in opts.fields:
                # ForeignKey is a special case since the field will actually be a
                # descriptor that returns the other object
                if isinstance(field, models.ForeignKey):
                    data_type = field.rel.to.__name__
                    app_label = field.rel.to._meta.app_label
                    verbose = parse_model_rst((_("the related `%(app_label)s.%(data_type)s` object") %
                                               {'app_label': app_label, 'data_type': data_type}),
                                              'xraymodel', _('model:') + data_type)
                else:
                    data_type = get_readable_field_data_type(field)
                    verbose = field.verbose_name

                help_text = field.help_text
                if help_text and '`' in help_text:
                    try:
                        help_text = parse_model_rst(help_text, 'xraymodel', _('model:') + opts.model_name)
                    except:
                        pass

                fields.append({
                    'name': field.name,
                    'group_name': 'self',
                    'data_type': data_type,
                    'verbose': verbose,
                    'help_text': help_text,
                    })

            # Gather many-to-many fields.
            for field in opts.many_to_many:
                data_type = field.rel.to.__name__
                app_label = field.rel.to._meta.app_label
                verbose = _("related `%(app_label)s.%(object_name)s` objects") % {
                    'app_label': app_label, 'object_name': data_type}
                fields.append({
                    'name': "%s.all" % field.name,
                    'group_name': 'm2m',
                    "data_type": 'List',
                    'verbose': parse_model_rst(_("all %s") % verbose, 'xraymodel', _('model:') + opts.model_name),
                    })
                fields.append({
                    'name': "%s.count" % field.name,
                    'group_name': 'm2m',
                    'data_type': 'Integer',
                    'verbose': parse_model_rst(_("number of %s") % verbose, 'xraymodel', _('model:') + opts.model_name),
                    })

            # Gather related objects
            # (v1.4) rels = opts.get_all_related_objects() + opts.get_all_related_many_to_many_objects()
            rels = opts.related_objects
            for rel in rels:
                # (v1.4)_rel_mod_meta = rel.opts
                _rel_mod_meta = rel.related_model._meta
                verbose = _("related `%(app_label)s.%(object_name)s` objects") % {
                    'app_label': _rel_mod_meta.app_label,
                    'object_name': _rel_mod_meta.object_name
                }
                accessor = rel.get_accessor_name()
                fields.append({
                    'name': "%s.all" % accessor,
                    'group_name': 'related',
                    'data_type': 'List',
                    'verbose': parse_model_rst(
                        _("all %s") % verbose,
                        'xraymodel',
                        _('model:') + opts.model_name
                    ),
                })
                fields.append({
                    'name': "%s.count" % accessor,
                    'group_name': 'related',
                    'data_type': 'Integer',
                    'verbose': parse_model_rst(_("number of %s") % verbose, 'xraymodel', _('model:') + opts.model_name),
                })

            return fields

        def get_model(cls):
            return {
                'cls': cls,
                'meta': cls._meta,
                'name': cls.__name__,
                'db_table': cls._meta.db_table,
                'using_db': router.db_for_read(cls),
                'group_name': cls._meta.app_label,
                'module': cls.__module__,
                'doc': pydoc.getdoc(cls),
                'fields': get_fields(cls),
                'methods': sorted(get_cls_methods(cls), key=operator.itemgetter('flag', 'name'), reverse=True),
                }

        def _get_methods(model):
            # Gather model methods.
            methods = []

            for func_name, func in model.__dict__.items():
                if (inspect.isfunction(func) and len(inspect.getargspec(func)[0]) == 1):
                    try:
                        for exclude in MODEL_METHODS_EXCLUDE:
                            if func_name.startswith(exclude):
                                raise StopIteration
                    except StopIteration:
                        continue
                    verbose = func.__doc__
                    # verbose = parse_model_rst(utils.trim_docstring(verbose), 'xraymodel',
                    #                           _('model:') + opts.model_name)
                    methods.append({
                        'name': func_name,
                        'data_type': get_return_data_type(func_name),
                        'verbose': verbose,
                        })

            return methods

        cls._register_rs_role()
        model_list = map(get_model, models.get_models())

        return model_list


class ViewsDoc(DocBase):
    name = 'views'
    page_routings = (
        (r'^$', 'index'),
        (r'^(?P<full_name>[^/]+)/$', 'detail'),
    )

    def _get_template_name(self):
        return 'xray/views/index.html'

    def get_index(self, req, *args, **kwargs):
        ctx = {}
        ctx['views'] = sorted(self._get_all_views(), key=operator.itemgetter('url'))

        return self.render_with_ctx(ctx)

    def get_detail(self, req, full_name, *arg, **kwargs):
        ctx = {
            'is_detail': True,
        }
        full_name_tuple = tuple(full_name.rsplit('.', 1))
        getter = operator.itemgetter('module', 'name')
        ctx['views'] = sorted(
            filter(
                lambda x: getter(x) == full_name_tuple,
                self._get_all_views()
            ),
            key=operator.itemgetter('url')
        )

        ctx['this_view'] = {
            'module': full_name_tuple[0],
            'name': full_name_tuple[1],
        }

        return self.render_with_ctx(ctx)

    @classmethod
    def _get_all_views(cls):
        """
        :return:
        [{
            'url': ..,
            'url_mod': ..,
            'name': ..,
            'module': ..,
            'full_name': ..,
            'doc': ..,
        }]
        """

        settings_modules = [settings]

        view_list = []
        for settings_mod in settings_modules:
            urlconf = import_module(settings_mod.ROOT_URLCONF)
            view_functions = cls.extract_views_from_urlpatterns(urlconf.urlpatterns, mod=urlconf.__name__)
            for (func, regex, url_mod) in view_functions:
                mod, func_name = func.__module__, getattr(func, '__name__', func.__class__.__name__)
                view_list.append({
                    'name': func_name,
                    'module': mod,
                    'full_name': '{}.{}'.format(mod, func_name),
                    'raw_url': regex,
                    'url': simplify_regex(regex),
                    'url_mod': url_mod,
                    })

        return view_list

    @classmethod
    def extract_views_from_urlpatterns(cls, urlpatterns, base='', mod=None):
        """
        Return a list of views from a list of urlpatterns.

        Each object in the returned list is a two-tuple: (view_func, regex)
        """
        views = []
        for p in urlpatterns:
            if hasattr(p, 'url_patterns'):
                try:
                    sub_patterns = p.url_patterns
                except ImportError:
                    continue
                url_mod = None
                if inspect.ismodule(p):
                    url_mod = p.__name__
                elif hasattr(p, 'urlconf_module'):
                    _x = p.urlconf_module
                    if inspect.ismodule(_x):
                        url_mod = _x.__name__
                    else:
                        url_mod = 'a {} in {}'.format(type(_x), mod)
                else:
                    url_mod = p
                views.extend(
                    cls.extract_views_from_urlpatterns(sub_patterns, base=base + cls.fix_pattern(p.regex.pattern, base), mod=url_mod)
                )
            elif hasattr(p, 'callback'):
                try:
                    views.append((p.callback, base + cls.fix_pattern(p.regex.pattern, base), mod))
                except ViewDoesNotExist:
                    continue
            else:
                raise TypeError("%s does not appear to be a urlpattern object" % p)
        return views

    @staticmethod
    def fix_pattern(pat, base):
        if not base:
            return pat
        return pat.lstrip('^')


class PyDoc(DocBase):
    name = 'pydoc'
    page_routings = (
        (r'^$', 'index'),
        (r'^(?P<path>.*)$', 'module'),
    )

    def _get_template_name(self):
        return 'xray/pydoc/index.html'

    def get_module(self, request, path, *args, **kwargs):
        join = pydoc.join

        if path[-5:] == '.html':
            path = path[:-5]
        if path[:1] == '/':
            path = path[1:]

        ctx = {}

        try:
            obj = pydoc.locate(path)
        except pydoc.ErrorDuringImport, value:
            return self.render_with_ctx(ctx, title=path, contents=my_html.escape(str(value)))

        if obj:
            return self.render_with_ctx(ctx, title=pydoc.describe(obj),
                                        contents=my_html.document(obj, path))
        else:
            return self.render_with_ctx(ctx, title=path,
                                        contents='no Python documentation found for %s' % repr(path))

    def get_index(self, request, *args, **kwargs):
        join = pydoc.join

        ctx = {}
        ctx['title'] = 'Python: Index of Modules'

        def bltinlink(name):
            return '<a href="%s.html">%s</a>' % (name, name)

        names = filter(lambda x: x != '__main__',
                       sys.builtin_module_names)

        contents = my_html.multicolumn(names, bltinlink)
        indices = ['<p>' + my_html.bigsection(
            'Built-in Modules', '#ffffff', '#ee77aa', contents)]

        paths = map(os.path.normpath, sys.path)
        paths = map(os.path.realpath, paths)
        paths = reduce(lambda lst, it: (lst if it in lst else (lst + [it])), paths, [])
        seen = {}
        for dir in paths:
            indices.append(my_html.index(dir, seen))

        contents = join(indices) + '''<p align=right>
<font color="#909090" face="helvetica, arial"><strong>
pydoc</strong> by Ka-Ping Yee &lt;ping@lfw.org&gt;</font>'''

        ctx['contents'] = contents

        return self.render_with_ctx(ctx)


named_group_matcher = re.compile(r'\(\?P(<\w+>).+?\)')
non_named_group_matcher = re.compile(r'\(.*?\)')


def simplify_regex(pattern):
    """
    Clean up urlpattern regexes into something somewhat readable by Mere Humans:
    turns something like "^(?P<sport_slug>\w+)/athletes/(?P<athlete_slug>\w+)/$"
    into "<sport_slug>/athletes/<athlete_slug>/"
    """
    # handle named groups first
    pattern = named_group_matcher.sub(lambda m: m.group(1), pattern)

    # handle non-named groups
    pattern = non_named_group_matcher.sub("<var>", pattern)

    # clean up any outstanding regex-y characters.
    pattern = pattern.replace('^', '').replace('$', '').replace('?', '').replace('//', '/').replace('\\', '')
    if not pattern.startswith('/'):
        pattern = '/' + pattern
    return pattern
