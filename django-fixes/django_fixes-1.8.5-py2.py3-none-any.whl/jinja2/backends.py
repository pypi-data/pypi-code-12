from __future__ import absolute_import

import sys
import os

from django.conf import settings

from django.template import TemplateDoesNotExist,TemplateSyntaxError
from django.template.backends.jinja2 import Jinja2 as DjangoJinja2Backend
from django.template.backends.utils import csrf_input_lazy,csrf_token_lazy
from django.template.context import _builtin_context_processors
from django.template.utils import get_app_template_dirs

from django.utils import six
from django.utils.functional import cached_property
from django.utils.module_loading import import_string

import jinja2
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import BaseLoader as Jinja2BaseLoader


class Jinja2Backend(DjangoJinja2Backend):
    """
    A Django template backend that adds support for context processors to Django's current Jinja2 backend.
    """
    app_dirname='templates'
    _default_extensions=[
        'jinja2.ext.do',
        'jinja2.ext.loopcontrols',
        'jinja2.ext.with_',
        'jinja2.ext.i18n',
        'jinja2.ext.autoescape',
        ]


    def __init__(self,params):
        params=params.copy()
        # OPTIONS are passed as kwargs to the Environment class
        params['OPTIONS']=params.pop('OPTIONS').copy()
        # set our default loader, if not explicitly overridden by the user
        if 'loader' not in params['OPTIONS']:
            from .loaders import Jinja2AppSpecificLoader
            dirs=params['DIRS']
            app_dirs=get_app_template_dirs(self.app_dirname) if bool(params['APP_DIRS']) else ()
            params['OPTIONS']['loader']=Jinja2AppSpecificLoader(dirs,app_dirs,app_dirname=self.app_dirname,only_match_filename_extensions=params['OPTIONS'].get('only_match_filename_extensions',None))
        params['OPTIONS'].setdefault('undefined',jinja2.Undefined)
        params['OPTIONS'].setdefault('extensions',self._default_extensions)
        # pop context_processors because jinja2 doesn't know about them, we run them before handing off to jinja2
        self.context_processors=params['OPTIONS'].pop('context_processors',[])
        # import globals
        gs=params['OPTIONS'].pop('globals',{})
        params['OPTIONS']['globals']={n:import_string(g) for n,g in gs.items()}
        super(self.__class__,self).__init__(params)


    @cached_property
    def context_processor_functions(self):
        context_processors=_builtin_context_processors
        context_processors+=tuple(self.context_processors)
        return tuple(import_string(path) for path in self.context_processors)


    def from_string(self,template_code):
        return Template(self.env.from_string(template_code),self.context_processor_functions)


    def get_template(self,template_name):
        try:
            return Template(self.env.get_template(template_name),self.context_processor_functions)
        except jinja2.TemplateNotFound as exc:
            six.reraise(TemplateDoesNotExist,TemplateDoesNotExist(exc.args),sys.exc_info()[2])
        except jinja2.TemplateSyntaxError as exc:
            six.reraise(TemplateSyntaxError,TemplateSyntaxError(exc.args),sys.exc_info()[2])


class Template(object):
    def __init__(self,template,context_processor_functions):
        self.template=template
        self.context_processor_functions=context_processor_functions

    def render(self,context=None,request=None):
        full_context={}
        if request is not None:
            # populate some basics
            full_context['request']=request
            full_context['csrf_input']=csrf_input_lazy(request)
            full_context['csrf_token']=csrf_token_lazy(request)
            # and run context processors
            for p in self.context_processor_functions:
                full_context.update(p(request))

        # overwrite context processor results with context specific values
        if context is not None: full_context.update(context)
        return self.template.render(full_context)


# provide django template language compatible version of the url tag
def url(name,*args,**kwargs):
    from django.core.urlresolvers import reverse
    return reverse(name,args=args,kwargs=kwargs)


# provide a custom jinja2 environment
def environment(**options):
    from django.contrib.staticfiles.storage import staticfiles_storage

    # globals aren't accepted as a parameter to Environment
    gs=options.pop('globals',{})
    options.pop('only_match_filename_extensions',None)
    env=jinja2.Environment(**options)
    # standard replacements for django template language functions
    env.globals.update({
        'static':staticfiles_storage.url,
        'url':url,
    })
    # and any user specified globals
    env.globals.update(gs)
    return env
