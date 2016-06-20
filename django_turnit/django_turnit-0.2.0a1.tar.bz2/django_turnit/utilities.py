# -*- coding: utf-8 -*-
"""
Utilities for :mod:`django_turnit` application

:creationdate: 07/03/16 09:27
:moduleauthor: François GUÉRIN <frague59@gmail.com>
:modulename: templatetags.turnit_tags

"""
from __future__ import absolute_import

import hashlib
import base64
import logging
import mimetypes
import subprocess

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.apps import apps

logger = logging.getLogger('django_turnit.utilities')


# noinspection PyProtectedMember
def get_id_from_field_file(file_field):
    """
    Extracts meta data from field

    :param file_field:
    :return: field_file name
    """
    return file_field.name


# noinspection PyProtectedMember
def get_file_fields_for_app(app_label, output=None):
    """
    Gets the PDF files in a django application.
    This function search for file fields in the database tables and finds the PDF files.

    :param app_label: Application label
    :param output: if set, the list is filled with tuples, else a brand new list is created (default: None)
    :returns: List of tuples (<FileField instance>, <field identifier>)
    """
    if not output:
        output = []
    app_class = apps.get_app(app_label)
    app_models = apps.get_models(app_class)
    settings.DEBUG and logger.debug(u'get_file_fields_for_app(%s) app_models = %s', app_label, app_models)
    for model_class in app_models:
        try:
            output = get_file_fields_for_model(model_class, output=output)
        except AbstractModelException:
            continue
    # settings.DEBUG and logger.debug(u'get_file_fields_for_app() output = %s', output)
    return output


