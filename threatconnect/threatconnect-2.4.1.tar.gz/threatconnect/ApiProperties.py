""" ApiProperties """


#
# g_properties
#
def g_properties(group_uri):
    """ """
    properties = {
        'add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri,
        },
        'association_groups': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '/{0}/groups',  # group id
        },
        'association_group_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/groups/{1}/{2}',  # group id, group type, group id
        },
        'association_group_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/groups/{1}/{2}',  # group id, group type, group id
        },
        'association_indicators': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '/{0}/indicators',  # group id
        },
        'association_indicator_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/{0}/{1}/groups/' + group_uri + '/{2}',  # indicator type, indicator_value
        },
        'association_indicator_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/{0}/{1}/groups/' + group_uri + '/{2}',  # indicator type, indicator_value
        },
        'association_tasks': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '/{0}/tasks',  # group id
        },
        'association_task_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/tasks/{1}',  # group id, task id
        },
        'association_task_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/tasks/{1}',  # group id, task id
        },
        'association_victims': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '/{0}/victims',  # group id
        },
        'association_victim_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/victims/{1}',  # group id, victim id
        },
        'association_victim_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/victims/{1}',  # group id, victim id
        },
        'attributes': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/attributes',  # group id
        },
        'attribute_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/attributes',  # group id
        },
        'attribute_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/attributes/{1}',  # group id, attribute id
        },
        'attribute_update': {
            'http_method': 'PUT',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/attributes/{1}',  # group id, attribute id
        },
        'base': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '',
        },
        'delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}',  # group id
        },
        'document_download': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/documents/{0}/download',  # document id
        },
        'document_upload': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/documents/{0}/upload',  # document id
        },
        'filters': [
            'add_adversary_id',
            'add_email_id',
            'add_document_id',
            'add_id',
            'add_incident_id',
            'add_indicator',
            'add_security_label',
            'add_signature_id',
            'add_threat_id',
            'add_tag',
            'add_task_id',
            'add_victim_id',
            # post filters
            'add_pf_name',
            'add_pf_date_added',
            'add_pf_file_type',
        ],
        'groups': {
            'http_method': 'GET',
            'owner_allowed': False,
            'pagination': True,
            'uri': '/v2/groups/{0}/{1}/groups/' + group_uri  # group type, group id
        },
        'id': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}',  # group id
        },
        'indicators': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/indicators/{0}/{1}/groups/' + group_uri,  # group id
        },
        'signature_download': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/signatures/{0}/download',  # signature id
        },
        'signature_upload': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/signatures/{0}/upload',  # signature id
        },
        'security_label_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '/{0}/securityLabels/{1}',  # group id, security label
        },
        'security_label_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '/{0}/securityLabels/{1}',  # group id, security label
        },
        'security_label_load': {
            'http_method': 'GET',
            'owner_allowed': False,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '/{0}/securityLabels',  # group id
        },
        'security_labels': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/securityLabels/{0}/groups/' + group_uri  # security labels
        },
        'tag_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/tags/{1}',  # group id, security label
        },
        'tag_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}/tags/{1}',  # group id, security label
        },
        'tags': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/tags/{0}/groups/' + group_uri,  # tag name
        },
        'tags_load': {
            'http_method': 'GET',
            'owner_allowed': False,
            'pagination': True,
            'uri': '/v2/groups/' + group_uri + '/{0}/tags',  # group id
        },
        'tasks': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/tasks/{0}/groups/' + group_uri,  # task id
        },
        'update': {
            'http_method': 'PUT',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/groups/' + group_uri + '/{0}',  # group id
        },
        'victims': {
            'http_method': 'GET',
            'owner_allowed': False,
            'pagination': True,
            'uri': '/v2/victims/{0}/groups/' + group_uri  # victim id
        },
    }

    return properties


