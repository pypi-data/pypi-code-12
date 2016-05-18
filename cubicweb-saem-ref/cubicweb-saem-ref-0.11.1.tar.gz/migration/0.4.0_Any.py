sync_schema_props_perms('place_address')

add_relation_definition('Agent', 'agent_user', 'CWUser')

kind = cnx.find('AgentKind', name=u'person').one()
for user in find('CWUser').entities():
    if user.login == 'anon':
        continue
    create_entity('Agent', name=user.login, agent_user=user, agent_kind=kind)
commit()

# specialize generic EACInformation
add_entity_type('Mandate')
add_entity_type('LegalStatus')
add_entity_type('Structure')
add_entity_type('History')

for eacinfo in find_entities('EACInformation'):
    if eacinfo.type == u'mandate':
        create_entity('Mandate', term=eacinfo.term,
                      description=eacinfo.description,
                      description_format=eacinfo.description_format,
                      start_date=eacinfo.start_date,
                      end_date=eacinfo.end_date,
                      mandate_agent=eacinfo.eac_information_agent)
    elif eacinfo.type == u'legalStatus':
        create_entity('LegalStatus', term=eacinfo.term,
                      description=eacinfo.description,
                      description_format=eacinfo.description_format,
                      start_date=eacinfo.start_date,
                      end_date=eacinfo.end_date,
                      legal_status_agent=eacinfo.eac_information_agent)
    elif eacinfo.type == u'biogHist':
        create_entity('History', text=eacinfo.description,
                      text_format=eacinfo.description_format,
                      history_agent=eacinfo.eac_information_agent)
    elif eacinfo.type == u'structureOrGenealogy':
        create_entity('Structure', description=eacinfo.description,
                      description_format=eacinfo.description_format,
                      structure_agent=eacinfo.eac_information_agent)

drop_entity_type('EACInformation')
drop_relation_type('eac_information_agent')


# Description changed
sync_schema_props_perms('agent_relationship_from')
sync_schema_props_perms('agent_relationship_to')

sync_schema_props_perms('ExternalUri', syncprops=False)

sync_schema_props_perms('start_date')
sync_schema_props_perms('end_date')


add_cube('prov')
sync_schema_props_perms('Agent')

eac2prov = {"created": u'create',
            "derived": u'create',
            "revised": u'replace',
            "updated": u'modify',
           }

prov_activity_types = schema['Activity'].rdef('type').constraint_by_type('StaticVocabularyConstraint').values

for event in find_entities('MaintenanceEvent'):
    event_type = event.event_type
    if event_type not in prov_activity_types:
        if event_type in eac2prov:
            event_type = eac2prov[event_type]
        else:
            print ('could not find a correspondance for "%s" maintenance event '
                   'in PROV-O terminology, %s will be dropped.' % (event_type, event))
            continue
    assert event_type in prov_activity_types, event_type
    create_entity('Activity', type=event_type,
                  description=event.description,
                  description_format=event.description_format,
                  start=event.datetime,
                  end=event.datetime,
                  associated_with=event.event_agent,
                  generated=event.event_concerns,
                  used=event.event_concerns,
                 )
    commit()

drop_entity_type('MaintenanceEvent')


add_attribute('MirrorEntity', 'error_flag')


for rtype in ('function_agent', 'phone_number', 'place_address', 'place_agent',
              'mandate_agent', 'structure_agent', 'history_agent',
              'resource_relation_agent', 'source_agent'):
    sync_schema_props_perms(rtype, syncperms=False)


add_cube('relationwidget')

# cubicweb-skos had no release before, adding migration steps here instead.
add_relation_type('exact_match')
add_relation_type('close_match')
sync_schema_props_perms()  # too many changes in skos (fti, constraints, etc.)
