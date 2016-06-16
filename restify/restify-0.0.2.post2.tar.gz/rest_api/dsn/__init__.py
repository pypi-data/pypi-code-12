from rest_api.dsn import base, sentry


DSN_HANDLERS = {
    'base'      : base.BaseDSNDriver,
    'sentry'    : sentry.SentryDSNDriver,
}


def load_dsn(name):

    if name not in DSN_HANDLERS:
        return None

    return DSN_HANDLERS[name]
