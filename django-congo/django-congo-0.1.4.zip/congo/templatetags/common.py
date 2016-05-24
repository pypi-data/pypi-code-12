# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.templatetags import Library
from congo.utils.classes import Message, BlankImage
from decimal import Decimal
from django.contrib.messages.storage.base import Message as DjangoMessage
from django.core.cache import caches
from django.template.base import TemplateSyntaxError, Node
from django.template.defaultfilters import iriencode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from random import random

register = Library()

@register.filter
def form_iriencode(url):
    return iriencode(url).replace("%20", "+")

@register.filter(is_safe = True)
def or_blank(value, use_html = True):
    if value:
        return value
    else:
        text = _("(Blank)")
        html = u"""<span class="text-muted">%s</span>""" % text
        blank = html if bool(use_html) else text
        return mark_safe(blank)

@register.filter
def if_empty(value, arg = ""):
    return value or arg

@register.smart_tag
def smart_tag_test(*args, **kwargs):
    result = ""
    if not args and not kwargs:
        result += "<h4>No args and kwargs</h4><p>...no args, no kwargs :(</p>"
    if args:
        result += "<h4>Args</h4>"
        result += "<ul>"
        for a in args:
            result += "<li>%s</li>" % a
        result += "</ul>"
    if kwargs:
        result += "<h4>Kwargs</h4>"
        result += "<ul>"
        for k, v in kwargs.items():
            result += "<li>%s: %s</li>" % (k, v)
        result += "</ul>"
    return result

@register.smart_tag(takes_context = True)
def smart_tag_context_test(context, *args, **kwargs):
    result = "<h4>User: %s</h4>" % context['request'].user
    if not args and not kwargs:
        result += "<h4>No args and kwargs</h4><p>...no args, no kwargs :(</p>"
    if args:
        result += "<h4>Args</h4>"
        result += "<ul>"
        for a in args:
            result += "<li>%s</li>" % a
        result += "</ul>"
    if kwargs:
        result += "<h4>Kwargs</h4>"
        result += "<ul>"
        for k, v in kwargs.items():
            result += "<li>%s: %s</li>" % (k, v)
        result += "</ul>"
    return result

# Messages

@register.smart_tag
def message(msg, **kwargs):
    # dismiss (bool, False)
    # close (bool, False)

    if not msg:
        return ""
    elif isinstance(msg, Message) or isinstance(msg, DjangoMessage):
        obj = msg
    else:
        level = kwargs.get('level', None)
        if level not in Message.DEFAULT_TAGS.values():
            level = 'info'
        obj = getattr(Message, level)(msg)
    return Message.render(obj, **kwargs)

@register.tag
def blockmessage(parser, token):
    try:
        tag_name, level = token.contents.split(None, 1)
    except ValueError:
        level = "info"
    node_list = parser.parse(('endblockmessage',))
    parser.delete_first_token()
    return BlockMessageNode(node_list, level[1:-1])

class BlockMessageNode(Node):
    def __init__(self, node_list, level):
        self.node_list = node_list
        self.level = level

    def render(self, context):
        level = self.level
        if level not in Message.DEFAULT_TAGS.values():
            level = 'info'
        obj = getattr(Message, level)(self.node_list.render(context))
        return Message.render(obj)

# # ecape
#
# @register.tag('escape')
# def do_escape(parser, token):
#    """
#    {% escape %}
#        <div>Some HTML here...</div>
#    {% endescape %}
#    """
#    node_list = parser.parse(('endescape',))
#    parser.delete_first_token()
#    return EscapeNode(node_list)
#
# class EscapeNode(Node):
#    def __init__(self, node_list):
#        self.node_list = node_list
#
#    def render(self, context):
#        return escape(self.node_list.render(context))

# # var & blockvar
#
@register.smart_tag
def var(obj):
    return obj

@register.tag
def blockvar(parser, token):
    # https://djangosnippets.org/snippets/545/
    try:
        tag_name, var_name = token.contents.split(None, 1)
    except ValueError:
        raise TemplateSyntaxError("'var' node requires a variable name.")
    node_list = parser.parse(('endblockvar',))
    parser.delete_first_token()
    return VarNode(node_list, var_name)

