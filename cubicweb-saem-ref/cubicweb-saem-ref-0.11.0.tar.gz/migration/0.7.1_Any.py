# coding: utf-8
for rtype in ('seda_file_type_code', 'seda_document_type_code', 'seda_character_set_code'):
    sync_schema_props_perms(rtype)
    sync_schema_props_perms(rtype + '_value')


add_attribute('SEDADocumentTypeCode', 'user_annotation')

for title in (u'SEDA : Formats de fichier source',
              u'SEDA : jeu de caractères de codage',
              u'SEDA : codes des types de contenu'):
    find('ConceptScheme', title=title).one().cw_delete()
    commit()

from os.path import join, dirname
process_script(join(dirname(__file__), 'create_seda_schemes.py'))


# add word table
sqls = """
CREATE EXTENSION  pg_trgm;;
CREATE TABLE words (
  etype VARCHAR(64) NOT NULL,
  word VARCHAR(100) NOT NULL
);;
CREATE INDEX words_unique_idx ON words (etype, word);;
CREATE INDEX words_word_idx ON words USING gin(word gin_trgm_ops)
"""
for statement in sqls.split(';;'):
    sql(statement)

print 'you should now rebuild the text index using `cubicweb-ctl db-rebuild-fti %s`' % config.appid
