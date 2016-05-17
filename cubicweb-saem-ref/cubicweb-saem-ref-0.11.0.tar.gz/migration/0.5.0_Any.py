from urlparse import urlparse, urlunparse

add_relation_type('scheme_relation')
for etype in ('SEDAProfile', 'ProfileArchive', 'ProfileDocument', 'ProfileArchiveObject',
              'SEDAAppraisalRule', 'SEDAAppraisalRuleDuration', 'SEDAAppraisalRuleCode',
              'SEDAContentDescription', 'SEDAAccessRestrictionCode', 'SEDAKeyword',
              'SEDAName', 'SEDADescription', 'SEDADescriptionLevel', 'SEDADate'):
    add_entity_type(etype)

from os.path import join, dirname
process_script(join(dirname(__file__), 'create_seda_schemes.py'))

sync_schema_props_perms('MirrorEntity')
for agent_mirror in rql('Any X,ID WHERE X extid ID, X mirror_of A, A is Agent').entities():
    agent_mirror.cw_set(extid='Agent ' + agent_mirror.extid)
commit()

add_attribute('AsalaeConnector', 'url')
add_attribute('AsalaeConnector', 'password')
sync_schema_props_perms('AsalaeConnector')
add_attribute('AlfrescoConnector', 'sedaprofiles_node')

for alf_connector in find_entities('AlfrescoConnector'):
    if alf_connector.port != 80:
        parsed = list(urlparse(alf_connector.url))
        parsed[1] += ':%d' % alf_connector.port
        url = urlunparse(parsed)
        alf_connector.cw_set(url=url)
        commit()
drop_attribute('AlfrescoConnector', 'port')
