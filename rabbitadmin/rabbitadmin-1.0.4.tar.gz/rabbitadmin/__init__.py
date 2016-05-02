from . import http


class Client(object):
    _NO_VALUE = object()
    
    def __init__(self, scheme, host, port, username, password, httpclass = http.HTTP):
        self.connection = httpclass(
            scheme=scheme,
            host=host,
            port=port,
            username=username,
            password=password,
            )
        self.urlquote = httpclass.urlquote
        self.queryencode = httpclass.queryencode

    def __enter__(self):
        self._old_connection = self.connection
        self.connection = self.connection.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self._old_connection.__exit__(type, value, traceback)
        self.connection = self._old_connection
        del self._old_connection


    def get_overview(self):
        '''Various random bits of information that describe the whole system'''

        _query_string = ""
        _api_endpoint = "api/overview{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def put_cluster_name(self, name):
        '''Name identifying this RabbitMQ cluster'''

        _query_string = ""
        _api_endpoint = "api/cluster-name{querystring}".format(querystring=_query_string, )
        _all_data_args = {'name': name}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.PUT(endpoint=_api_endpoint, data=_data_args)

    def delete_cluster_name(self):
        '''Name identifying this RabbitMQ cluster'''

        _query_string = ""
        _api_endpoint = "api/cluster-name{querystring}".format(querystring=_query_string, )
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_cluster_name(self):
        '''Name identifying this RabbitMQ cluster'''

        _query_string = ""
        _api_endpoint = "api/cluster-name{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_nodes(self):
        '''A list of nodes in the RabbitMQ cluster'''

        _query_string = ""
        _api_endpoint = "api/nodes{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_node(self, node):
        '''An individual node in the RabbitMQ cluster'''

        _query_string = ""
        _api_endpoint = "api/nodes/{node}{querystring}".format(querystring=_query_string, node=self.urlquote(node))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_extensions(self):
        '''A list of extensions to the management plugin'''

        _query_string = ""
        _api_endpoint = "api/extensions{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_connections(self):
        '''A list of all open connections'''

        _query_string = ""
        _api_endpoint = "api/connections{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_vhost_connections(self, vhost):
        '''A list of all open connections in a specific vhost'''

        _query_string = ""
        _api_endpoint = "api/vhosts/{vhost}/connections{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def delete_connection(self, connection):
        '''An individual connection. DELETEing it will close the connection'''

        _query_string = ""
        _api_endpoint = "api/connections/{connection}{querystring}".format(querystring=_query_string, connection=self.urlquote(connection))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_connection(self, connection):
        '''An individual connection. DELETEing it will close the connection'''

        _query_string = ""
        _api_endpoint = "api/connections/{connection}{querystring}".format(querystring=_query_string, connection=self.urlquote(connection))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_connection_channels(self, connection):
        '''List of all channels for a given connection'''

        _query_string = ""
        _api_endpoint = "api/connections/{connection}/channels{querystring}".format(querystring=_query_string, connection=self.urlquote(connection))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_channels(self):
        '''A list of all open channels'''

        _query_string = ""
        _api_endpoint = "api/channels{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_vhost_channels(self, vhost):
        '''A list of all open channels in a specific vhost'''

        _query_string = ""
        _api_endpoint = "api/vhosts/{vhost}/channels{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_channel(self, channel):
        '''Details about an individual channel'''

        _query_string = ""
        _api_endpoint = "api/channels/{channel}{querystring}".format(querystring=_query_string, channel=self.urlquote(channel))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_all_consumers(self):
        '''A list of all consumers'''

        _query_string = ""
        _api_endpoint = "api/consumers{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_vhost_consumers(self, vhost):
        '''A list of all consumers in a given virtual host'''

        _query_string = ""
        _api_endpoint = "api/vhosts/{vhost}/consumers{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_all_exchanges(self):
        '''A list of all exchanges'''

        _query_string = ""
        _api_endpoint = "api/exchanges{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_exchanges(self, vhost = '/'):
        '''A list of all exchanges in a given virtual host'''

        _query_string = ""
        _api_endpoint = "api/exchanges/{vhost}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def put_exchange(self, vhost, exchange, type = 'direct', auto_delete = _NO_VALUE, durable = _NO_VALUE, internal = _NO_VALUE, arguments = _NO_VALUE):
        '''An individual exchange'''

        _query_string = ""
        _api_endpoint = "api/exchanges/{vhost}/{exchange}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange))
        _all_data_args = {'type': type, 'auto_delete': auto_delete, 'durable': durable, 'internal': internal, 'arguments': arguments}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.PUT(endpoint=_api_endpoint, data=_data_args)

    def get_exchange(self, vhost, exchange):
        '''An individual exchange'''

        _query_string = ""
        _api_endpoint = "api/exchanges/{vhost}/{exchange}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange))
        return self.connection.GET(endpoint=_api_endpoint)

    def delete_exchange(self, vhost, exchange, if_unused = _NO_VALUE):
        '''An individual exchange'''

        _all_query_args = {'if-unused': if_unused}
        _query_args = {k: v for k, v in _all_query_args.items() if v != self._NO_VALUE}
        if _query_args:
            _query_string = "?" + self.queryencode(_query_args)
        else:
            _query_string = ""
        _api_endpoint = "api/exchanges/{vhost}/{exchange}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def post_exchange(self, vhost, exchange, properties, routing_key, payload, payload_encoding):
        '''Publish a message to a given exchange'''

        _query_string = ""
        _api_endpoint = "api/exchanges/{vhost}/{exchange}/publish{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange))
        _all_data_args = {'properties': properties, 'routing_key': routing_key, 'payload': payload, 'payload_encoding': payload_encoding}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.POST(endpoint=_api_endpoint, data=_data_args)

    def get_binding_from_source_exchange(self, vhost, exchange):
        '''A list of all bindings in which a given exchange is the source'''

        _query_string = ""
        _api_endpoint = "api/exchanges/{vhost}/{exchange}/bindings/source{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_binding_from_destination_exchange(self, vhost, exchange):
        '''A list of all bindings in which a given exchange is the destination'''

        _query_string = ""
        _api_endpoint = "api/exchanges/{vhost}/{exchange}/bindings/destination{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_all_queues(self):
        '''A list of all queues'''

        _query_string = ""
        _api_endpoint = "api/queues{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_queues(self, vhost = '/'):
        '''A list of all queues in a given virtual host'''

        _query_string = ""
        _api_endpoint = "api/queues/{vhost}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def put_queue(self, vhost, queue, auto_delete = _NO_VALUE, durable = _NO_VALUE, arguments = _NO_VALUE, node = _NO_VALUE):
        '''An individual queue'''

        _query_string = ""
        _api_endpoint = "api/queues/{vhost}/{queue}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), queue=self.urlquote(queue))
        _all_data_args = {'auto_delete': auto_delete, 'durable': durable, 'arguments': arguments, 'node': node}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.PUT(endpoint=_api_endpoint, data=_data_args)

    def get_queue(self, vhost, queue):
        '''An individual queue'''

        _query_string = ""
        _api_endpoint = "api/queues/{vhost}/{queue}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), queue=self.urlquote(queue))
        return self.connection.GET(endpoint=_api_endpoint)

    def delete_queue(self, vhost, queue, if_empty = _NO_VALUE, if_unused = _NO_VALUE):
        '''An individual queue'''

        _all_query_args = {'if-empty': if_empty, 'if-unused': if_unused}
        _query_args = {k: v for k, v in _all_query_args.items() if v != self._NO_VALUE}
        if _query_args:
            _query_string = "?" + self.queryencode(_query_args)
        else:
            _query_string = ""
        _api_endpoint = "api/queues/{vhost}/{queue}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), queue=self.urlquote(queue))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_queue_bindings(self, vhost, queue):
        '''A list of all bindings on a given queue'''

        _query_string = ""
        _api_endpoint = "api/queues/{vhost}/{queue}/bindings{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), queue=self.urlquote(queue))
        return self.connection.GET(endpoint=_api_endpoint)

    def delete_queue_contents(self, vhost, queue):
        '''Contents of a queue. DELETE to purge. Note you can't GET this'''

        _query_string = ""
        _api_endpoint = "api/queues/{vhost}/{queue}/contents{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), queue=self.urlquote(queue))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def post_queue_action(self, vhost, queue, action = 'sync'):
        '''Actions that can be taken on a queue'''

        _query_string = ""
        _api_endpoint = "api/queues/{vhost}/{queue}/actions{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), queue=self.urlquote(queue))
        _all_data_args = {'action': action}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.POST(endpoint=_api_endpoint, data=_data_args)

    def post_queue_get(self, vhost, queue, count = 1, requeue = True, encoding = 'auto', truncate = _NO_VALUE):
        '''Get messages from a queue'''

        _query_string = ""
        _api_endpoint = "api/queues/{vhost}/{queue}/get{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), queue=self.urlquote(queue))
        _all_data_args = {'count': count, 'requeue': requeue, 'encoding': encoding, 'truncate': truncate}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.POST(endpoint=_api_endpoint, data=_data_args)

    def get_all_bindings(self):
        '''A list of all bindings'''

        _query_string = ""
        _api_endpoint = "api/bindings{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_bindings(self, vhost = '/'):
        '''A list of all bindings in a given virtual host'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def post_bindings_by_queue(self, vhost, exchange, queue, routing_key = _NO_VALUE, arguments = _NO_VALUE):
        '''A list of all bindings between an exchange and a queue'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}/e/{exchange}/q/{queue}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange), queue=self.urlquote(queue))
        _all_data_args = {'routing_key': routing_key, 'arguments': arguments}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.POST(endpoint=_api_endpoint, data=_data_args)

    def get_bindings_by_queue(self, vhost, exchange, queue):
        '''A list of all bindings between an exchange and a queue'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}/e/{exchange}/q/{queue}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange), queue=self.urlquote(queue))
        return self.connection.GET(endpoint=_api_endpoint)

    def delete_binding_by_queue(self, vhost, exchange, queue, props):
        '''An individual binding between an exchange and a queue'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}/e/{exchange}/q/{queue}/{props}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange), queue=self.urlquote(queue), props=self.urlquote(props))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_binding_by_queue(self, vhost, exchange, queue, props):
        '''An individual binding between an exchange and a queue'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}/e/{exchange}/q/{queue}/{props}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), exchange=self.urlquote(exchange), queue=self.urlquote(queue), props=self.urlquote(props))
        return self.connection.GET(endpoint=_api_endpoint)

    def post_bindings_between_exchanges(self, vhost, source, destination, routing_key = _NO_VALUE, arguments = _NO_VALUE):
        '''A list of all bindings between two exchanges'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}/e/{source}/e/{destination}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), source=self.urlquote(source), destination=self.urlquote(destination))
        _all_data_args = {'routing_key': routing_key, 'arguments': arguments}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.POST(endpoint=_api_endpoint, data=_data_args)

    def get_bindings_between_exchanges(self, vhost, source, destination):
        '''A list of all bindings between two exchanges'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}/e/{source}/e/{destination}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), source=self.urlquote(source), destination=self.urlquote(destination))
        return self.connection.GET(endpoint=_api_endpoint)

    def delete_binding_between_exchanges(self, vhost, source, destination, props):
        '''An individual binding between two exchanges'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}/e/{source}/e/{destination}/{props}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), source=self.urlquote(source), destination=self.urlquote(destination), props=self.urlquote(props))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_binding_between_exchanges(self, vhost, source, destination, props):
        '''An individual binding between two exchanges'''

        _query_string = ""
        _api_endpoint = "api/bindings/{vhost}/e/{source}/e/{destination}/{props}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), source=self.urlquote(source), destination=self.urlquote(destination), props=self.urlquote(props))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_vhosts(self):
        '''A list of all vhosts'''

        _query_string = ""
        _api_endpoint = "api/vhosts{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def put_vhost(self, vhost = '/', tracing = _NO_VALUE):
        '''An individual virtual host'''

        _query_string = ""
        _api_endpoint = "api/vhosts/{vhost}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        _all_data_args = {'tracing': tracing}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.PUT(endpoint=_api_endpoint, data=_data_args)

    def delete_vhost(self, vhost = '/'):
        '''An individual virtual host'''

        _query_string = ""
        _api_endpoint = "api/vhosts/{vhost}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_vhost(self, vhost = '/'):
        '''An individual virtual host'''

        _query_string = ""
        _api_endpoint = "api/vhosts/{vhost}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_vhost_permissions(self, vhost = '/'):
        '''A list of all permissions for a given virtual host'''

        _query_string = ""
        _api_endpoint = "api/vhosts/{vhost}/permissions{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_users(self):
        '''A list of all users'''

        _query_string = ""
        _api_endpoint = "api/users{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def put_user(self, user, tags = '', password = _NO_VALUE, password_hash = _NO_VALUE):
        '''An individual user'''

        _query_string = ""
        _api_endpoint = "api/users/{user}{querystring}".format(querystring=_query_string, user=self.urlquote(user))
        _all_data_args = {'tags': tags, 'password': password, 'password_hash': password_hash}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.PUT(endpoint=_api_endpoint, data=_data_args)

    def delete_user(self, user):
        '''An individual user'''

        _query_string = ""
        _api_endpoint = "api/users/{user}{querystring}".format(querystring=_query_string, user=self.urlquote(user))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_user(self, user):
        '''An individual user'''

        _query_string = ""
        _api_endpoint = "api/users/{user}{querystring}".format(querystring=_query_string, user=self.urlquote(user))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_user_permissions(self, user):
        '''A list of all permissions for a given user'''

        _query_string = ""
        _api_endpoint = "api/users/{user}/permissions{querystring}".format(querystring=_query_string, user=self.urlquote(user))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_whoami(self):
        '''Details of the currently authenticated user'''

        _query_string = ""
        _api_endpoint = "api/whoami{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_all_permissions(self):
        '''A list of all permissions for all users'''

        _query_string = ""
        _api_endpoint = "api/permissions{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def put_user_vhost_permissions(self, vhost, user, configure, write, read):
        '''An individual permission of a user and virtual host'''

        _query_string = ""
        _api_endpoint = "api/permissions/{vhost}/{user}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), user=self.urlquote(user))
        _all_data_args = {'configure': configure, 'write': write, 'read': read}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.PUT(endpoint=_api_endpoint, data=_data_args)

    def delete_user_vhost_permissions(self, vhost, user):
        '''An individual permission of a user and virtual host'''

        _query_string = ""
        _api_endpoint = "api/permissions/{vhost}/{user}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), user=self.urlquote(user))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_user_vhost_permissions(self, vhost, user):
        '''An individual permission of a user and virtual host'''

        _query_string = ""
        _api_endpoint = "api/permissions/{vhost}/{user}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), user=self.urlquote(user))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_all_parameters(self):
        '''A list of all parameters'''

        _query_string = ""
        _api_endpoint = "api/parameters{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_component_parameters(self, component):
        '''A list of all parameters for a given component'''

        _query_string = ""
        _api_endpoint = "api/parameters/{component}{querystring}".format(querystring=_query_string, component=self.urlquote(component))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_vhost_component_parameters(self, component, vhost = '/'):
        '''A list of all parameters for a given component and virtual host'''

        _query_string = ""
        _api_endpoint = "api/parameters/{component}/{vhost}{querystring}".format(querystring=_query_string, component=self.urlquote(component), vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def put_parameter(self, component, vhost, parameter, name, value):
        '''An individual parameter'''

        _query_string = ""
        _api_endpoint = "api/parameters/{component}/{vhost}/{parameter}{querystring}".format(querystring=_query_string, component=self.urlquote(component), vhost=self.urlquote(vhost), parameter=self.urlquote(parameter))
        _all_data_args = {'vhost': vhost, 'component': component, 'name': name, 'value': value}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.PUT(endpoint=_api_endpoint, data=_data_args)

    def delete_parameter(self, component, vhost, parameter):
        '''An individual parameter'''

        _query_string = ""
        _api_endpoint = "api/parameters/{component}/{vhost}/{parameter}{querystring}".format(querystring=_query_string, component=self.urlquote(component), vhost=self.urlquote(vhost), parameter=self.urlquote(parameter))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_parameter(self, component, vhost, parameter):
        '''An individual parameter'''

        _query_string = ""
        _api_endpoint = "api/parameters/{component}/{vhost}/{parameter}{querystring}".format(querystring=_query_string, component=self.urlquote(component), vhost=self.urlquote(vhost), parameter=self.urlquote(parameter))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_all_policies(self):
        '''A list of all policies'''

        _query_string = ""
        _api_endpoint = "api/policies{querystring}".format(querystring=_query_string, )
        return self.connection.GET(endpoint=_api_endpoint)

    def get_policies(self, vhost = '/'):
        '''A list of all policies in a given virtual host'''

        _query_string = ""
        _api_endpoint = "api/policies/{vhost}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)

    def put_policy(self, vhost, policy, pattern, definition, priority = _NO_VALUE, apply_to = _NO_VALUE):
        '''An individual policy'''

        _query_string = ""
        _api_endpoint = "api/policies/{vhost}/{policy}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), policy=self.urlquote(policy))
        _all_data_args = {'pattern': pattern, 'definition': definition, 'priority': priority, 'apply-to': apply_to}
        _data_args = {k: v for k, v in _all_data_args.items() if v != self._NO_VALUE}
        return self.connection.PUT(endpoint=_api_endpoint, data=_data_args)

    def delete_policy(self, vhost, policy):
        '''An individual policy'''

        _query_string = ""
        _api_endpoint = "api/policies/{vhost}/{policy}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), policy=self.urlquote(policy))
        return self.connection.DELETE(endpoint=_api_endpoint)

    def get_policy(self, vhost, policy):
        '''An individual policy'''

        _query_string = ""
        _api_endpoint = "api/policies/{vhost}/{policy}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost), policy=self.urlquote(policy))
        return self.connection.GET(endpoint=_api_endpoint)

    def get_aliveness_test(self, vhost = '/'):
        '''Declares a test queue, then publishes and consumes a message'''

        _query_string = ""
        _api_endpoint = "api/aliveness-test/{vhost}{querystring}".format(querystring=_query_string, vhost=self.urlquote(vhost))
        return self.connection.GET(endpoint=_api_endpoint)