class VarNode(Node):
    def __init__(self, node_list, var_name):
        self.node_list = node_list
        self.var_name = var_name

    def render(self, context):
        output = self.node_list.render(context)
        context[self.var_name] = output
        return ""

# cache

@register.tag('cache')
def do_cache(parser, token):
    """
    {% cache "cache_key" [expire_time] %}
        .. some expensive processing ..
    {% endcache %}
    """

    node_list = parser.parse(('endcache',))
    parser.delete_first_token()
    tokens = token.split_contents()

    if len(tokens) == 2:
        cache_key = tokens[1]
        expire_time = 0
    elif len(tokens) == 3:
        cache_key, expire_time = tokens[1:]
    else:
        raise TemplateSyntaxError("'cache' tag requires 1 or 2 arguments.")

    return CacheNode(node_list, cache_key[1:-1], expire_time)

class CacheNode(Node):
    def __init__(self, node_list, cache_key, expire_time):
        self.node_list = node_list
        self.cache_key = cache_key
        self.expire_time = expire_time

    def render(self, context):
        try:
            expire_time = int(self.expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError('"cache" tag got a non-integer timeout value: %r' % self.expire_time)

        cache_backend = settings.CONGO_TEMPLATE_CACHE_BACKEND
        cache = caches[cache_backend]
        version = 'template'
        value = cache.get(self.cache_key, version = version)
        if value is None:
            value = self.node_list.render(context)
            if not expire_time:
                # jeśli nie podano czasu, ustawiamy cache na domyślny -10% / +20%
                expire_time = settings.CACHES[cache_backend].get('TIMEOUT', 0)
                expire_time = int(expire_time * (.9 + random() * .3))
            if expire_time:
                cache.set(self.cache_key, value, expire_time, version = version)
            else:
                cache.set(self.cache_key, value, version = version)
        return value

# gallery

def _photo_url(photo, **kwargs):
    # width (int)
    try:
        width = int(kwargs.get('width'))
    except (ValueError, TypeError):
        width = None

    # height (int)
    try:
        height = int(kwargs.get('height'))
    except (ValueError, TypeError):
        height = None

    # size (int)
    try:
        width = int(kwargs.get('size'))
        height = width
    except (ValueError, TypeError):
        pass

    # crop (bool)
    crop = bool(kwargs.get('crop'))

    html = None
    if photo and getattr(photo, 'image'):
        html = photo.image.get_url(width, height, crop)
    if not html:
        html = BlankImage().get_url(width, height)
    return mark_safe(html)

@register.smart_tag
def blank_photo_url(**kwargs):
    return _photo_url(None, **kwargs)

def _render_photo(photo, **kwargs):
    # width (int)
    try:
        width = int(kwargs.get('width'))
    except (ValueError, TypeError):
        width = None

    # height (int)
    try:
        height = int(kwargs.get('height'))
    except (ValueError, TypeError):
        height = None

    # size (int)
    try:
        width = int(kwargs.get('size'))
        height = width
    except (ValueError, TypeError):
        pass

    html = None
    if photo and getattr(photo, 'image'):
        html = photo.image.render(width, height, **kwargs)
    if not html:
        html = BlankImage().render(width, height, **kwargs)
    return mark_safe(html)

def _photos(photo_list, **kwargs):
    # title (string)
    title = kwargs.get('title', '')

    # label (string)
    label = kwargs.get('note', '')

    # add_url (bool)
    add_url = bool(kwargs.get('add_url', False))

    # add_blank (bool)
    add_blank = bool(kwargs.get('add_blank', True))

    # as_gallery (bool)
    as_gallery = bool(kwargs.get('as_gallery', None))

    def render(photo):
        if photo:
            _title = title or photo.title or ""
            image_url = ""
            
            if label:
                image_label = """<span class="note">%s</span>""" % label
            else:
                image_label = ""
            
            if add_url:
                image_url = photo.image.get_url()

            if image_url:
                image_html = _render_photo(photo, **kwargs)
                return """<div class="thumbnail-wrapper"><a href="%s" title="%s" class="colorbox">%s</a>%s%s</div>""" % (image_url, _title, image_html, image_label)
            else:
                kwargs['alt_text'] = _title
                image_html = _render_photo(photo, **kwargs)
                return """<div class="thumbnail-wrapper">%s%s</div>""" % (image_html, image_label)
        else:
            kwargs['alt_text'] = title
            image_html = _render_photo(photo, **kwargs)
            return """<div class="thumbnail-wrapper">%s</div>""" % (image_html)

    result = ""
    if as_gallery or len(photo_list) > 1:
        result = """<div class="thumbnail-gallery">%s</div>""" % ''.join([render(photo) for photo in photo_list])
    elif len(photo_list) == 1:
        result = render(photo_list[0])
    elif add_blank:
        # if no photos add blank image
        result = render(None)
    return result

@register.smart_tag
def blank_photo(**kwargs):
    return _photos([], **kwargs)

# google maps

@register.smart_tag
def google_maps(mode, **kwargs):
    # https://console.developers.google.com/project/notional-grove-89813/apiui/credential
    key = settings.CONGO_GOOGLE_BROWSER_API_KEY

    if mode == "street_view":
        # https://www.google.pl/maps/@52.2021098,20.5612702,3a,90y,103.45h,85.34t/data=!3m7!1e1!3m5!1sgfByKVyrwy0AAAQo8YZlqQ!2e0!3e2!7i13312!8i6656!6m1!1e1
        # location=52.2021098,20.5612702

        location = kwargs.get('location', '52.200891,20.560264')
        # kierunek w płaszyźnie poziomej: +/- 180
        heading = kwargs.get('heading', 60)
        # odchylenie od poziomu: +/- 90
        pitch = kwargs.get('pitch', 5)
        # zumm: 15 - 90
        fov = kwargs.get('fov', 65)
        return "https://www.google.com/maps/embed/v1/streetview?key=%s&location=%s&heading=%s&pitch=%s&fov=%s" % (key, location, heading, pitch, fov)
    elif mode == "street_view_img":
        location = kwargs.get('location', '52.200891,20.560264')
        heading = kwargs.get('heading', 60)
        pitch = kwargs.get('pitch', 5)
        scale = kwargs.get('scale', 2)
        # max size: 640x640
        size = kwargs.get('size', '640x640')
        return "https://maps.googleapis.com/maps/api/streetview?key=%s&location=%s&heading=%s&pitch=%s&scale=%s&size=%s" % (key, location, heading, pitch, scale, size)
    elif mode == "directions":
        origin = kwargs.get('origin', 'Warszawa, Polska')
        destination = kwargs.get('destination', 'Faktor, Piorunów 13, 05-870 Błonie, Polska')
        avoid = kwargs.get('avoid', 'tolls')
        return "https://www.google.com/maps/embed/v1/directions?key=%s&origin=%s&destination=%s&avoid=%s" % (key, form_iriencode(origin), form_iriencode(destination), form_iriencode(avoid))
    elif mode == "place":
        q = kwargs.get('q', u'Faktor, Piorunów 13, 05-870 Błonie, Polska')
        zoom = kwargs.get('zoom', '10')
        return "https://www.google.com/maps/embed/v1/place?key=%s&q=%s&zoom=%s" % (key, form_iriencode(q), zoom)
    elif mode == "place_img":
        center = kwargs.get('center', u'52.200891,20.560264')
        # max size: 640x640
        size = kwargs.get('size', '640x640')
        zoom = kwargs.get('zoom', '10')
        markers = kwargs.get('markers', 'color:red%7C52.200891,20.560264')
        return "http://maps.googleapis.com/maps/api/staticmap?key=%s&center=%s&zoom=%s&markers=%s&size=%s" % (key, form_iriencode(center), zoom, markers, size)
    elif mode == "external":
        location = kwargs.get('location', '52.200891,20.560264')
        zoom = kwargs.get('zoom', '10')
        place_id = kwargs.get('place_id', '3945958479054158299')
        return "https://maps.google.com/maps?ll=%s&z=%s&cid=%s" % (location, zoom, place_id)
    elif mode == "external-directions":
        origin = kwargs.get('origin', 'Warsaw+Poland')
        destination = kwargs.get('destination', 'Faktor,+Piorun%C3%B3w+13,+05-870+B%C5%82onie,+Polska')
        return "https://www.google.com/maps/dir/%s/%s/" % (origin, destination)
    return ""
