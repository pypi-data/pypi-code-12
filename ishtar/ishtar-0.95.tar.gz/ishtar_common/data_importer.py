#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# See the file COPYING for details.

import copy
import csv
import datetime
import io
import logging
import re
import sys
import zipfile

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.db import IntegrityError, DatabaseError, transaction
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

NEW_LINE_BREAK = '#####@@@#####'

RE_FILTER_CEDEX = re.compile("(.*) *(?: *CEDEX|cedex|Cedex|Cédex|cédex *\d*)")


class ImportFormater(object):
    def __init__(self, field_name, formater=None, required=True, through=None,
                 through_key=None, through_dict=None,
                 through_unicity_keys=None, duplicate_fields=[], regexp=None,
                 regexp_formater_args=[], force_value=None,
                 post_processing=False, concat=False, concat_str=False,
                 comment="", force_new=None):
        self.field_name = field_name
        self.formater = formater
        self.required = required
        self.through = through
        self.through_key = through_key
        self.through_dict = through_dict
        self.through_unicity_keys = through_unicity_keys
        self.duplicate_fields = duplicate_fields
        self.regexp = regexp
        self.regexp_formater_args = regexp_formater_args
        # write this value even if a value exists
        self.force_value = force_value
        # post process after import
        self.post_processing = post_processing
        # concatenate with existing value
        self.concat = concat
        self.concat_str = concat_str
        self.comment = comment
        self.force_new = force_new

    def reinit_db_target(self, db_target, nb=0):
        if not self.formater:
            return
        if type(db_target) in (list, tuple):
            db_target = db_target[nb]
        if type(self.formater) not in (list, tuple):
            self.formater.db_target = db_target
            self.formater.init_db_target()
        else:
            for idx, formater in enumerate(self.formater):
                formater.db_target = db_target
                formater.init_db_target()

    def init_db_target(self):
        pass

    def __unicode__(self):
        return self.field_name

    def report_succes(self, *args):
        return

    def report_error(self, *args):
        return

    def init(self, vals, output=None, choose_default=False,
             import_instance=None):
        try:
            lst = iter(self.formater)
        except TypeError:
            lst = [self.formater]
        for formater in lst:
            if formater:
                formater.check(vals, output, self.comment,
                               choose_default=choose_default,
                               import_instance=import_instance)

    def post_process(self, obj, context, value, owner=None):
        raise NotImplemented()


class ImporterError(Exception):
    STANDARD = 'S'
    HEADER = 'H'

    def __init__(self, message, type='S'):
        self.msg = message
        self.type = type

    def __str__(self):
        return self.msg


class Formater(object):
    def __init__(self, *args, **kwargs):
        self.db_target = kwargs.get('db_target', None)

    def format(self, value):
        return value

    def check(self, values, output=None, comment='', choose_default=False,
              import_instance=None):
        return

    def init_db_target(self):
        pass


class ChoiceChecker(object):
    def report_new(self, comment):
        if not self.new_keys:
            return
        msg = u"For \"%s\" these new associations have been made:\n" % comment
        sys.stderr.write(msg.encode('utf-8'))
        for k in self.new_keys:
            msg = u'"%s";"%s"\n' % (k, self.new_keys[k])
            sys.stderr.write(msg.encode('utf-8'))


class UnicodeFormater(Formater):
    def __init__(self, max_length=None, clean=False, re_filter=None,
                 notnull=False, prefix=u'', db_target=None):
        self.max_length = max_length
        self.db_target = db_target
        self.clean = clean
        self.re_filter = re_filter
        self.notnull = notnull
        self.prefix = prefix

    def format(self, value):
        try:
            if type(value) != unicode:
                value = unicode(value.strip())
            vals = []
            for v in value.split(u'\n'):
                v = v.strip()
                if v:
                    vals.append(v)
            value = u"\n".join(vals)
            if self.re_filter:
                m = self.re_filter.match(value)
                if m:
                    value = u"".join(m.groups())
            if self.clean:
                if value.startswith(","):
                    value = value[1:]
                if value.endswith(","):
                    value = value[:-1]
                value = value.replace(", , ", ", ")
        except UnicodeDecodeError:
            return
        if self.max_length and len(value) > self.max_length:
            raise ValueError(
                _(u"\"%(value)s\" is too long. The max length is %(length)d "
                  u"characters.") % {'value': value,
                                     'length': self.max_length})
        if self.notnull and not value:
            return
        if value:
            value = self.prefix + value
        return value


class BooleanFormater(Formater):
    def format(self, value):
        value = value.strip().upper()
        if value in ('1', 'OUI', 'VRAI', 'YES', 'TRUE'):
            return True
        if value in ('', '0', 'NON', 'FAUX', 'NO', 'FALSE'):
            return False
        raise ValueError(_(u"\"%(value)s\" not equal to yes or no") % {
            'value': value})


class FloatFormater(Formater):
    def format(self, value):
        value = value.strip().replace(',', '.')
        if not value:
            return
        try:
            return float(value)
        except ValueError:
            raise ValueError(_(u"\"%(value)s\" is not a float") % {
                'value': value})


class YearFormater(Formater):
    def format(self, value):
        value = value.strip()
        if not value:
            return
        try:
            value = int(value)
            assert value > 0 and value < (datetime.date.today().year + 30)
        except (ValueError, AssertionError):
            raise ValueError(_(u"\"%(value)s\" is not a valid date") % {
                'value': value})


