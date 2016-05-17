# SEDA profiles now have an ark identifier in the schema (replacing identifier)
add_attribute('SEDAProfile', 'ark')
drop_attribute('SEDAProfile', 'identifier')

# Add an ark identifier to existing SEDA profiles
for profile in rql('SEDAProfile P').entities():
    ark = profile.cw_adapt_to('IARKGenerator').generate_ark()
    profile.cw_set(ark=ark, cwuri=u'ark:/' + ark)
commit()

sync_schema_props_perms('AgentFunction', syncperms=False)

sync_schema_props_perms('seda_transferring_agent', syncperms=False)
sync_schema_props_perms('seda_parent', syncperms=False)


sql("SET TIME ZONE 'Europe/Paris'")

for entity in schema.entities():
    if entity.final:
        continue
    change_attribute_type(entity.type, 'creation_date', 'TZDatetime', ask_confirm=False)
    change_attribute_type(entity.type, 'modification_date', 'TZDatetime', ask_confirm=False)

create_entity('ArchivalRole', name=u'seda-actor', commit=True)

add_attribute('SEDAProfile', 'support_seda_exports')
rql('SET X support_seda_exports "SEDA-0.2.xsd, SEDA-1.0.xsd"')
commit()

profile_wf = get_workflow_for('SEDAProfile')
publish = profile_wf.transition_by_name('publish')
publish.set_permissions(conditions=('U in_group G, G name IN ("users", "managers"),'
                                    'X support_seda_exports ~= "%SEDA-0.2%"',),
                        reset=True)
commit()

# 0.8 migration missed some permission changes
sync_schema_props_perms(syncprops=False)

# New relation replace between profiles
add_relation_type('seda_replace')

for stmt in repo.system_source.dbhelper.sql_create_sequence('ext_ark_count').split(';'):
    if stmt:
        sql(stmt)
