# -*- coding: utf-8 -*-

################################################################
# xmldirector.bookalope
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

import bookalope
from xmldirector.bookalope.interfaces import IBookalopeSettings


def convert_bookalope(context, source, cover=None, formats=[], title=u'', author=u'', prefix=None, storage_path='result'):
    """ Convert ``source`` using bookalope.net """

    registry = getUtility(IRegistry)
    settings = registry.forInterface(IBookalopeSettings)
    handle = context.get_handle()

    if not settings.bookalope_api_key:
        raise ValueError('Bookalope API key not configured')

    b_client = bookalope.BookalopeClient(beta_host=settings.bookalope_beta)
    b_client.token = settings.bookalope_api_key

    book = b_client.create_book()
    bookflow = book.bookflows[0]

    bookflow.title = title
    bookflow.author = author
    bookflow.save()

    if not formats:
        raise ValueError('You must specify a list of ebook formats')

    available_formats = [fext for format_ in b_client.get_export_formats() for fext in format_.file_exts]
    for format_ in formats:
        if not format_ in available_formats:
            raise ValueError('Unsupported EBook format "{}"'.format(format_))

    with handle.open(source, 'rb') as doc:
        bookflow.set_document('index.docx', doc.read())

    if cover:
        with handle.open(cover, 'rb') as doc:
            bookflow.set_cover_image('cover.jpg', doc.read())

    if not handle.exists(storage_path):
        handle.makedir(storage_path, recursive=True)

    for format_ in formats:
        # Get the Style instance for the default styling.
        styles = b_client.get_styles(format_)
        default_style = next(_ for _ in styles if _.short_name == "default")
        converted_bytes = bookflow.convert(format_, default_style, version="test")

        fname = "{}/{}.{}".format(storage_path, prefix or bookflow.id, format_)
        with handle.open(fname, "wb") as doc_conv:
            doc_conv.write(converted_bytes)

    book.delete()
