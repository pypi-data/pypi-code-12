from __future__ import absolute_import

# TODO: try/catch or put imports in methods, so that this can be imported but only errors if actually used but no django - better to error if imported by code but no django
from django.template import Context,Template
from django.utils.html import escape
from django.utils.safestring import SafeString as S


def prettyFormatValue(value):
    """
    Formats a python datatype appropriately for being displayed to a user.
    """
    if value is None:
        value=S('-')
    elif isinstance(value,bool):
        value=S({True:'Yes',False:'No'}.get(value,'-'))
    elif isinstance(value,datetime) and (value.second>0 or value.minute>0 or value.hour>0):
        value=S(value.strftime('%d/%m/%Y %H:%M:%S'))
    elif isinstance(value,date):
        value=S(value.strftime('%d/%m/%Y'))
    else:
        value=escape(value)
    return value


def formatTemplate(templateString,**kwargs):
    """Formats a template string using Django's template language using keyword args as the context."""
    t=Template(templateString)
    return t.render(Context(kwargs))


def formatFieldProperty(fieldName,formatFn,**kwargs):
    """Returns a property that formats a field as specified."""
    def formatter(self):
        v=getattr(self,fieldName)
        return formatFn(v,**kwargs)
    return property(formatter)
