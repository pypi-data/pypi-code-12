"""Collection of constants fo the ``server_guardian`` app."""


# keep this in sync with server_guardian_api.constants
SERVER_STATUS = {  # pragma: no cover
    'OK': 'OK',
    'WARNING': 'WARNING',
    'DANGER': 'DANGER',
}

SERVER_STATUS_CHOICES = (  # pragma: no cover
    ('OK', SERVER_STATUS['OK']),
    ('WARNING', SERVER_STATUS['WARNING']),
    ('DANGER', SERVER_STATUS['DANGER']),
)

ERROR_STATUS = [SERVER_STATUS['WARNING'], SERVER_STATUS['DANGER']]  # pragma: no cover  # NOQA

HTML_STATUS_FALLBACK = [{  # pragma: no cover
    'label': 'json_error',
    'status': SERVER_STATUS['DANGER'],
    'info': 'JSON response could not be decoded.'
}]
