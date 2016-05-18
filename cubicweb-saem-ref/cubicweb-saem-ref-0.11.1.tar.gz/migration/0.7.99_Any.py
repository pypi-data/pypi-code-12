from cubicweb.schema import ETYPE_NAME_MAP
ETYPE_NAME_MAP['ProfileArchive'] = 'ProfileArchiveObject'
sql('ALTER TABLE cw_ProfileArchive add column cw_seda_parent integer')
sql('UPDATE cw_ProfileArchive SET cw_seda_parent=cw_seda_archive_profile')
drop_relation_type('seda_archive_profile')
rename_entity_type('ProfileArchive', 'ProfileArchiveObject')
sql("UPDATE entities SET type='ProfileArchiveObject' WHERE type='ProfileArchive';")

for etype in ('FileTypeCode', 'CharacterSetCode', 'DocumentTypeCode'):
    rename_entity_type(etype, 'SEDA' + etype)
