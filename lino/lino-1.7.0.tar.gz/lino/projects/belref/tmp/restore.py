#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This is a Python dump created using Lino 1.7.0, Django 1.9.5, Python 2.7.6, Babel 2.2.0, Jinja 2.8, Sphinx 1.4a1, python-dateutil 2.5.2, OdfPy ODFPY/1.3.2, docutils 0.12, suds 0.4, PyYaml 3.11, Appy 0.9.2 (2015/04/30 15:00).

"""
from __future__ import unicode_literals

import logging
logger = logging.getLogger('lino.modlib.lino_startup.management.commands.dump2py')
import os

SOURCE_VERSION = '0.1'

from decimal import Decimal
from datetime import datetime as dt
from datetime import time, date
from django.conf import settings
# from django.contrib.contenttypes.models import ContentType
from lino.utils.dpy import create_mti_child
from lino.utils.dpy import DpyLoader
from lino.core.utils import resolve_model
        
def new_content_type_id(m):
    if m is None: return m
    ct = settings.SITE.modules.contenttypes.ContentType.objects.get_for_model(m)
    if ct is None: return None
    return ct.pk
    

def bv2kw(fieldname, values):
    """
    Needed if `Site.languages` changed between dumpdata and loaddata
    """
    return settings.SITE.babelkw(fieldname, fr=values[0],nl=values[1],de=values[2])
    
concepts_Concept = resolve_model("concepts.Concept")
concepts_Link = resolve_model("concepts.Link")
countries_Country = resolve_model("countries.Country")
countries_Place = resolve_model("countries.Place")
system_SiteConfig = resolve_model("system.SiteConfig")


def create_concepts_concept(id, name, abbr, wikipedia, definition, is_jargon_domain):
    kw = dict()
    kw.update(id=id)
    if name is not None: kw.update(bv2kw('name',name))
    if abbr is not None: kw.update(bv2kw('abbr',abbr))
    if wikipedia is not None: kw.update(bv2kw('wikipedia',wikipedia))
    if definition is not None: kw.update(bv2kw('definition',definition))
    kw.update(is_jargon_domain=is_jargon_domain)
    return concepts_Concept(**kw)

def create_concepts_link(id, type, parent_id, child_id):
    if type: type = settings.SITE.modules.concepts.LinkTypes.get_by_value(type)
    kw = dict()
    kw.update(id=id)
    kw.update(type=type)
    kw.update(parent_id=parent_id)
    kw.update(child_id=child_id)
    return concepts_Link(**kw)

def create_countries_country(name, isocode, short_code, iso3, inscode, actual_country_id):
    kw = dict()
    if name is not None: kw.update(bv2kw('name',name))
    kw.update(isocode=isocode)
    kw.update(short_code=short_code)
    kw.update(iso3=iso3)
    kw.update(inscode=inscode)
    kw.update(actual_country_id=actual_country_id)
    return countries_Country(**kw)

def create_countries_place(id, parent_id, name, country_id, zip_code, type, inscode):
    if type: type = settings.SITE.modules.countries.PlaceTypes.get_by_value(type)
    kw = dict()
    kw.update(id=id)
    kw.update(parent_id=parent_id)
    if name is not None: kw.update(bv2kw('name',name))
    kw.update(country_id=country_id)
    kw.update(zip_code=zip_code)
    kw.update(type=type)
    kw.update(inscode=inscode)
    return countries_Place(**kw)

def create_system_siteconfig(id, default_build_method, simulate_today):
    if default_build_method: default_build_method = settings.SITE.modules.printing.BuildMethods.get_by_value(default_build_method)
    kw = dict()
    kw.update(id=id)
    kw.update(default_build_method=default_build_method)
    kw.update(simulate_today=simulate_today)
    return system_SiteConfig(**kw)




def main():
    loader = DpyLoader(globals())
    from django.core.management import call_command
    # call_command('initdb', interactive=False)
    call_command('initdb')
    os.chdir(os.path.dirname(__file__))
    loader.initialize()

    execfile("concepts_concept.py")
    execfile("concepts_link.py")
    execfile("countries_country.py")
    execfile("countries_place.py")
    execfile("system_siteconfig.py")
    loader.finalize()

if __name__ == '__main__':
    main()
