__author__ = 'vinay'
from functools import wraps
import re

from bs4 import BeautifulSoup, Tag
from mistune import markdown

from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.test.client import Client
from django.template import TemplateSyntaxError
from django.utils.decorators import available_attrs
from django.utils.functional import SimpleLazyObject

from .validators import validate_and_get_template, ValidationError


# we are initialising Client as global variable
# so that we need to load the middlewares only once
_dum_client = Client()


@SimpleLazyObject
def dum_request(**request_settings):
    """
    Returns WSGIRequest object that is ready to be passed into a view
    """
    request_handler = _dum_client.handler
    environ = _dum_client._base_environ(**request_settings)
    if environ.get('PATH_INFO', '/') == '/':
        # we are doing this because the catchall url does not catch '/'
        environ.update({'PATH_INFO': '/asd/'})

    request = WSGIRequest(environ)
    if request_handler._request_middleware is None:
        request_handler.load_middleware()

    urlconf = settings.ROOT_URLCONF
    urlresolvers.set_urlconf(urlconf)
    resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
    try:
        response = None
        # Apply request middleware
        for middleware_method in request_handler._request_middleware:
            response = middleware_method(request)
            if response:
                break

        if response is None:
            if hasattr(request, 'urlconf'):
                # Reset url resolver with a custom urlconf.
                urlconf = request.urlconf
                urlresolvers.set_urlconf(urlconf)
                resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)

            resolver_match = resolver.resolve(request.path_info)
            callback, callback_args, callback_kwargs = resolver_match
            request.resolver_match = resolver_match

            # Apply view middleware
            for middleware_method in request_handler._view_middleware:
                response = middleware_method(request, callback, callback_args, callback_kwargs)
                if response:
                    break
    except:
        pass
    finally:
        return request


CMS_ATTRIBUTES = ['data-cms-attr', 'data-cms-content', 'data-cms-include']

attr_re = re.compile(r'^(?:(?:[a-z-]+:[a-z_0-9]+)+(?:\|(?:[a-z-]+:[a-z_0-9]+))*)*$', re.IGNORECASE)
content_re = re.compile(r'^(?:md:)?([a-z_0-9])+$', re.IGNORECASE)
include_html_re = re.compile(r'^(?:(?:[a-z_0-9])+:)?.+$', re.IGNORECASE)
namespace_re = re.compile(r'^(?:[a-z_0-9])+$', re.IGNORECASE)

NAMESPACE_DELIMITER = '-'

# only 'html.parser' doesn't bother adding <html> tag for html components
HTML_PARSER = 'html.parser'


def parse_cms_template(html, dictionary, parent_namespace='', publish=False, request=dum_request):
    """
    Refer to tests for cms syntax

    :param html: Html to be parsed using cms syntax
    :type html: str
    :param dictionary: Dictionary that is to be used to parse the cms attributes in template
    :type dictionary: dict
    :param parent_namespace: Namespace of the html content to be parsed (if any)
    :type parent_namespace: str
    :param publish: This will hide sensitive info while rendering for public usage
    :type publish: bool
    :rtype : str
    """
    soup = BeautifulSoup(html, features=HTML_PARSER)

    for tag in soup.find_all(attrs={'data-cms-include': include_html_re}):
        namespace = get_namespace(tag, parent_namespace=parent_namespace)
        include_value = tag.attrs.pop('data-cms-include')
        if ':' in include_value:
            local_namespace, default_template_name = include_value.split(':', 1)
        else:
            try:
                local_namespace = tag.attrs['data-cms-namespace']
            except KeyError:
                raise TemplateSyntaxError(
                    'value of data-cms-include should be of the form {namespace}:{template path}'
                    'if namespace is not specified then another attribute data-cms-namespace should be defined'
                )
            else:
                if not namespace_re.match(local_namespace):
                    raise TemplateSyntaxError(
                        '"{}" is not a valid value for data-cms-namespace'.format(local_namespace)
                    )
                else:
                    default_template_name = include_value

        namespace += NAMESPACE_DELIMITER + local_namespace if namespace else local_namespace

        template_name = dictionary.get(namespace, default_template_name)

        if template_name.endswith('.html'):
            template_name = template_name[:-5]

        try:
            include_template = validate_and_get_template(template_name)
        except ValidationError:
            include_template = validate_and_get_template(
                default_template_name[:-5] if default_template_name.endswith('.html') else default_template_name
            )

        include_html = include_template.render(request=request)

        tag.attrs['data-cms-namespace'] = local_namespace
        if not publish:
            tag.attrs['data-cms-include'] = template_name

        new_tag = Tag(soup, name=tag.name, attrs=tag.attrs)
        new_tag.insert(0, BeautifulSoup(include_html, features=HTML_PARSER))
        tag.replaceWith(new_tag)

    # soup does not recognize the changes made in above loop unless I do this
    # Also do not move it inside the loop. It will mess up the variable scoping
    soup = BeautifulSoup(soup.encode_contents(), features=HTML_PARSER)

    for tag in soup.find_all(attrs={'data-cms-attr': attr_re}):
        _ns = get_namespace(tag, parent_namespace=parent_namespace)
        attrs = tag['data-cms-attr'].split('|')

        for attr in attrs:
            attr_name, key = attr.split(':', 1)
            key = _ns + NAMESPACE_DELIMITER + key if _ns else key

            if key in dictionary:
                tag[attr_name] = dictionary[key]

    soup = BeautifulSoup(soup.encode_contents(), features=HTML_PARSER)

    for tag in soup.find_all(attrs={'data-cms-content': content_re}):
        _ns = get_namespace(tag, parent_namespace=parent_namespace)
        key = tag['data-cms-content']
        md = False

        if key.startswith('md:'):
            key = key[3:]
            md = True

        key = _ns + NAMESPACE_DELIMITER + key if _ns else key

        if key in dictionary:
            content = dictionary[key]
        else:
            content = tag.encode_contents()
            if not any(_ in content for _ in CMS_ATTRIBUTES):
                continue

        new_tag = Tag(soup, name=tag.name, attrs=tag.attrs)
        if any(_ in content for _ in CMS_ATTRIBUTES):
            content = parse_cms_template(content, dictionary, parent_namespace=key, request=request)

        if md:
            content = markdown(content, False)

        new_tag.insert(0, BeautifulSoup(content, features=HTML_PARSER))
        tag.replace_with(new_tag)

    soup = BeautifulSoup(soup.encode_contents(), features=HTML_PARSER)
    # don't use soup.prettify as it will insert empty spaces inside textarea
    return soup.encode_contents()


def get_namespace(tag, parent_namespace=''):
    ancestor_namespaces = [parent.attrs.get('data-cms-namespace') or parent.attrs.get('data-cms-content')
                           for parent in tag.find_parents(is_namespace_parent)]

    if parent_namespace:
        ancestor_namespaces.append(parent_namespace)

    return NAMESPACE_DELIMITER.join(reversed(ancestor_namespaces))


def is_namespace_parent(tag):
    attrs = tag.attrs
    if namespace_re.match(attrs.get('data-cms-namespace', '')) or content_re.match(attrs.get('data-cms-content', '')):
        return True

    return False


def can_edit_content(user):
    return user.has_perm('cfblog.change_content')


def user_passes_test(test_func=can_edit_content):
    """
    Similar to user_passes_test in django.contrib.auth.decorators.
    Instead of redirecting it just raises PermissionDenied.

    :param test_func: Should take a User object and return a bool
    :type test_func: function
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return _wrapped_view
    return decorator
