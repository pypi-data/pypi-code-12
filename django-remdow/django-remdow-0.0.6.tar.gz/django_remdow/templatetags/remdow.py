# -*- encoding: utf-8 -*-

import hashlib
import imghdr
import os
import sys
from functools import wraps

from bs4 import BeautifulSoup
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.safestring import mark_safe

if sys.version_info > (3, 0):
    from urllib.request import build_opener
else:
    from urllib2 import build_opener

from django import template
from django.conf import settings

register = template.Library()


def get_extensions():
    return ['jpg', 'jpeg', 'png', 'gif']


def _download(file_path, url):
    with open(file_path, 'wb') as fio:
        opener = build_opener()
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1')]
        fio.write(opener.open(url).read())
        fio.flush()

    extension = imghdr.what(file_path)
    if extension in get_extensions():
        old_file_path = file_path
        file_path = "%s.%s" % (file_path, extension)
        os.rename(old_file_path, file_path)
        ext = 'png'
        if ext != extension:
            sym_path = "%s.%s" % (old_file_path, ext)
            if not os.path.exists(sym_path):
                os.symlink(file_path, sym_path)
    return file_path


def get_filename(url):
    if sys.version_info > (3, 0):
        link = str(url).encode('utf-8')
    else:
        link = str(url)
    return hashlib.md5(link).hexdigest()


def get_folder(folder_type='img'):
    folder = os.path.join(settings.STATIC_ROOT, 'remdow/%s' % folder_type)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return folder


def download_link(value, type_link):
    m = get_filename(value)
    file_path = os.path.join(get_folder(type_link), m)

    if not os.path.exists(file_path + '.%s' % 'png'):
        file_path = _download(file_path, value)
        _, file_extension = os.path.splitext(file_path)
        if file_extension:
            if '.' in file_extension:
                file_extension = file_extension[1:]
            result = static('remdow/%s/%s.%s' % (type_link, m, file_extension))
        else:
            result = static('remdow/%s/%s' % (type_link, m))
    else:
        if all([x != m for x in get_extensions()]):
            result = static('remdow/%s/%s.%s' % (type_link, m, 'png'))
        else:
            result = static('remdow/%s/%s' % (type_link, m))
    return result


def _get_soup(value):
    return BeautifulSoup(value, "html.parser")


def _get_img(soup):
    return soup.find_all('img', src=True)


def as_mark_safe(func=None):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        return mark_safe(func(*args, **kwargs))

    return func_wrapper


@register.filter(name='img_local')
@as_mark_safe
def remdow_img_local(value):
    soup = _get_soup(value)
    for link in _get_img(soup):
        link["src"] = download_link(link["src"], 'img')
    return str(soup)


def add_class_image(value, class_name):
    soup = _get_soup(value)
    for link in _get_img(soup):
        link["class"] = link.get('class', []) + [class_name]
    return str(soup)


@register.filter(name='img_responsive')
@as_mark_safe
def remdow_img_responsive(value):
    return add_class_image(value, 'img-responsive')


@register.filter(name='img_center')
@as_mark_safe
def remdow_img_center(value):
    return add_class_image(value, 'center-block')


@register.simple_tag(name='lazy_script_include')
@as_mark_safe
def remdow_lazy_script_include():
    return '<script src="//cdn.jsdelivr.net/layzr.js/2.0.2/layzr.min.js">var layzr = new Layzr();</script>'


@register.filter(name='img_lazy')
@as_mark_safe
def remdow_lazy_img(value):
    soup = _get_soup(value)
    for link in _get_img(soup):
        link["data-normal"] = str(link["src"])
        link["srcset"] = str(link["src"])
        del link["src"]
    return str(soup)