class YearNoFuturFormater(Formater):
    def format(self, value):
        value = value.strip()
        if not value:
            return
        try:
            value = int(value)
            assert value > 0 and value < (datetime.date.today().year)
        except (ValueError, AssertionError):
            raise ValueError(_(u"\"%(value)s\" is not a valid date") % {
                'value': value})


class IntegerFormater(Formater):
    def format(self, value):
        value = value.strip()
        if not value:
            return
        try:
            return int(value)
        except ValueError:
            raise ValueError(_(u"\"%(value)s\" is not an integer") % {
                'value': value})


class StrChoiceFormater(Formater, ChoiceChecker):
    def __init__(self, choices, strict=False, equiv_dict={}, model=None,
                 cli=False, many_split='', db_target=None):
        self.choices = list(choices)
        self.strict = strict
        self.equiv_dict = copy.deepcopy(equiv_dict)
        self.cli = cli
        self.model = model
        self.db_target = db_target
        self.create = False
        self.missings = set()
        self.new_keys = {}
        self.match_table = {}
        self.many_split = many_split
        for key, value in self.choices:
            value = unicode(value)
            if not self.strict:
                value = slugify(value)
            if value not in self.equiv_dict:
                v = key
                if model and v:
                    v = model.objects.get(pk=v)
                self.equiv_dict[value] = v
        self.init_db_target()

    def init_db_target(self):
        if not self.db_target:
            return
        for target_key in self.db_target.keys.filter(is_set=True).all():
            key = target_key.key
            if not self.strict:
                key = slugify(key)
            if key in self.equiv_dict:
                continue
            v = target_key.value
            if self.model and v and type(v) in (int, unicode):
                try:
                    v = self.model.objects.get(txt_idx=v)
                except:
                    v = self.model.objects.get(pk=v)
            self.equiv_dict[key] = v

    def prepare(self, value):
        return unicode(value).strip()

    def _get_choices(self, comment=''):
        msgstr = comment + u" - "
        msgstr += unicode(_(u"Choice for \"%s\" is not available. "
                            u"Which one is relevant?\n"))
        idx = -1
        for idx, choice in enumerate(self.choices):
            msgstr += u"%d. %s\n" % (idx + 1, choice[1])
        idx += 2
        if self.create:
            msgstr += unicode(_(u"%d. None of the above - create new")) % idx \
                + u"\n"
            idx += 1
        msgstr += unicode(_(u"%d. None of the above - skip")) % idx + u"\n"
        return msgstr, idx

    def check(self, values, output=None, comment='', choose_default=False,
              import_instance=None):
        from ishtar_common.models import TargetKey
        if self.db_target:
            q = {'target': self.db_target,
                 'associated_import': import_instance,
                 'is_set': True
                 }
            for v in self.equiv_dict:
                q['key'] = v
                value = self.equiv_dict[v]
                if hasattr(value, 'pk'):
                    value = value.pk
                q['value'] = value
                with transaction.commit_on_success():
                    try:
                        t, created = TargetKey.objects.get_or_create(**q)
                    except IntegrityError:
                        pass

        if (not output or output == 'silent') and not choose_default:
            return
        if self.many_split:
            new_values = []
            r = re.compile(self.many_split)
            for value in values:
                new_values += r.split(value)
            values = new_values
        for value in values:
            base_value = copy.copy(value)
            value = self.prepare(value)
            if value in self.equiv_dict:
                continue
            if output != 'cli' and not choose_default:
                self.missings.add(value)
                continue
            msgstr, idx = self._get_choices(comment)
            res = None
            if choose_default:
                res = 1
            while res not in range(1, idx + 1):
                msg = msgstr % value
                sys.stdout.write(msg.encode('utf-8'))
                sys.stdout.write("\n>>> ")
                res = raw_input()
                try:
                    res = int(res)
                except ValueError:
                    pass
            res -= 1
            if res < len(self.choices):
                v = self.choices[res][0]
                if self.model and v:
                    v = self.model.objects.get(pk=v)
                self.equiv_dict[value] = v
                self.add_key(v, value)
                self.new_keys[value] = v
            elif self.create and res == len(self.choices):
                self.equiv_dict[value] = self.new(base_value)
                self.choices.append((self.equiv_dict[value].pk,
                                     unicode(self.equiv_dict[value])))
                self.new_keys[value] = unicode(self.equiv_dict[value])
            else:
                self.equiv_dict[value] = None
            if self.equiv_dict[value] and self.db_target:
                from ishtar_common.models import TargetKey
                q = {'target': self.db_target, 'key': value,
                     'associated_import': import_instance,
                     }
                query = TargetKey.objects.filter(**q)
                if query.count():
                    target = query.all()[0]
                    target.value = self.equiv_dict[value]
                    target.is_set = True
                    target.save()
                else:
                    with transaction.commit_on_success():
                        q['value'] = self.equiv_dict[value]
                        q['is_set'] = True
                        try:
                            TargetKey.objects.create(**q)
                        except IntegrityError:
                            pass
        if output == 'db' and self.db_target:
            from ishtar_common.models import TargetKey
            for missing in self.missings:
                q = {'target': self.db_target, 'key': missing,
                     'associated_import': import_instance}
                if TargetKey.objects.filter(**q).count():
                    continue
                with transaction.commit_on_success():
                    try:
                        TargetKey.objects.create(**q)
                    except IntegrityError:
                        pass
        if output == 'cli':
            self.report_new(comment)

    def new(self, value):
        return

    def add_key(self, obj, value):
        return

    def format(self, value):
        origin_value = value
        value = self.prepare(value)
        if not self.strict:
            value = slugify(value)
        if value in self.equiv_dict:
            self.match_table[origin_value] = self.equiv_dict[value] or ''
            return self.equiv_dict[value]


