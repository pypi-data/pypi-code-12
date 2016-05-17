# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from contextlib import contextmanager

import os
import os.path as path
import codecs
import yaml
import logging

import gaia.base as base

logger = logging.getLogger('gaia')

i18n_path = os.path.join(base.find_path(), 'i18n')

tables = {}

for root, dirs, files in os.walk(i18n_path, followlinks=True):
    logger.info("i18n checking [%s, %s, %s] ..." % (root, str(dirs), str(files)))
    if path.basename(root) == 'i18n':
        for d in dirs:
            tables[d] = {}
    else:
        lang = path.basename(root)
        logger.info("initialing language %s ..." % lang)

        for fnm in files:
            fpth = os.path.join(root, fnm)
            bndl = ''.join(fnm.split('.')[:-1])
            logger.info("initialing bundle [%s:%s] ..." % (lang, bndl))
            with codecs.open(fpth, "r", "utf-8") as f:
                s = f.read()
                try:
                    tables[lang][bndl] = yaml.load(s)
                    logger.info("init bundle [%s:%s] done ..." % (lang, bndl))
                except Exception as e:
                    tables[lang][bndl] = {}
                    logger.error(e)


def table(lang, tname):
    if lang in tables and tname in tables[lang]:
        return tables[lang][tname]
    else:
        raise Exception('[%s:%s] is not supported!' % (lang, tname))


def get(lang, table, key):
    if lang in tables and table in tables[lang] and key in tables[lang][table]:
        return tables[lang][table][key]
    else:
        raise Exception('[%s:%s:%s] is not supported!' % (lang, table, key))


@contextmanager
def ctx(lang, tname):
    yield table(lang, tname)