def cmd_exists(cmd):
    """
    Checks if a file exists and is an executable

    :param cmd: command
    :returns: `True` if command exists
    """
    return subprocess.call("type " + cmd, shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


# noinspection PyProtectedMember
def get_file_fields_for_model(model_class, output=None):
    """
    Gets the PDF files in a django application model.
    This function search for file fields in the database **table** and finds the PDF files.

    :param model_class: Model class
    :param output: if set, the list is filled with tuples, else a brand new list is created (default: None)
    :returns: List of tuples (<FileField instance>, <field identifier>)
    """
    if not output:
        output = []
    if model_class._meta.abstract:
        raise AbstractModelException('Model should not be an `abstract` one')
    # Gets the model field names list
    field_names = model_class._meta.get_all_field_names()
    candidate_fields = {}
    for field_name in field_names:
        field_class = model_class._meta.get_field_by_name(field_name)[0]
        if (issubclass(field_class.__class__, models.FileField) and
                not issubclass(field_class.__class__, models.ImageField)):
            candidate_fields.update({field_name: field_class})
    if len(candidate_fields) == 0:
        return output
    settings.DEBUG and logger.debug(u'get_file_fields_for_model(%s) candidate_fields = %s', model_class,
                                    candidate_fields)
    # Gets values from table
    for instance in model_class.objects.all():
        output = get_file_fields_for_model_instance(instance, candidate_fields, output=output)
    # settings.DEBUG and logger.debug(u'get_file_fields_for_model() output = %s', output)
    return output


# noinspection PyProtectedMember
def get_file_fields_for_model_instance(model_instance, candidate_fields, output=None):
    """
    Gets the PDF files in a django application model.
    This function search for file fields in the database **table** and finds the PDF files.

    :param model_instance: Model instance (row)
    :param candidate_fields: list of fields which could contain a PDF file
    :param output: if set, the list is filled with tuples, else a brand new list is created (default: None)
    :returns: List of tuples (<FileField instance>, <field identifier>)
    """
    if not output:
        output = []

    for field_name in candidate_fields:
        if field_name != 'pk':
            identifier = ('%(app_label)s.%(model_name)s.%(pk)s.%(field_name)s' %
                          {'app_label': type(model_instance)._meta.app_label,
                           'model_name': type(model_instance)._meta.model_name,
                           'pk': model_instance.pk,
                           'field_name': field_name})
            settings.DEBUG and logger.debug(u'get_file_fields_for_model_instance(%s) identifier = %s', model_instance,
                                            identifier)
            try:
                file_field = get_file_field_from_id(identifier, strict=True)
            except FileTypeNotSupported:
                settings.DEBUG and logger.warning(u'get_file_fields_for_model_instance(%s) file type not supported.',
                                                  model_instance)
            else:
                output.extend(file_field)
    # settings.DEBUG and logger.debug(u'get_file_fields_for_model_instance(%s) output = %s', model_instance, output)
    return output


def get_file_field_from_id(field_identifier, strict=True):
    """
    Parses the related field value and returns the field file

    :param field_identifier: field itemdifier
    :param strict: if `True`, identifier is complete and **One-and-only-One** file_field  will be returned
    :returns: if `strict` is True, a file field, else a list on file_fields, depending of the `field_identifier`
    """
    splited_identifier = field_identifier.split('.')
    output = []
    if strict:
        if len(splited_identifier) != 4:
            raise ValueError('get_file_field_from_id() itentifier MUST have 4 components, %d found : %s' %
                             (len(splited_identifier), field_identifier))

    app_label = safe_list_get(splited_identifier, 0)
    model_name = safe_list_get(splited_identifier, 1)
    pk = safe_list_get(splited_identifier, 2)
    field_name = safe_list_get(splited_identifier, 3)

    if app_label and not model_name:
        settings.DEBUG and logger.info("Will search for file fields in the whole `%s` application" % app_label)
        return get_file_fields_for_app(app_label=app_label, output=output)

    # Gets the model class
    model_class = apps.get_model(app_label, model_name)

    # No pk provided
    if model_class and not pk:
        return get_file_fields_for_model(model_class=model_class, output=output)

    # Gets the row instance
    try:
        model_instance = model_class.objects.get(pk=pk)
    except ObjectDoesNotExist:
        logger.error(u'get_file_field_from_id() Unable to get related object for %s.',
                     field_identifier)
        raise

    if model_instance and not field_name:
        return get_file_fields_for_model_instance(model_instance=model_instance)

    # Gets the field_file
    if not hasattr(model_instance, field_name):
        msg = unicode('The model model_instance <%(model_instance)s> does not have a `%(field_name)s` field.' %
                      {'model_instance': model_instance, 'field_name': field_name}, errors='replace')
        logger.error(u'get_file_field_from_id() %s', msg)
        raise AttributeError(msg)

    field_file = getattr(model_instance, field_name)
    file_type, encoding = mimetypes.guess_type(field_file.url)
    logger.debug(u'get_file_field_from_id() field_type = %s for %s', file_type, field_file)
    if file_type not in settings.TURNIT_INPUT_SUPPORTED_FILE_TYPES:
        raise FileTypeNotSupported('`%s` file type is not supported by django_turnit application.')

    return [(field_file, field_identifier), ]


def get_file_hash(input_file, hash_class=hashlib.sha256, buffer_size=65536):
    """
    Gets the Hash signature for a given file

    :param input_file: File that needs to be hashed
    :param hash_class: Hash function (default: hashlib.sha256)
    :param buffer_size: buffer size
    :returns: file hash
    """
    with open(input_file, 'rb') as ifile:
        hash_str = hash_class(ifile.read()).digest()
        b64_encoded = base64.b64encode(hash_str)
        settings.DEBUG and logger.debug('get_file_hash() b64_encoded = %s', b64_encoded)
        return b64_encoded


def safe_list_get(l, idx, default=None):
    """
    Gets safely a value from a list

    :param l: list
    :param idx: index
    :param default: default returned value if item is not found (default: None)
    :returns: item at index `idx`, else the `default` value
    """
    try:
        return l[idx]
    except IndexError:
        return default


class AbstractModelException(Exception):
    """
    Exception raised when the browsed :class:`django:django.db.models.Model` is tagged as `astract`
    """
    pass


class FileTypeNotSupported(Exception):
    """
    Exception raised when the file contained in :class:`django:django.db.models.FileField` is not reported to have a
    supported file type (MIME)
    """
    pass