#
# i_properties
#
def i_properties(indicator_uri):
    """ """
    properties = {
        'add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri,
        },
        'association_groups': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/groups',  # indicator value
        },
        'association_group_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/groups/{1}/{2}',  # indicator value, group type, group id
        },
        'association_group_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/groups/{1}/{2}',  # indicator value, group type, group id
        },
        'association_indicators': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/indicators',  # indicator value
        },
        'association_tasks': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/tasks',  # indicator value
        },
        'association_task_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/tasks/{1}',  # indicator value, task id
        },
        'association_task_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/tasks/{1}/{2}',  # indicator value, tasks id
        },
        'association_victims': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/victims',  # indicator value
        },
        'attributes': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/attributes',  # indicator value
        },
        'attribute_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/attributes',  # indicator value
        },
        'attribute_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/attributes/{1}',  # indicator value, attribute id
        },
        'attribute_update': {
            'http_method': 'PUT',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/attributes/{1}',  # indicator value, attribute id
        },
        'base': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '',
        },
        'delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}',  # indicator value
        },
        'filters': [
            'add_adversary_id',
            'add_document_id',
            'add_email_id',
            'add_incident_id',
            'add_indicator',
            'add_security_label',
            # 'add_signature_id',
            'add_tag',
            'add_task_id',
            'add_threat_id',
            'add_victim_id',
            # post filters
            'add_pf_attribute',
            'add_pf_confidence',
            'add_pf_date_added',
            'add_pf_last_modified',
            'add_pf_rating',
            'add_pf_tag',
            'add_pf_threat_assess_confidence',
            'add_pf_threat_assess_rating',
            'add_pf_type'],
        'groups': {
            'http_method': 'GET',
            'owner_allowed': False,
            'pagination': True,
            'uri': '/v2/groups/{0}/{1}/indicators/' + indicator_uri  # group type, group value
        },
        'indicator': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}',  # indicator value
        },
        'id': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}',  # indicator value
        },
        'security_label_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/securityLabels/{1}',  # indicator value, security label
        },
        'security_label_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/securityLabels/{1}',  # indicator value, security label
        },
        'security_label_load': {
            'http_method': 'GET',
            'owner_allowed': False,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/securityLabels',  # indicator value
        },
        'security_labels': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/securityLabels/{0}/indicators/' + indicator_uri  # security labels
        },
        'tag_add': {
            'http_method': 'POST',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/tags/{1}',  # indicator value, security label
        },
        'tag_delete': {
            'http_method': 'DELETE',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/tags/{1}',  # indicator value, security label
        },
        'tags': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/tags/{0}/indicators/' + indicator_uri,  # tag name
        },
        'tags_load': {
            'http_method': 'GET',
            'owner_allowed': False,
            'pagination': True,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}/tags',  # indicator value
        },
        'tasks': {
            'http_method': 'GET',
            'owner_allowed': True,
            'pagination': True,
            'uri': '/v2/tasks/{0}/indicators/' + indicator_uri,  # task id
        },
        'update': {
            'http_method': 'PUT',
            'owner_allowed': True,
            'pagination': False,
            'uri': '/v2/indicators/' + indicator_uri + '/{0}',  # indicator value
        },
        'victims': {
            'http_method': 'GET',
            'owner_allowed': False,
            'pagination': True,
            'uri': '/v2/victims/{0}/indicators/' + indicator_uri  # victim id
        },
    }

    if indicator_uri == 'files':
        properties['file_occurrence'] = {
            'http_method': 'GET',
            'uri': '/v2/indicators/files/{0}/fileOccurrences/{1}',  # hash, occurrence id
            'owner_allowed': True,
            'pagination': False
        }

        properties['file_occurrence_add'] = {
            'http_method': 'POST',
            'uri': '/v2/indicators/files/{0}/fileOccurrences',  # hash
            'owner_allowed': True,
            'pagination': False,
        }

        properties['file_occurrence_delete'] = {
            'http_method': 'DELETE',
            'uri': '/v2/indicators/files/{0}/fileOccurrences/{1}',  # hash, occurrence id
            'owner_allowed': True,
            'pagination': False,
        }

        properties['file_occurrence_update'] = {
            'http_method': 'PUT',
            'uri': '/v2/indicators/files/{0}/fileOccurrences/{1}',  # hash, occurrence id
            'owner_allowed': True,
            'pagination': False,
        }

        properties['file_occurrences'] = {
            'http_method': 'GET',
            'uri': '/v2/indicators/files/{0}/fileOccurrences',  # hash
            'owner_allowed': True,
            'pagination': False,
        }

    if indicator_uri == 'hosts':
        properties['dns_resolution'] = {
            'http_method': 'GET',
            'uri': '/v2/indicators/hosts/{0}/dnsResolutions',  # indicator value
            'owner_allowed': True,
            'pagination': True,
        }

    return properties


