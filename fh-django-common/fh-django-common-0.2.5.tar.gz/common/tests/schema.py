pattern_date = '^\d{4}-\d{2}-\d{2}$'
pattern_datetime = '^\d{4}-\d{2}-\d{2}T\d{2}\:\d{2}\:\d{2}.\d{1,6}Z$'
pattern_phone = '^\+\d{1,2}\d{3}\d{3}\d{4}$'
pattern_email = '^.+@.+\..+$'
pattern_url = '^((https?|ftp)://|www\.)[^\s/$.?#].[^\s]*$'

HTTP_400 = {
    'type': 'object'
}

HTTP_404 = {
    'type': 'object'
}

HTTP_200_LIST = {
    'type': 'object',
    'required': ['next', 'previous', 'count', 'results'],
    'properties': {
        'next': {'type': ['string', 'null']},
        'previous': {'type': ['string', 'null']},
        'count': {'type': 'number'},
        'results': {'type': 'array'},
    },
    'additionalProperties': False
}