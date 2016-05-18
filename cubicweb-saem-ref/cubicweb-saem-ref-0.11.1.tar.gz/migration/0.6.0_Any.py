add_attribute('SEDAAppraisalRule', 'user_cardinality')

add_entity_type('AssociationRelation')
add_entity_type('ChronologicalRelation')
add_entity_type('HierarchicalRelation')

for entity in find_entities('AgentRelation'):
    etype, rtype_from, rtype_to = {
        'association': ('AssociationRelation', 'association_from',
                        'association_to'),
        'chronological': ('ChronologicalRelation', 'chronological_predecessor',
                          'chronological_successor'),
        'hierarchical': ('HierarchicalRelation', 'hierarchical_parent',
                         'hierarchical_child'),
    }[entity.relationship]
    kwargs = {rtype_from: entity.agent_relationship_from,
              rtype_to: entity.agent_relationship_to}
    create_entity(etype, description=entity.description,
                  description_format=entity.description_format,
                  **kwargs)

drop_entity_type('AgentRelation')

add_relation_type('contact_point')

drop_attribute('SEDAKeyword', 'value')
add_relation_definition('SEDAKeyword', 'seda_keyword_value', 'Concept')
rql('DELETE SEDAKeyword K WHERE NOT K seda_keyword_scheme S')
commit()
sync_schema_props_perms('seda_keyword_scheme')