#
# groups
#
groups_properties = {
    'base': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/groups',
    },
    'groups': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/groups/{0}/{1}/groups',  # group type, group value
    },
    'filters': [
        'add_adversary_id',
        'add_document_id',
        'add_email_id',
        'add_incident_id',
        'add_indicator',
        'add_security_label',
        'add_signature_id',
        'add_task_id',
        'add_threat_id',
        'add_tag',
        'add_tasks',
        'add_victim_id',
        # post filters
        'add_pf_name',
        'add_pf_date_added',
        'add_pf_type'
    ],
    'indicators': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/indicators/{0}/{1}/groups',  # indicator type, indicator value
    },
    'tags': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/tags/{0}/groups',  # tag name
    },
    'tasks': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/tasks/{0}/groups',  # task id
    },
    'security_labels': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/securityLabels/{0}/groups',  # security labels
    },
    'victims': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/victims/{0}/groups',  # victim id
    },
}


#
# indicators
#
indicators_properties = {
    'base': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/indicators',
    },
    'bulk': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/indicators/bulk/json',
    },
    'groups': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/groups/{0}/{1}/indicators',  # group type, group value
    },
    'filters': [
        'add_adversary_id',
        'add_email_id',
        'add_incident_id',
        'add_indicator',
        'add_security_label',
        'add_signature_id',
        'add_tag',
        'add_task_id',
        'add_threat_id',
        'add_victim_id',
        'add_pf_attribute',
        'add_pf_confidence',
        'add_pf_date_added',
        'add_pf_last_modified',
        'add_pf_rating',
        'add_pf_tag',
        'add_pf_threat_assess_confidence',
        'add_pf_threat_assess_rating',
        'add_pf_type'],
    'indicator': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/indicators/{0}/{1}',  # indicator type, indicator value
    },
    'tags': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/tags/{0}/indicators',  # tag name
    },
    'tasks': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/tasks/{0}/indicators',  # task id
    },
    'security_labels': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/securityLabels/{0}/indicators',  # security labels
    },
    'victims': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/victims/{0}/indicators',  # victim id
    },
}


#
# owners
#
owners_properties = {
    'base': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/owners',
    },
    'filters': [
        'add_id',
        'add_indicator',
        'add_pf_name',
        'add_pf_type',
    ],
    'id': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/owners/{0}',  # owner id
    },
    'indicators': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/indicators/{0}/{1}/owners',  # indicator type, indicator value
    },
    'individual_metrics': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/owners/{0}/metrics',
    },
    'members': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/owners/mine/members',
    },
    'metrics': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/owners/metrics',
    },
    'mine': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/owners/mine',
    },
}

#
# tasks
#
tasks_properties = {
    'add': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks',
    },
    'assignee_add': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/assignees/{1}',  # task id, assignee account
    },
    'assignee_delete': {
        'http_method': 'DELETE',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/assignees/{1}',  # task id, assignee account
    },
    'association_groups': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/tasks/{0}/groups',  # task id
    },
    'association_group_add': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/groups/{1}/{2}',  # task id, group type, group id
    },
    'association_group_delete': {
        'http_method': 'DELETE',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/groups/{1}/{2}',  # task id, group type, group id
    },
    'association_indicators': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/tasks/{0}/indicators',  # task id
    },
    'association_indicator_add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': False,
        # 'uri': '/v2/indicators/{0}/{1}/tasks/{2}',  # indicator type, indicator_value, task_id
        'uri': '/v2/tasks/{0}/indicators/{1}/{2}',  # task id, indicator type, indicator_value
    },
    'association_indicator_delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': False,
        # 'uri': '/v2/indicators/{0}/{1}/tasks/{2}',  # indicator type, indicator_value, task_id
        'uri': '/v2/tasks/{0}/indicators/{1}/{2}',  # task id, indicator type, indicator_value
    },
    'association_victims': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/tasks/{0}/victims',  # task id
    },
    'association_victim_add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/tasks/{0}/victims/{1}',  # task id, victim id
    },
    'association_victim_delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/tasks/{0}/victims/{1}',  # task id, victim id
    },
    'attributes': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/attributes',  # task id
    },
    'attribute_add': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/attributes',  # task id
    },
    'attribute_delete': {
        'http_method': 'DELETE',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/attributes/{1}',  # tasks id, attribute id
    },
    'attribute_update': {
        'http_method': 'PUT',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/attributes/{1}',  # task id, attribute id
    },
    'base': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/tasks',
    },
    'escalatee_add': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/escalatees/{1}',  # task id, assignee account
    },
    'escalatee_delete': {
        'http_method': 'DELETE',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/escalatees/{1}',  # task id, assignee account
    },
    'delete': {
        'http_method': 'DELETE',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}',
    },
    'groups': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/groups/{0}/{1}/tasks',  # group type, group value
    },
    'filters': [
        'add_adversary_id',
        'add_document_id',
        'add_email_id',
        'add_id',
        'add_incident_id',
        'add_indicator',
        'add_security_label',
        'add_signature_id',
        'add_threat_id',
        'add_tag',
        'add_victim_id',
        # post filters
        'add_pf_attribute',
        'add_pf_name',
        'add_pf_date_added',
    ],
    'id': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}',  # task id
    },
    'indicators': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/indicators/{0}/{1}/tasks',  # indicator type, indicator value
    },
    'security_label_add': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/tasks/{0}/securityLabels/{1}',  # task id, security label
    },
    'security_label_delete': {
        'http_method': 'DELETE',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/tasks/{0}/securityLabels/{1}',  # task id, security label
    },
    'security_label_load': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/tasks/{0}/securityLabels',  # task id
    },
    'security_labels': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/securityLabels/{0}/tasks',  # security labels
    },
    'tag_add': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/tags/{1}',  # task id, security label
    },
    'tag_delete': {
        'http_method': 'DELETE',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}/tags/{1}',  # task id, security label
    },
    'tags': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/tags/{0}/tasks',  # tag name
    },
    'tags_load': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/tasks/{0}/tags',  # tasks id
    },
    'update': {
        'http_method': 'PUT',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/tasks/{0}',  # task id
    },
    'victims': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/victims/{0}/tasks',  # victim id
    },
}

