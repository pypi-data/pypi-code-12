from appdynamics.agent import pb
from appdynamics.agent.models import transactions

NAMING_SCHEME = {
    'type': 'test-scheme',
    'properties': [
        {'name': 'uri-suffix-scheme', 'value': 'method'},
        {'name': 'suffix-key', 'value': ''},
        {'name': 'delimiter', 'value': '.'},
    ],
}

SIMPLE_CONFIG = {
    'currentVersion': 123456789,
    'agentState': pb.ConfigResponse.REGISTERED,

    'agentIdentity': {
        'nodeID': 123,
        'appID': 234,
        'tierID': 345,
        'controllerGUID': 'abc',
        'accountGUID': 'def',
    },
}

COMPLEX_CONFIG = dict(SIMPLE_CONFIG, **{
    'txConfig': {
        'pythonWeb': {
            'entryPointType': transactions.ENTRY_WSGI,
            'enabled': True,
            'discoveryConfig': {
                'enabled': True,
                'namingScheme': NAMING_SCHEME,
                'excludes': [
                    {
                        'http': {
                            'uri': {
                                'type': pb.StringMatchCondition.STARTS_WITH,
                                'matchStrings': ['/excluded'],
                            },
                        },
                        'http': {
                            'method': pb.PUT,
                            'uri': {
                                'type': pb.StringMatchCondition.IS_IN_LIST,
                                'matchStrings': ['/blacklist0', '/blacklist1'],
                            },
                        },
                    },
                ],
            },
            'customDefinitions': [
                {
                    'id': 1000,
                    'btName': 'Hello to AppD',
                    'priority': 1,
                    'condition': {
                        'http': {
                            'uri': {
                                'type': pb.StringMatchCondition.EQUALS,
                                'matchStrings': ['/hello/appd'],
                            },
                        },
                    },
                },

                {
                    'id': 1001,
                    'btName': 'Hello',
                    'priority': 2,
                    'condition': {
                        'http': {
                            'uri': {
                                'type': pb.StringMatchCondition.STARTS_WITH,
                                'matchStrings': ['/hello'],
                            },
                        },
                    },
                },
            ],
        },
    },

    'txInfo': {
        'registeredBTs': [
            {
                'id': 2000,
                'btInfo': {
                    'entryPointType': transactions.ENTRY_WSGI,
                    'internalName': '/.GET',
                }
            },
        ],
        'blackListedAndExcludedBTs': [
            {
                'entryPointType': transactions.ENTRY_WSGI,
                'internalName': '/foo/bar.GET',
            },
        ],
    },

    'bckInfo': {
        'registeredBackends': [],
        'foreignRegisteredBackends': [],
    },

    'errorConfig': {
        'errorDetection': {
            'pythonErrorThreshold': pb.PY_ERROR,
            'detectErrors': True,
            'markTransactionAsError': True,
        },
        'ignoredExceptions': [
            {
                'classNames': ['AssertionError'],
            },
        ],
        'ignoredMessages': [
            {
                'matchCondition': {
                    'type': pb.StringMatchCondition.STARTS_WITH,
                    'matchStrings': ['IGNORE_ME'],
                },
            },
        ],
    },

    # Stuff that isn't supported, yet.
    'bckConfig': {},
    'callgraphConfig': {},
    'timestampSkew': 0,
    'eumConfig': {},
    'processCallGraphReq': {},
    'dataGatherers': [],
    'dataGathererBTConfig': {},
    'infoPointConfig': {},
})
