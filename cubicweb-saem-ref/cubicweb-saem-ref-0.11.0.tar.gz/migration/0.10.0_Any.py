drop_entity_type('MirrorEntity')
drop_entity_type('AlfrescoConnector')
drop_entity_type('AsalaeConnector')

for ertype in ('Label', 'ConceptScheme', 'in_scheme', 'broader_concept', 'label_of',
               'SEDAProfile'):
    sync_schema_props_perms(ertype, syncrdefs=False, syncprops=False)

with session.deny_all_hooks_but('metadata', 'syncschema'):
    rename_relation_type('vocabulary_source', 'equivalent_concept', force=True)
add_relation_type('vocabulary_source')

rql('SET X vocabulary_source SC WHERE X equivalent_concept C, C in_scheme SC')
commit()

add_entity_type('Citation')
add_entity_type('Occupation')