#
# victims
#
victims_properties = {
    'add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims',
    },
    'assets': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/victimAssets',  # victim id
    },
    'asset_add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/victimAssets/{1}',  # victim id, asset type
    },
    'asset_delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/victimAssets/{1}/{2}',  # victim id, asset type, asset id
    },
    'asset_update': {
        'http_method': 'PUT',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/victimAssets/{1}/{2}',  # victim id, asset type, asset id
    },
    'association_groups': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/victims/{0}/groups',  # victim id
    },
    'association_group_add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/groups/{1}/{2}',  # victim id, group type, group id
    },
    'association_group_delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/groups/{1}/{2}',  # victim id, group type, group id
    },
    'association_indicators': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/victims/{0}/indicators',  # victim id
    },
    'association_tasks': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/victims/{0}/tasks',  # victim id
    },
    'association_task_add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/tasks/{1}',  # victim id, task id
    },
    'association_task_delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/task/{1}',  # victim id, tasks id
    },
    'attributes': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/attributes',  # victim id
    },
    'attribute_add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/attributes',  # victim id
    },
    'attribute_delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/attributes/{1}',  # victim id, attribute id
    },
    'attribute_update': {
        'http_method': 'PUT',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/attributes/{1}',  # victim id, attribute id
    },
    'base': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/victims',
    },
    'delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}',
    },
    'groups': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/groups/{0}/{1}/victims',  # group type, group id
    },
    'filters': [
        'add_adversary_id',
        'add_document_id',
        'add_email_id',
        'add_id',
        'add_incident_id',
        'add_indicator',
        'add_signature_id',
        'add_security_label',
        'add_tag',
        'add_task_id',
        'add_threat_id',
        # post filters
        'add_pf_attribute',
        'add_pf_date_added',
        'add_pf_name',
        'add_pf_type',
    ],
    'id': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}',  # victim id
    },
    'indicators': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/indicators/{0}/{1}/victims',  # indicator type, indicator value
    },
    'security_label_add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/victims/{0}/securityLabels/{1}',  # victim id, security label
    },
    'security_label_delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/victims/{0}/securityLabels/{1}',  # victim id, security label
    },
    'security_label_load': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/victims/{0}/securityLabels',  # victim id
    },
    'security_labels': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/securityLabels/{0}/victims',  # security labels
    },
    'tag_add': {
        'http_method': 'POST',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/tags/{1}',  # victim id, security label
    },
    'tag_delete': {
        'http_method': 'DELETE',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}/tags/{1}',  # victim id, security label
    },
    'tags': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/tags/{0}/victims',  # tag name
    },
    'tags_load': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': True,
        'uri': '/v2/victims/{0}/tags',  # victim id
    },
    'tasks': {
        'http_method': 'GET',
        'owner_allowed': True,
        'pagination': True,
        'uri': '/v2/tasks/{0}/victims',  # task id
    },
    'update': {
        'http_method': 'PUT',
        'owner_allowed': True,
        'pagination': False,
        'uri': '/v2/victims/{0}',
    },
}

