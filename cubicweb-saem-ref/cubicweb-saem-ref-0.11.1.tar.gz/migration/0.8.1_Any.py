from cubes.saem_ref import workflows


for etype in ('Agent', 'ConceptScheme', 'SEDAProfile'):
    make_workflowable(etype)
    workflows.define_publication_workflow(add_workflow, etype)
    rql('SET X in_state ST WHERE X is {etype}, ST name "draft", ST state_of W, '
        'W workflow_of ET, ET name "{etype}"'.format(etype=etype))
    commit()
    sync_schema_props_perms(etype)

sync_schema_props_perms('phone_number', syncperms=False)
sync_schema_props_perms('postal_address', syncperms=False)

sync_schema_props_perms('seda_character_set_code', syncperms=False)
sync_schema_props_perms('seda_document_type_code', syncperms=False)
sync_schema_props_perms('seda_file_type_code', syncperms=False)


for agent in rql('Any X,A WHERE X is Agent, X ark A, NOT X cwuri ~= "%ark:%"').entities():
    agent.cw_set(cwuri=agent.cw_adapt_to('IARKGenerator').build_url(agent.ark))
commit()


add_relation_type('archival_agent')
add_relation_type('related_concept_scheme')

rql('SET X archival_agent Y WHERE P seda_transferring_agent X, P seda_archival_agent Y')
drop_relation_type('seda_archival_agent')

for agent in rql('Any X WHERE X is Agent, X archival_role AR, AR name "deposit", NOT X archival_agent Y').entities():
    msg = 'You should add an archival agent to agent %s (%s)' % (agent.name, agent.absolute_url())
    print msg.encode('utf-8')
