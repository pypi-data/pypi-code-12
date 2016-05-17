sync_schema_props_perms('contact_point')
sync_schema_props_perms('cwuri')
sync_schema_props_perms('ark')

drop_attribute('ChronologicalRelation', 'start_date')
drop_attribute('ChronologicalRelation', 'end_date')

add_cube('vtimeline')

for eid in set(x for x, in rql('Any S WHERE X is ConceptScheme, X cw_source S, S name != "system"', build_descr=False)):
    source = cnx.entity_from_eid(eid)
    create_entity('SKOSSource', name=source.name,
                  url=source.url, through_cw_source=source)
    commit()

add_entity_type('SEDAFileTypeCode')
add_relation_type('seda_file_type_code')
add_relation_type('seda_file_type_code_value')

add_entity_type('SEDACharacterSetCode')
add_relation_type('seda_character_set_code')
add_relation_type('seda_character_set_code_value')

add_entity_type('SEDADocumentTypeCode')
add_relation_type('seda_document_type_code')
add_relation_type('seda_document_type_code_value')

# Add new SEDA schemes by calling back create_seda_schemes script (no-op for
# existing schemes).
from os.path import join, dirname
process_script(join(dirname(__file__), 'create_seda_schemes.py'))