class TypeFormater(StrChoiceFormater):
    def __init__(self, model, cli=False, defaults={}, many_split=False,
                 db_target=None):
        self.create = True
        self.strict = False
        self.model = model
        self.defaults = defaults
        self.many_split = many_split
        self.db_target = db_target
        self.missings = set()
        self.equiv_dict, self.choices = {}, []
        self.match_table = {}
        self.new_keys = {}
        for item in model.objects.all():
            self.choices.append((item.pk, unicode(item)))
            for key in item.get_keys():
                self.equiv_dict[key] = item

    def prepare(self, value):
        return slugify(unicode(value).strip())

    def add_key(self, obj, value):
        obj.add_key(slugify(value), force=True)

    def new(self, value):
        values = copy.copy(self.defaults)
        values['label'] = value
        values['txt_idx'] = slugify(value)
        if 'order' in self.model._meta.get_all_field_names():
            order = 1
            q = self.model.objects.values('order').order_by('-order')
            if q.count():
                order = q.all()[0]['order'] or 1
            values['order'] = order
        return self.model.objects.create(**values)


class DateFormater(Formater):
    def __init__(self, date_formats=["%d/%m/%Y"], db_target=None):
        self.date_formats = date_formats
        if type(date_formats) not in (list, tuple):
            self.date_formats = [self.date_formats]
        self.db_target = db_target

    def format(self, value):
        value = value.strip()
        if not value:
            return
        for date_format in self.date_formats:
            try:
                return datetime.datetime.strptime(value, date_format).date()
            except:
                continue
        raise ValueError(_(u"\"%(value)s\" is not a valid date") % {
            'value': value})


class FileFormater(Formater):
    need_archive = True

    def format(self, value, archive):
        value = value.strip()
        if not value:
            return
        zp = zipfile.ZipFile(archive)
        value = value.strip().replace(u'\\', u'/')
        items = value.replace(u'/', u'_').split(u'.')
        filename = settings.MEDIA_ROOT + 'imported/' + \
            u".".join(items[:-1]) + u'.' + items[-1]
        try:
            with open(filename, 'w') as f:
                with zp.open(value) as z:
                    f.write(z.read())
            f = open(filename, 'r')
            my_file = File(f)
            return my_file
        except KeyError:
            raise ValueError(_(u"\"%(value)s\" is not a valid path for the "
                               u"given archive") % {'value': value})


class StrToBoolean(Formater, ChoiceChecker):
    def __init__(self, choices={}, cli=False, strict=False, db_target=None):
        self.dct = copy.copy(choices)
        self.cli = cli
        self.strict = strict
        self.db_target = db_target
        self.missings = set()
        self.init_db_target()
        self.match_table = {}
        self.new_keys = {}

    def init_db_target(self):
        if not self.db_target:
            return
        for target_key in self.db_target.keys.filter(is_set=True).all():
            key = self.prepare(target_key.key)
            if key in self.dct:
                continue
            v = target_key.format()
            self.dct[key] = v

    def prepare(self, value):
        value = unicode(value).strip()
        if not self.strict:
            value = slugify(value)
        return value

    def check(self, values, output=None, comment='', choose_default=False,
              import_instance=None):
        if (not output or output == 'silent') and not choose_default:
            return
        msgstr = comment + u" - "
        msgstr += unicode(_(
            u"Choice for \"%s\" is not available. "
            u"Which one is relevant?\n"))
        msgstr += u"1. True\n"
        msgstr += u"2. False\n"
        msgstr += u"3. Empty\n"
        for value in values:
            value = self.prepare(value)
            if value in self.dct:
                continue
            if output != 'cli' and not choose_default:
                self.missings.add(value)
                continue
            res = None
            if choose_default:
                res = 1
            while res not in range(1, 4):
                msg = msgstr % value
                sys.stdout.write(msg.encode('utf-8'))
                sys.stdout.write("\n>>> ")
                res = raw_input()
                try:
                    res = int(res)
                except ValueError:
                    pass
            if res == 1:
                self.dct[value] = True
            elif res == 2:
                self.dct[value] = False
            else:
                self.dct[value] = None
            self.new_keys[value] = unicode(self.dct[value])
        if output == 'db' and self.db_target:
            from ishtar_common.models import TargetKey
            for missing in self.missings:
                try:
                    q = {'target': self.db_target, 'key': missing,
                         'associated_import': import_instance}
                    if not TargetKey.objects.filter(**q).count():
                        TargetKey.objects.create(**q)
                except IntegrityError:
                    pass
        if output == 'cli':
            self.report_new(comment)

    def format(self, value):
        origin_value = value
        value = self.prepare(value)
        if value in self.dct:
            val = self.dct[value] and "True" or "False"
            self.match_table[origin_value] = _(val)
            return self.dct[value]

logger = logging.getLogger(__name__)


def get_object_from_path(obj, path):
    for k in path.split('__')[:-1]:
        if not hasattr(obj, k):
            return
        obj = getattr(obj, k)
    return obj


