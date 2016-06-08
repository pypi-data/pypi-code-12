#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

import locale
import re
from zipfile import ZipFile, ZIP_DEFLATED
from cStringIO import StringIO
from xml.etree.cElementTree import ElementTree, fromstring

from django.conf import settings
from ooo_translation import ooo_translation


def translate_context(context, locale):
    if locale not in ooo_translation:
        return context
    new_context = {}
    for k in context:
        new_key = k
        if k in ooo_translation[locale]:
            new_key = ooo_translation[locale][k]
        new_context[new_key] = context[k]
    return new_context

OOO_NS = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"


def _set_value_from_formula(value, context, default_value):
    value = value.strip()
    if value.startswith("ooow:") and len(value) >= 5:
        value = value[5:]
    if value.startswith('"') and value.endswith('"') and len(value) > 1:
        value = value[1:-1]
    elif value in context:
        value = _format_value(context[value], default_value)
    else:
        value = None
    return value


def _parse_condition(condition, context, default_value):
    # parse only == and != operator
    operator = ""
    if "!=" in condition:
        operator = "!="
    elif "==" in condition:
        operator = "=="
    else:
        return
    var1, var2 = condition.split(operator)
    var1 = _set_value_from_formula(var1, context, default_value)
    var2 = _set_value_from_formula(var2, context, default_value)
    res = var1 == var2
    if operator == '!=':
        res = not res
    return res


def _format_value(value, default_value):
    if hasattr(value, 'strftime'):
        c_locale = settings.LANGUAGE_CODE.split('-')
        if len(c_locale) == 2:
            c_locale[1] = c_locale[1].upper()
        c_locale = "_".join(c_locale)
        if locale.getlocale()[0] != c_locale:
            for loc in (c_locale, c_locale + '.utf8'):
                try:
                    locale.setlocale(locale.LC_ALL, loc)
                    break
                except:
                    pass
        try:
            if settings.DATE_FORMAT:
                value = value.strftime(settings.DATE_FORMAT).lower()
            else:
                value = value.strftime('%x')
        except ValueError:
            value = unicode(value)
        if locale.getlocale()[1]:
            value = value.decode(locale.getlocale()[1])
    value = unicode(value) if value else default_value
    return value

VAR_EXPR = u"###%sVAR %s###"
WHOLE_KEY_FILTER = u"((?:(?: )*(?:<[^#>]*>)*(?: )*(?:[-a-zA-Z0-9_])*(?: )*)*)"
WHOLE_KEY_FILTER = u"([^#]*)"
RE_VAR = re.compile(VAR_EXPR % (WHOLE_KEY_FILTER, WHOLE_KEY_FILTER))
IF_EXPR = u"###%sIF %s###(.*)###ENDIF###"
RE_IF = re.compile(IF_EXPR % (WHOLE_KEY_FILTER, WHOLE_KEY_FILTER))
TAG_FILTER = re.compile(u"(<[^<^>]*>)")
KEY_FILTER = re.compile(u"([-a-zA-Z0-9_]*)")


def _filter_key(base_key):
    # return (key, extra_marker)
    # manage strange key such as:
    # test_<text:span text:style-name="T1">date</text:span>
    key = base_key[:]
    key = key.strip()
    tags, new_key = '', key[:]
    for tag in TAG_FILTER.findall(key):
        tags += tag
        new_key = new_key.replace(tag, '')
    full_key = ''
    for k in KEY_FILTER.findall(new_key):
        if not k:
            continue
        full_key += k
    return full_key, tags


def _custom_parsing(context, value, default_value=''):
    """
    ###VAR nom_var### for displaying a variable name
    ###IF nom_var### ###ENDIF### for conditionnal display
    Be carreful nested condition are not yet managed!
    """
    for regexp, sub_exp, if_cond in ((RE_IF, IF_EXPR, True),
                                     (RE_VAR, VAR_EXPR, False)):
        for base_key in regexp.findall(value[:]):
            v, val = "", None
            if if_cond:  # the value inside the if is parsed
                pre_tag, base_key, val = base_key
            else:
                pre_tag, base_key = base_key
            key, extra_markers = _filter_key(base_key)
            v = ''
            if pre_tag:
                v = pre_tag
            if key in context and context[key]:
                if if_cond:
                    v += _custom_parsing(context, val, default_value)
                else:
                    v += _format_value(context[key], default_value)
            # to preserve a consistent OOO file put extra_markers
            if extra_markers:
                v += extra_markers
            value = re.sub(sub_exp % (pre_tag, base_key), v, value)
    return value


def _ooo_replace(content, context, missing_keys, default_value=''):

    # regular ooo parsing
    for xp in ('variable-set', 'variable-get'):
        for p in content.findall(".//" + OOO_NS + xp):
            name = p.get(OOO_NS + "name")
            if name in context:
                value = context[name]
                p.text = _format_value(value, default_value)
            else:
                if default_value is not None:
                    p.text = default_value
                missing_keys.add(name)
    for p in content.findall(".//" + OOO_NS + "conditional-text"):
        condition = p.get(OOO_NS + "condition")
        res = 'true' if _parse_condition(condition, context, default_value) \
              else 'false'
        value = p.get(OOO_NS + 'string-value-if-' + res)
        value = _format_value(value, default_value)
        if value.strip() in context:
            value = context[value.strip()]
        p.text = value

    # raw content parsing
    str_io = StringIO()
    content.write(str_io)
    value = str_io.getvalue()
    value = _custom_parsing(context, value, default_value).encode('utf-8')
    return value


def ooo_replace(infile, outfile, context, default_value=''):
    inzip = ZipFile(infile, 'r', ZIP_DEFLATED)
    outzip = ZipFile(outfile, 'w', ZIP_DEFLATED)

    values = {}
    missing_keys = set()
    for xml_file in ('content.xml', 'styles.xml'):
        content = ElementTree(fromstring(inzip.read(xml_file)))
        values[xml_file] = _ooo_replace(content, context, missing_keys,
                                        default_value)

    for f in inzip.infolist():
        if f.filename in values:
            outzip.writestr(f.filename, values[f.filename])
        else:
            outzip.writestr(f, inzip.read(f.filename))

    inzip.close()
    outzip.close()
    return missing_keys

if __name__ == '__main__':
    infile = "../archaeological_files/tests/"\
             "AR_dossier_DRAC_modele_ishtar_1-MOD.odt"
    outfile = "../archaeological_files/tests/"\
              "AR_dossier_DRAC_modele_ishtar-test.odt"
    rep = {"file_incharge_surname": u"Yann",
           "file_incharge_name": u"Le Jeune",
           "fileact_ref": u"ref"}
    ooo_replace(infile, outfile, rep, default_value="")
