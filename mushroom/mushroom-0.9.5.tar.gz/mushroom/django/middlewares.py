from mushroom.rpc.middleware import Middleware


class CloseOldConnectionsMiddleware(Middleware):

    def process_response(self, request, response):
        from django.db import close_old_connections
        close_old_connections()

    def process_exception(self, request, exception):
        from django.db import close_old_connections
        close_old_connections()