class Importer(object):
    SLUG = ''
    NAME = ''
    DESC = ""
    LINE_FORMAT = []
    OBJECT_CLS = None
    IMPORTED_LINE_FIELD = None
    UNICITY_KEYS = []
    EXTRA_DEFAULTS = {}
    DEFAULTS = {}
    ERRORS = {
        'header_check': _(
            u"The given file is not correct. Check the file "
            u"format. If you use a CSV file: check that column separator "
            u"and encoding are similar to the ones used by the reference "
            u"file."),
        'too_many_cols': _(u"Too many cols (%(user_col)d) when "
                           u"maximum is %(ref_col)d"),
        'no_data': _(u"No data provided"),
        'value_required': _(u"Value is required"),
        'not_enough_cols': _(u"At least %d columns must be filled"),
        'regex_not_match': _(u"The regexp doesn't match.")
    }

    def _create_models(self, force=False):
        from ishtar_common import models
        q = models.ImporterType.objects.filter(slug=self.SLUG)
        if not force and (not self.SLUG or q.count()):
            return
        if force and q.count():
            q.all()[0].delete()
        name = self.NAME if self.NAME else self.SLUG

        model_name = self.OBJECT_CLS.__module__ + '.' + \
            self.OBJECT_CLS.__name__

        unicity_keys = ''
        if self.UNICITY_KEYS:
            unicity_keys = ";".join(self.UNICITY_KEYS)

        importer = models.ImporterType.objects.create(
            slug=self.SLUG, name=name, description=self.DESC,
            associated_models=model_name, unicity_keys=unicity_keys)

        for default in self.DEFAULTS:
            values = self.DEFAULTS[default]
            imp_default = models.ImporterDefault.objects.create(
                importer_type=importer,
                target='__'.join(default))
            for key in values:
                if key in ('history_modifier',):
                    continue
                value = values[key]
                if hasattr(value, 'txt_idx') and value.txt_idx:
                    value = value.txt_idx
                elif hasattr(value, 'pk') and value.pk:
                    value = value.pk
                if callable(value):
                    value = value()
                models.ImporterDefaultValues.objects.create(
                    default_target=imp_default,
                    target=key,
                    value=value)
        for idx, line in enumerate(self.line_format):
            idx += 1
            if not line:
                continue
            column = models.ImporterColumn.objects.create(
                importer_type=importer, col_number=idx)
            targets = line.field_name
            if type(targets) not in (list, tuple):
                targets = [targets]
            formaters = line.formater
            if type(formaters) not in (list, tuple):
                formaters = [formaters]
            for idx, target in enumerate(targets):
                formater = formaters[idx]
                formater_name = formater.__class__.__name__
                if formater_name not in models.IMPORTER_TYPES_DCT:
                    formater_name = 'UnknowType'
                options = ''
                if formater_name == 'TypeFormater':
                    options = formater.model.__module__ + '.' + \
                        formater.model.__name__
                elif formater_name == 'UnicodeFormater':
                    options = unicode(formater.max_length or '')
                elif formater_name == 'DateFormater':
                    options = formater.date_formats[0]
                formater_model, created = \
                    models.FormaterType.objects.get_or_create(
                        formater_type=formater_name, options=options.strip(),
                        many_split=getattr(formater, 'many_split', None) or '')
                regexp_filter = None
                if getattr(formater, 'regexp', None):
                    regexp_filter, created = \
                        models.Regexp.objects.get_or_create(
                            regexp=formater.regex,
                            defaults={'name': "Default name"})
                models.ImportTarget.objects.get_or_create(
                    column=column, target=target, formater_type=formater_model,
                    force_new=getattr(formater, 'force_new', False),
                    concat=getattr(formater, 'concat', False),
                    concat_str=getattr(formater, 'concat_str', ''),
                    regexp_filter=regexp_filter,
                    comment=line.comment)
        return True

    def __init__(self, skip_lines=0, reference_header=None,
                 check_col_num=False, test=False, history_modifier=None,
                 output='silent', import_instance=None,
                 conservative_import=False):
        """
         * skip_line must be set if the data provided has got headers lines.
         * a reference_header can be provided to perform a data compliance
           check. It can be useful to warn about bad parsing.
         * test doesn't write in the database
        """
        self.skip_lines = skip_lines
        self.reference_header = reference_header
        self.test = test
        self.errors = []  # list of (line, col, message)
        self.validity = []  # list of (line, col, message)
        self.number_updated = 0
        self.number_created = 0
        self.check_col_num = check_col_num
        self.line_format = copy.copy(self.LINE_FORMAT)
        self.import_instance = import_instance
        self.archive = None
        self.conservative_import = conservative_import
        # for a conservative_import UNICITY_KEYS should be defined
        assert not self.conservative_import or bool(self.UNICITY_KEYS)
        self.DB_TARGETS = {}
        self.match_table = {}
        self.concats = set()
        self.concat_str = {}
        if import_instance and import_instance.imported_images:
            self.archive = import_instance.imported_images
        self._defaults = self.DEFAULTS.copy()
        # EXTRA_DEFAULTS are for multiple inheritance
        if self.EXTRA_DEFAULTS:
            for k in self.EXTRA_DEFAULTS:
                if k not in self._defaults:
                    self._defaults[k] = {}
                self._defaults[k].update(self.EXTRA_DEFAULTS[k])
        self.history_modifier = history_modifier
        self.output = output
        if not self.history_modifier:
            if self.import_instance:
                self.history_modifier = self.import_instance.user
            else:
                # import made by the CLI: get the first admin
                self.history_modifier = User.objects.filter(
                    is_superuser=True).order_by('pk')[0]

    def post_processing(self, item, data):
        # force django based post-processing for the item
        item.save()
        if hasattr(item, 'RELATED_POST_PROCESS'):
            for related_key in item.RELATED_POST_PROCESS:
                for related in getattr(item, related_key).all():
                    related.save()
        return item

    def initialize(self, table, output='silent', choose_default=False):
        """
        copy vals in columns and initialize formaters
        * output:
         - 'silent': no associations
         - 'cli': output by command line interface and stocked in the database
         - 'db': output on the database with no interactive association
           (further exploitation by web interface)
        """
        assert output in ('silent', 'cli', 'db')
        vals = []
        for idx_line, line in enumerate(table):
            if self.skip_lines > idx_line:
                continue
            for idx_col, val in enumerate(line):
                if idx_col >= len(self.line_format):
                    break
                if idx_col >= len(vals):
                    vals.append([])
                vals[idx_col].append(val)
        for idx, formater in enumerate(self.line_format):
            if formater and idx < len(vals):

                if self.DB_TARGETS:
                    field_names = formater.field_name
                    if type(field_names) not in (list, tuple):
                        field_names = [field_names]
                    db_targets = []
                    for field_name in field_names:
                        db_targets.append(
                            self.DB_TARGETS["{}-{}".format(
                                idx + 1, field_name)])
                    formater.reinit_db_target(db_targets)

                formater.init(vals[idx], output, choose_default=choose_default,
                              import_instance=self.import_instance)

    def importation(self, table, initialize=True, choose_default=False):
        if initialize:
            self.initialize(table, self.output, choose_default=choose_default)
        self._importation(table)

    def _associate_db_target_to_formaters(self):
        if not self.import_instance:
            return
        self.DB_TARGETS = {}
        from ishtar_common.models import ImporterColumn, ImportTarget
        for idx, line in enumerate(self.line_format):
            idx += 1
            if not line:
                continue
            col = ImporterColumn.objects.get(
                importer_type=self.import_instance.importer_type,
                col_number=idx)
            formater = line.formater
            targets = line.field_name
            if type(formater) not in (list, tuple):
                formater = [formater]
                targets = [targets]
            for target in targets:
                tg = target
                if type(target) == list and type(target[0]) == list:
                    tg = target[0]
                self.DB_TARGETS["{}-{}".format(idx, tg)] = \
                    ImportTarget.objects.get(column=col, target=tg)

    @classmethod
    def _field_name_to_data_dict(
            cls, field_name, value, data, force_value=False, concat=False,
            concat_str=u"", force_new=False):
        field_names = field_name
        if type(field_names) not in (list, tuple):
            field_names = [field_name]
        for field_name in field_names:
            keys = field_name.split('__')
            current_data = data
            for idx, key in enumerate(keys):
                if idx == (len(keys) - 1):  # last
                    if concat:
                        if key not in current_data:
                            current_data[key] = ""
                        if not value:
                            continue
                        current_data[key] = (current_data[key] + concat_str) \
                            if current_data[key] else u""
                        current_data[key] += value
                    elif force_value and value:
                        if concat_str and key in current_data \
                                and current_data[key]:
                            current_data[key] = unicode(current_data[key]) + \
                                concat_str + unicode(value)
                        else:
                            current_data[key] = value
                    elif key not in current_data or not current_data[key]:
                        current_data[key] = value
                    elif concat_str:
                        current_data[key] = unicode(current_data[key]) +\
                            concat_str + unicode(value)
                    if force_new:
                        current_data['__force_new'] = True
                elif key not in current_data:
                    current_data[key] = {}
                current_data = current_data[key]
        return data

    def _importation(self, table):
        self.match_table = {}
        table = list(table)
        if not table or not table[0]:
            raise ImporterError(self.ERRORS['no_data'], ImporterError.HEADER)
        if self.check_col_num and len(table[0]) > len(self.line_format):
            raise ImporterError(self.ERRORS['too_many_cols'] % {
                'user_col': len(table[0]), 'ref_col': len(self.line_format)})
        self.errors = []
        self.validity = []
        self.number_imported = 0
        # index of the last required column
        for idx_last_col, formater in enumerate(reversed(self.line_format)):
            if formater and formater.required:
                break
        else:
            idx_last_col += 1
        # min col number to be filled
        self.min_col_number = len(self.line_format) - idx_last_col
        # check the conformity with the reference header
        if self.reference_header and \
           self.skip_lines and \
           self.reference_header != table[0]:
            raise ImporterError(self.ERRORS['header_check'],
                                type=ImporterError.HEADER)
        self.now = datetime.datetime.now()
        start = datetime.datetime.now()
        total = len(table)
        if self.output == 'cli':
            sys.stdout.write("\n")
        for idx_line, line in enumerate(table):
            if self.output == 'cli':
                left = None
                if idx_line > 10:
                    ellapsed = datetime.datetime.now() - start
                    time_by_item = ellapsed / idx_line
                    if time_by_item:
                        left = ((total - idx_line) * time_by_item).seconds
                txt = u"\r* %d/%d" % (idx_line + 1, total)
                if left:
                    txt += u" (%d seconds left)" % left
                sys.stdout.write(txt.encode('utf-8'))
                sys.stdout.flush()
            try:
                self._line_processing(idx_line, line)
            except ImporterError, msg:
                self.errors.append((idx_line, None, msg))

    def _line_processing(self, idx_line, line):
        self.idx_line = idx_line
        if self.skip_lines > idx_line:
            self.validity.append(line)
            return
        if not line:
            self.validity.append([])
            return
        self._throughs = []  # list of (formater, value)
        self._post_processing = []  # list of (formater, value)
        data = {}

        # keep in database the raw line for testing purpose
        if self.IMPORTED_LINE_FIELD:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(line)
            data[self.IMPORTED_LINE_FIELD] = output.getvalue()

        n = datetime.datetime.now()
        logger.debug('%s - Processing line %d' % (unicode(n - self.now),
                                                  idx_line))
        self.now = n
        n2 = n
        self.c_errors = False
        c_row = []
        for idx_col, val in enumerate(line):
            try:
                self._row_processing(c_row, idx_col, idx_line, val, data)
            except:
                pass

        self.validity.append(c_row)
        if not self.c_errors and (idx_col + 1) < self.min_col_number:
            self.c_errors = True
            self.errors.append((
                idx_line + 1, idx_col + 1,
                self.ERRORS['not_enough_cols'] % self.min_col_number))
        if self.c_errors:
            return
        n = datetime.datetime.now()
        logger.debug('* %s - Cols read' % (unicode(n - n2)))
        n2 = n
        if self.test:
            return
        # manage unicity of items (mainly for updates)
        if 'history_modifier' in \
                self.OBJECT_CLS._meta.get_all_field_names():
            data['history_modifier'] = self.history_modifier

        obj, created = self.get_object(self.OBJECT_CLS, data)
        if self.import_instance and hasattr(obj, 'imports') \
           and created:
            obj.imports.add(self.import_instance)

        if created:
            self.number_created += 1
        else:
            self.number_updated += 1

        if not created and 'defaults' in data:
            for k in data['defaults']:
                setattr(obj, k, data['defaults'][k])
            obj.save()
        n = datetime.datetime.now()
        logger.debug('* %s - Item saved' % (unicode(n - n2)))
        n2 = n
        for formater, value in self._throughs:
            n = datetime.datetime.now()
            logger.debug('* %s - Processing formater %s' % (unicode(n - n2),
                         formater.field_name))
            n2 = n
            data = {}
            if formater.through_dict:
                data = formater.through_dict.copy()
            if formater.through_key:
                data[formater.through_key] = obj
            data[formater.field_name] = value
            through_cls = formater.through
            if formater.through_unicity_keys:
                data['defaults'] = {}
                for k in data.keys():
                    if k not in formater.through_unicity_keys \
                       and k != 'defaults':
                        data['defaults'][k] = data.pop(k)
            if '__force_new' in data:
                created = data.pop('__force_new')
                t_obj = through_cls.objects.create(**data)
            else:
                t_obj, created = through_cls.objects.get_or_create(**data)
            if not created and 'defaults' in data:
                for k in data['defaults']:
                    setattr(t_obj, k, data['defaults'][k])
                t_obj.save()
            if self.import_instance and hasattr(t_obj, 'imports') \
               and created:
                t_obj.imports.add(self.import_instance)

        for formater, val in self._post_processing:
            formater.post_process(obj, data, val, owner=self.history_modifier)

        obj = self.post_processing(obj, data)

    def _row_processing(self, c_row, idx_col, idx_line, val, data):
        if idx_col >= len(self.line_format):
            return

        formater = self.line_format[idx_col]

        if formater and formater.post_processing:
            self._post_processing.append((formater, val))

        if not formater or not formater.field_name:
            c_row.append(_('Not imported'))
            return

        # regex management
        if formater.regexp:
            # multiline regexp is a mess...
            val = val.replace('\n', NEW_LINE_BREAK)
            match = formater.regexp.match(val)
            if not match:
                if formater.required:
                    self.errors.append(
                        (idx_line + 1, idx_col + 1,
                         self.ERRORS['value_required']))
                    self.c_errors = True
                elif not val.strip():
                    c_row.append("")
                    return
                val = val.replace(NEW_LINE_BREAK, '\n')
                self.errors.append(
                    (idx_line + 1, idx_col + 1,
                     unicode(self.ERRORS['regex_not_match']) + val))
                c_row.append("")
                return
            val_group = [v.replace(NEW_LINE_BREAK, '\n') if v else ''
                         for v in match.groups()]
        else:
            val_group = [val]

        c_values = []
        for idx_v, v in enumerate(val_group):
            func = formater.formater
            if type(func) in (list, tuple):
                func = func[idx_v]
            if not callable(func) and type(func) in (unicode, str):
                func = getattr(self, func)

            values = [v]
            many_values = getattr(func, 'many_split', None)
            if many_values:
                values = re.split(func.many_split, values[0])
            formated_values = []

            field_name = formater.field_name
            force_new = formater.force_new
            if type(field_name) in (list, tuple):
                field_name = field_name[idx_v]
            if type(force_new) in (list, tuple):
                force_new = force_new[idx_v]
            if formater.concat:
                self.concats.add(field_name)
            concat_str = formater.concat_str
            if type(formater.concat_str) in (list, tuple):
                concat_str = concat_str[idx_v]
            if concat_str:
                self.concat_str[field_name] = concat_str

            if self.DB_TARGETS:
                formater.reinit_db_target(
                    self.DB_TARGETS["{}-{}".format(idx_col + 1, field_name)],
                    idx_v)
            for idx, v in enumerate(values):
                value = None
                try:
                    if formater.regexp_formater_args:
                        args = []
                        for idx in formater.regexp_formater_args[idx_v]:
                            args.append(val_group[idx])
                        value = func.format(*args)
                    else:
                        if getattr(func, 'need_archive', False):
                            value = func.format(v, archive=self.archive)
                        else:
                            value = func.format(v)
                except ValueError, e:
                    if formater.required:
                        self.c_errors = True
                    self.errors.append((idx_line + 1, idx_col + 1, e.message))
                    c_values.append('')
                    return
                formated_values.append(value)
            if hasattr(func, 'match_table'):
                if field_name not in self.match_table:
                    self.match_table[field_name] = {}
                self.match_table[field_name].update(func.match_table)

            value = formated_values
            if not many_values:
                value = formated_values[0]

            printed_values = value
            if type(value) not in (list, tuple):
                printed_values = [value]
            try:
                # don't reunicode - unicoded values
                c_values.append(u" ; ".join([v for v in printed_values]))
            except TypeError:
                c_values.append(u" ; ".join([unicode(v)
                                             for v in printed_values]))
            if value is None and formater.required:
                self.c_errors = True
                self.errors.append((idx_line + 1, idx_col + 1,
                                   self.ERRORS['value_required']))
                return

            field_names = [field_name]
            force_news = [force_new]
            concats = [formater.concat]
            concat_str = [concat_str]
            for duplicate_field in formater.duplicate_fields:
                if type(duplicate_field[0]) in (list, tuple):
                    duplicate_field, force_new, concat, conc_str = \
                        duplicate_field[idx_v]
                else:
                    duplicate_field, force_new, concat, conc_str = \
                        duplicate_field
                field_names += [duplicate_field]
                force_news += [force_new]
                concats += [concat]
                concat_str += [conc_str]

            if formater.through:
                self._throughs.append((formater, value))
            else:
                for idx, field_name in enumerate(field_names):
                    self._field_name_to_data_dict(
                        field_name, value, data, formater.force_value,
                        force_new=force_news[idx], concat=concats[idx],
                        concat_str=concat_str[idx])
        c_row.append(u" ; ".join([v for v in c_values]))

    def get_field(self, cls, attribute, data, m2ms, c_path):
        field_object, model, direct, m2m = \
            cls._meta.get_field_by_name(attribute)
        if m2m:
            many_values = data.pop(attribute)
            if hasattr(field_object, 'rel'):
                model = field_object.rel.to
            elif hasattr(field_object, 'to'):
                model = field_object.to
            elif hasattr(field_object, 'model'):
                model = field_object.model
            if type(many_values) not in (list, tuple):
                many_values = [many_values]
            for val in many_values:
                if val.__class__ == model:
                    m2ms.append((attribute, val))
                elif val.__class__ != model and type(val) == dict:
                    vals = []

                    # contruct many dict for each values
                    default_dict = {}

                    # # get default values
                    p = [attribute]
                    if c_path:
                        p = list(c_path) + p
                    p = tuple(p)
                    if p in self._defaults:
                        for k in self._defaults[p]:
                            default_dict[k] = self._defaults[p][k]
                    # # init with simple values that will be duplicated
                    for key in val.keys():
                        if type(val[key]) not in (list, tuple):
                            default_dict[key] = val[key]
                    vals.append(default_dict.copy())
                    # # manage multiple values
                    for key in val.keys():
                        if type(val[key]) in (list, tuple):
                            for idx, v in enumerate(val[key]):
                                if len(vals) <= idx:
                                    vals.append(default_dict.copy())
                                vals[idx][key] = v

                    # check that m2m are not empty
                    notempty = False
                    for dct in vals:
                        for k in dct:
                            if dct[k] not in ("", None):
                                notempty = True
                                break
                    if not notempty:
                        continue

                    field_names = model._meta.get_all_field_names()
                    for v in vals:
                        if 'history_modifier' in field_names:
                            if 'defaults' not in v:
                                v['defaults'] = {}
                            v['defaults']['history_modifier'] = \
                                self.history_modifier
                        m2m_m2ms = []
                        c_c_path = c_path[:]
                        for k in v.keys():
                            if k not in field_names:
                                continue
                            self.get_field(model, k, v, m2m_m2ms, c_c_path)
                        if '__force_new' in v:
                            created = v.pop('__force_new')
                            has_values = bool([1 for k in v if v[k]])
                            if has_values:
                                v = model.objects.create(**v)
                            else:
                                continue
                        else:
                            v['defaults'] = v.get('defaults', {})
                            v, created = model.objects.get_or_create(
                                **v)
                        for att, objs in m2m_m2ms:
                            if type(objs) not in (list, tuple):
                                objs = [objs]
                            for obj in objs:
                                getattr(v, att).add(obj)
                        if self.import_instance \
                           and hasattr(v, 'imports') and created:
                            v.imports.add(self.import_instance)
                        m2ms.append((attribute, v))
        elif hasattr(field_object, 'rel') and field_object.rel:
            if type(data[attribute]) == dict:
                # put history_modifier for every created item
                if 'history_modifier' in \
                   field_object.rel.to._meta.get_all_field_names():
                    data[attribute]['history_modifier'] = \
                        self.history_modifier
                try:
                    c_path.append(attribute)
                    data[attribute], created = self.get_object(
                        field_object.rel.to, data[attribute].copy(), c_path)
                except ImporterError, msg:
                    self.errors.append((self.idx_line, None, msg))
                    data[attribute] = None
            elif type(data[attribute]) == list:
                data[attribute] = data[attribute][0]

    def get_object(self, cls, data, path=[]):
        m2ms = []
        if data and type(data) == dict:
            c_path = path[:]

            # get all related fields
            for attribute in list(data.keys()):
                c_c_path = c_path[:]
                if not attribute:
                    data.pop(attribute)
                    continue
                if not data[attribute]:
                    continue
                if attribute != '__force_new':
                    self.get_field(cls, attribute, data, m2ms, c_c_path)

            # filter uncessary default values
            create_dict = copy.deepcopy(data)
            for k in create_dict.keys():
                if type(create_dict[k]) == dict:
                    create_dict.pop(k)

            # default values
            path = tuple(path)
            defaults = {}
            if path in self._defaults:
                for k in self._defaults[path]:
                    if (k not in data or not data[k]):
                        defaults[k] = self._defaults[path][k]

            if 'history_modifier' in create_dict:
                defaults.update({
                    'history_modifier': create_dict.pop('history_modifier')
                })

            try:
                try:
                    dct = create_dict.copy()
                    for key in dct:
                        if callable(dct[key]):
                            dct[key] = dct[key]()
                    if '__force_new' in dct:
                        created = dct.pop('__force_new')
                        if not [k for k in dct if dct[k] is not None]:
                            return None, created
                        new_dct = defaults.copy()
                        new_dct.update(dct)
                        obj = cls.objects.create(**new_dct)
                    else:
                        # manage UNICITY_KEYS - only level 1
                        if not path and self.UNICITY_KEYS:
                            for k in dct.keys():
                                if k not in self.UNICITY_KEYS \
                                   and k != 'defaults':
                                    defaults[k] = dct.pop(k)

                        dct['defaults'] = defaults.copy()
                        obj, created = cls.objects.get_or_create(**dct)

                        if not created and not path and self.UNICITY_KEYS:
                            changed = False
                            if self.conservative_import:
                                for k in dct['defaults']:
                                    new_val = dct['defaults'][k]
                                    if new_val is None or new_val == '':
                                        continue
                                    val = getattr(obj, k)
                                    if val is None or val == '':
                                        changed = True
                                        setattr(obj, k, new_val)
                                    elif k in self.concats \
                                            and type(val) == unicode \
                                            and type(new_val) == unicode:
                                        setattr(obj, k, val + u"\n" + new_val)
                            else:
                                for k in dct['defaults']:
                                    new_val = dct['defaults'][k]
                                    if new_val is None or new_val == '':
                                        continue
                                    changed = True
                                    setattr(obj, k, new_val)
                            if changed:
                                obj.save()
                    if self.import_instance and hasattr(obj, 'imports') \
                       and created:
                        obj.imports.add(self.import_instance)
                except ValueError as e:
                    raise IntegrityError(e.message)
                except IntegrityError as e:
                    raise IntegrityError(e.message)
                except DatabaseError as e:
                    raise IntegrityError(e.message)
                except cls.MultipleObjectsReturned as e:
                    created = False
                    if 'defaults' in dct:
                        dct.pop('defaults')
                    raise IntegrityError(e.message)
                    # obj = cls.objects.filter(**dct).all()[0]
                for attr, value in m2ms:
                    values = [value]
                    if type(value) in (list, tuple):
                        values = value
                    for v in values:
                        getattr(obj, attr).add(v)
                        # force post save script
                        v.save()
                if m2ms:
                    # force post save script
                    obj.save()
            except IntegrityError as e:
                message = e.message
                try:
                    message = e.message.decode('utf-8')
                except (UnicodeDecodeError, UnicodeDecodeError):
                    message = ''
                try:
                    data = unicode(data)
                except UnicodeDecodeError:
                    data = ''
                raise ImporterError(
                    "Erreur d'import %s %s, contexte : %s, erreur : %s"
                    % (unicode(cls), unicode("__".join(path)),
                       unicode(data), message))
            return obj, created
        return data

    def _format_csv_line(self, values, empty=u"-"):
        return u'"' + u'","'.join(
            [(v and unicode(v).replace('"', '""')) or empty
             for v in values]) + u'"'

    def _get_csv(self, rows, header=[], empty=u"-"):
        if not rows:
            return ""
        csv_v = []
        if header:
            csv_v.append(self._format_csv_line(header, empty=empty))
        for values in rows:
            csv_v.append(self._format_csv_line(values, empty=empty))
        return u"\n".join(csv_v)

    def get_csv_errors(self):
        return self._get_csv(
            self.errors, header=[_("line"), _("col"), _("error")])

    def get_csv_result(self):
        return self._get_csv(self.validity)

    def get_csv_matches(self):
        header = [_('field'), _('source'), _('result')]
        values = []
        for field in self.match_table:
            for source in self.match_table[field]:
                values.append((field, source, self.match_table[field][source]))
        return self._get_csv(values, header=header)

    @classmethod
    def choices_check(cls, choices):
        def function(value):
            choices_dct = dict(choices)
            value = value.strip()
            if not value:
                return
            if value not in choices_dct.values():
                raise ValueError(
                    _(u"\"%(value)s\" not in %(values)s") % {
                        'value': value,
                        'values': u", ".join([val
                                              for val in choices_dct.values()])
                    })
            return value
        return function
