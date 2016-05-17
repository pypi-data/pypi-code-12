from __future__ import print_function

from os.path import join, dirname
from functools import partial

from logilab.database.fti import normalize

_sql = partial(sql, ask_confirm=False)

_sql('ALTER TABLE words ADD COLUMN normalized_word VARCHAR(100)')
for word, in _sql('SELECT DISTINCT word FROM words', ask_confirm=False):
    normalized_word = normalize(word)
    _sql('UPDATE words SET normalized_word=%(normalized_word)s WHERE word=%(word)s',
        {'word': word, 'normalized_word': normalized_word})
_sql('ALTER TABLE words ALTER COLUMN normalized_word SET NOT NULL')
commit(ask_confirm=False)

add_entity_type('GeneralContext')

sync_schema_props_perms('contact_point')

for etype in ('AssociationRelation', 'ChronologicalRelation',
              'HierarchicalRelation', 'EACResourceRelation', 'EACSource'):
    add_attribute(etype, 'xml_wrap')


for etype in ('History', 'AgentFunction', 'LegalStatus', 'AgentPlace'):
    add_relation_definition(etype, 'has_citation', 'Citation')

# Import concept scheme for appraisal rule durations
process_script(join(dirname(__file__), 'create_seda_schemes.py'))

add_relation_definition('SEDAAppraisalRuleDuration', 'seda_appraisal_rule_duration_value', 'Concept')

_rql = partial(rql, ask_confirm=False)

label_to_concept = {}  # label value --> (value is valid, corresponding concept)
default_rset = _rql('Any C WHERE L label_of C, L label "P10Y"')
for duration, value in _rql('Any D,V WHERE D is SEDAAppraisalRuleDuration, D value V'):
    if value is None:
        continue
    value = value.upper()
    concept = None
    if value in label_to_concept:
        concept = label_to_concept[value][1]
        if not label_to_concept[value][0]:
            print('SEDA appraisal rule duration value (%s, %s) does not match any known concept' % (
                duration, value))
    else:
        rset = _rql(
            'Any C WHERE L label_of C, L label %(duration)s, C in_scheme CS, CS scheme_relation SR, '
            '   SR name "seda_appraisal_rule_duration"', {'duration': value})
        if rset:
            label_to_concept[value] = (True, rset[0][0])
        else:
            print('SEDA appraisal rule duration value (%s, %s) does not match any known concept' % (
                duration, value))
            rset = default_rset
            label_to_concept[value] = (False, rset[0][0])
        concept = rset[0][0]
    _rql('SET RD seda_appraisal_rule_duration_value C WHERE RD eid %(rd)s, C eid %(c)s',
         {'rd': duration, 'c': concept})
commit()

drop_attribute('SEDAAppraisalRuleDuration', 'value')

with dropped_constraints('Agent', 'authority', droprequired=True):
    add_entity_type('Authority')
    add_entity_type('ArkNameAssigningAuthority')
    naa = create_entity('ArkNameAssigningAuthority', who=u'SAEMREF-TEST', what=0)
    org = create_entity('Authority', name=u'Default authority', ark_naa=naa)
    for agent in rql('Agent X').entities():
        agent.cw_set(authority=org)
commit()

sync_schema_props_perms('agent_kind', syncprops=False)

add_cube('oaipmh')
