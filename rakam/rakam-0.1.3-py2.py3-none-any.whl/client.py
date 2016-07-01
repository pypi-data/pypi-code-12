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
        return self.connection.send_bulk_events(events)

    def commit_bulk_events(self, timeout=None, raise_on_read_timeout=False):
        return self.connection.commit_bulk_events(timeout=timeout, raise_on_read_timeout=raise_on_read_timeout)

    def execute_sql(self, query, timeout=None):
        return self.connection.execute_sql(query, timeout=timeout)
