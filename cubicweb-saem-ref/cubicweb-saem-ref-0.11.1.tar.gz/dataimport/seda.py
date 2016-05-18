# coding: utf-8
import os
from os.path import join, dirname, basename

from cubicweb.dataimport.importer import HTMLImportLog

from cubes.skos.sobjects import lcsv_extentities, store_skos_extentities

from cubes.saem_ref.sobjects.skos import _store


def lcsv_import(cnx, store, fpath, scheme_uri):
    import_log = HTMLImportLog(basename(fpath))
    stream = open(fpath)
    entities = lcsv_extentities(stream, scheme_uri, '\t', 'utf-8')
    store_skos_extentities(cnx, store, entities, import_log,
                           raise_on_error=True, extid_as_cwuri=False)


def create_concept_scheme(cnx, store, title, fpath, rtype, comment, ark):
    scheme = cnx.create_entity('ConceptScheme', title=title, ark=ark)
    inserted = cnx.execute(
        'SET X scheme_relation CR WHERE CR name "%s", X eid %%(x)s' % rtype,
        {'x': scheme.eid})
    assert inserted, comment
    lcsv_import(cnx, store, fpath, scheme.cwuri)


def import_seda_schemes(cnx):
    # 25651 = Archives départementales de la Gironde (ADGIRONDE)
    # XXX ensure that:
    # * NAA for those vocabulary is 25651
    # * generated ark are identical from one instance to another
    store = _store(cnx, naa_what='25651')
    for i, (title, rtype, comment, fname) in enumerate([
        (u"SEDA : Codes de restriction d'accès",
         'seda_access_restriction_code',
         'access control',
         'seda_access_control.csv'),
        (u'SEDA : Sort final',
         'seda_appraisal_rule_code',
         'appraisal rule',
         'seda_appraisal_rule_code.csv'),
        (u'SEDA : Niveaux de description de contenu',
         'seda_description_level',
         'description level',
         'seda_description_level.csv'),
        (u'SEDA : Formats de fichier source',
         'seda_file_type_code',
         'file type code',
         'seda_file_type_code.csv'),
        (u'SEDA : Jeu de caractères de codage',
         'seda_character_set_code',
         'character set code',
         'seda_character_set_code.csv'),
        (u'SEDA : Codes des types de contenu',
         'seda_document_type_code',
         'document type code',
         'seda_document_type_code.csv'),
        (u"SEDA: Durée d'utilité administrative",
         'seda_appraisal_rule_duration',
         'appraisal rule duration',
         'seda_dua.csv'),
    ]):
        if not cnx.find('ConceptScheme', title=title):
            fpath = join(dirname(__file__), os.pardir, 'migration', 'data', fname)
            ark = u'25651/v00000000%s' % i
            create_concept_scheme(cnx, store, title, fpath, rtype, comment, ark=ark)
    store.flush()
    store.commit()
    store.finish()
