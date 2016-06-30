from rakam.connection import RakamConnection


class RakamClient(object):
    """
        Client class used for calling endpoints on rakam server.
    """
    def __init__(self, rakam_url, rakam_credentials=None, connection_options=None):
        connection_kwargs = {}
        if rakam_credentials is not None:
            connection_kwargs['rakam_credentials'] = rakam_credentials

        if connection_options is not None:
            connection_kwargs['options'] = connection_options

        self.connection = RakamConnection(rakam_url, **connection_kwargs)

    def send_bulk_events(self, events):
        return self.connection.send_bulk_event(events)

    def execute_sql(self, query, timeout=None):
        return self.connection.execute_sql(query, timeout=timeout)
