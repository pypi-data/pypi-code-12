add_entity_type('AgentRelation')

drop_relation_type('acted_on_behalf_of')

sync_schema_props_perms('Agent')

rename_attribute('Agent', 'identifier', 'isni')

add_entity_type('AgentPlace')

for a_eid, p_aeid in rql('Any X,A WHERE X postal_address A'):
    create_entity('AgentPlace', place_agent=a_eid, place_address=p_eid)
commit()

for agentkind in find_entities('AgentKind'):
    agentkind.cw_set(cwuri='agentkind/' + agentkind.name)
commit()


add_entity_type('AgentFunction')
for aeid, function in rql('Any X,F WHERE EXISTS(X function F), X is Agent').rows:
    create_entity('AgentFunction', name=function, function_agent=aeid)
commit()

add_entity_type('EACResourceRelation')

add_relation_type('equivalent_concept')

add_entity_type('EACSource')