#
# batch jobs
#
batch_job_properties = {
    'add': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/batch',
    },
    'id': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/batch/{0}',  # batch id
    },
    'batch_error_download': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/batch/{0}/errors',  # batch id
    },
    'batch_job_upload': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '/v2/batch/{0}',  # batch id
    },
    'filters': [
        'add_id'
    ]
}

#
# attributes
#
attribute_properties = {
    'load_security_labels': {
        'http_method': 'GET',
        'owner_allowed': False,
        'pagination': False,
        'uri': '{0}/attributes/{1}/securityLabels'
    },
    'delete_security_label': {
        'http_method': 'DELETE',
        'owner_allowed': False,
        'pagination': False,
        'uri': '{0}/attributes/{1}/securityLabels/{2}'
    },
    'add_security_label': {
        'http_method': 'POST',
        'owner_allowed': False,
        'pagination': False,
        'uri': '{0}/attributes/{1}/securityLabels/{2}'
    },
}

api_properties = {
    'ADDRESSES': {
        'properties': i_properties('addresses'),
        'resource_key':  'address',
        'uri_attribute':  'addresses',
    },
    'ADVERSARIES': {
        'properties': g_properties('adversaries'),
        'resource_key':  'adversary',
        'uri_attribute':  'adversaries',
    },
    'DOCUMENTS': {
        'properties': g_properties('documents'),
        'resource_key':  'document',
        'uri_attribute':  'documents',
    },
    'EMAIL_ADDRESSES': {
        'properties': i_properties('emailAddresses'),
        'resource_key':  'emailAddress',
        'uri_attribute':  'emailAddresses',
    },
    'EMAILS': {
        'properties': g_properties('emails'),
        'resource_key':  'email',
        'uri_attribute':  'emails',
    },
    'FILES': {
        'properties': i_properties('files'),
        'resource_key':  'file',
        'uri_attribute':  'files',
    },
    'GROUPS': {
        'properties': groups_properties,
        'resource_key':  'group',
        'uri_attribute':  'groups',
    },
    'HOSTS': {
        'properties': i_properties('hosts'),
        'resource_key':  'host',
        'uri_attribute':  'hosts',
    },
    'INCIDENTS': {
        'properties': g_properties('incidents'),
        'resource_key':  'incident',
        'uri_attribute':  'incidents',
    },
    'INDICATORS': {
        'properties': indicators_properties,
        'resource_key':  'indicator',
        'uri_attribute':  'indicators',
    },
    'OWNERS': {
        'properties': owners_properties,
        'resource_key':  'owner',
        'uri_attribute':  'owners',
    },
    # 'SECURITY_LABELS': {
    #     'properties': 'security_labels_properties',
    #     'resource_key':  'securityLabel',
    #     'uri_attribute':  'securityLabels',
    # },
    # 'TAGS': {
    #     'properties': 'tags_properties',
    #     'resource_key':  'tag',
    #     'uri_attribute':  'tags',
    # },
    'SIGNATURES': {
        'properties': g_properties('signatures'),
        'resource_key':  'signature',
        'uri_attribute':  'signatures',
    },
    'TASKS': {
        'properties': tasks_properties,
        'resource_key':  'task',
        'uri_attribute':  'tasks',
    },
    'THREATS': {
        'properties': g_properties('threats'),
        'resource_key':  'threat',
        'uri_attribute':  'threats',
    },
    'URLS': {
        'properties': i_properties('urls'),
        'resource_key':  'url',
        'uri_attribute':  'urls',
    },
    'VICTIMS': {
        'properties': victims_properties,
        'resource_key':  'victim',
        'uri_attribute':  'victims',
    },
    'BATCH_JOBS': {
        'properties': batch_job_properties,
        'resource_key': 'batchJob',
        'uri_attribute': 'batchJobs'
    },
    'ATTRIBUTES': {
        'properties': attribute_properties,
        'resource_key': 'attribute',
        'uri_attribute': 'attributes'
    }
}
