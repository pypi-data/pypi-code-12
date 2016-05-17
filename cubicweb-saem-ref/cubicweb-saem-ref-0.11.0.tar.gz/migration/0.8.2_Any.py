from itertools import chain
rset1 = rql('Any X,A WHERE X ark A, X cwuri ~="None%", X is IN (Agent, ConceptScheme, Concept)')
rset2 = rql('Any X,A WHERE X ark A, X cwuri ~="%s%%", X is IN (Agent, ConceptScheme, Concept)' % config['base-url'])
for entity in chain(rset1.entities(), rset2.entities()):
    assert entity.ark
    entity.cw_set(cwuri=u'ark:/' + entity.ark)
commit()

rql('SET X in_state S WHERE NOT X in_state Z, X is ET, ET default_workflow WF, WF initial_state S')
commit()
