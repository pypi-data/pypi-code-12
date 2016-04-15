# -*- coding: utf-8 -*-
"""
rio_client.transport.base
~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class Transport(object):
    """Requests Transport.

    Emit actions via awesome `requests`.
    """

    def __init__(self, context):
        self.context = context

    def get_emit_api(self, action):
        """Build emit api."""
        args = {'action': action}
        args.update(self.context)
        return (
            '%(scheme)s://%(sender)s:%(token)s@%(domain)s:%(port)d'
            '/event/%(project)s/emit/%(action)s' % args
        )

    def emit(self, action, payload):
        """Emit action with payload.

        :return: a dict with event_uuid, task_id, and is_success.
        """
        raise NotImplementedError

    def retry(self, times):
        """Define what exception to be caught and how many times to retry.

        :return: Retry object.
        """
        raise NotImplementedError
