# -*- coding: utf-8 -*-

from requests.structures import LookupDict

_operators = {

    'eq': ('eq','equals'),
    'contains': ('contains',),
    'exists': ('exists',),
    'not_exists': ('not_exists',),
}

operators = LookupDict(name='validation operations')

for (operator, titles) in list(_operators.items()):
    for title in titles:
        setattr(operators, title, operator)
        if not title.startswith('\\'):
            setattr(operators, title.upper(), operator)
