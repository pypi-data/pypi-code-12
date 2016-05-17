
if versions_map['saem_ref'][0] < (0, 7, 99):
    print "Migration has to be interrupted but is not finished."
    print "You should restart the command to fulfill it."
    import sys
    sys.exit(0)

repo.system_source.do_fti = False

for rtype in ('file_type_code', 'character_set_code', 'document_type_code'):
    cs = rql('Any CS WHERE CS scheme_relation RT, RT name %(rt)s', {'rt': rtype})[0][0]
    with cnx.deny_all_hooks_but('syncschema', 'metadata'):
        rename_relation_type(rtype, 'seda_' + rtype)
        rename_relation_type(rtype + '_value', 'seda_' + rtype + '_value')
        sync_schema_props_perms('seda_' + rtype + '_value')
    rql('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name %(rt)s',
        {'cs': cs, 'rt': 'seda_' + rtype})

add_relation_definition('ProfileArchiveObject', 'seda_parent', 'SEDAProfile')
drop_entity_type('ProfileArchive')
sync_schema_props_perms(('ProfileArchiveObject', 'user_cardinality', 'String'))

sync_schema_props_perms(('ProfileArchiveObject', 'seda_parent', 'ProfileArchiveObject'))
sync_schema_props_perms(('ProfileDocument', 'seda_parent', 'ProfileArchiveObject'))

add_relation_type('seda_clone_of')

add_cube('compound')

