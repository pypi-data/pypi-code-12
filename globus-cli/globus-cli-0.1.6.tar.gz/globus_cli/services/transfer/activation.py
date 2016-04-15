def autoactivate(client, endpoint_id, if_expires_in=None):
    kwargs = {}
    if if_expires_in is not None:
        kwargs['if_expires_in'] = if_expires_in

    return client.endpoint_autoactivate(endpoint_id, **kwargs)
