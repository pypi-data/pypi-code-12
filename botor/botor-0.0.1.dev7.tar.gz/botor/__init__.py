from botor.aws.sts import sts_conn


class Botor:
    conn_details = {
        'session_name': 'botor',
        'region': 'us-east-1'
    }

    def __init__(self, **kwargs):
        """
        botor = Botor(
            **{'account_number': '000000000000',
               'assume_role': 'role_name',
            })
        """
        self.conn_details.update(kwargs)

    def call(self, function_expr, **kwargs):
        """
        botor = Botor(
            **{'account_number': '000000000000',
               'assume_role': 'role_name',
               'session_name': 'testing',
               'region': 'us-east-1',
               'tech': 'kms',
               'service_type': 'client'
            })

        botor.call("list_aliases")
        botor.call("kms.client.list_aliases")
        """
        if '.' in function_expr:
            tech, service_type, function_name = function_expr.split('.')
        else:
            tech = self.conn_details.get('tech')
            service_type = self.conn_details.get('service_type', 'client')
            function_name = function_expr

        @sts_conn(tech, service_type=service_type)
        def wrapped_method(function_name, **nargs):
            service_type = nargs.pop(nargs.pop('service_type', 'client'))
            return getattr(service_type, function_name)(**nargs)

        kwargs.update(self.conn_details)
        if 'tech' in kwargs:
            del kwargs['tech']
        return wrapped_method(function_name, **kwargs)

    @staticmethod
    def go(function_expr, **kwargs):
        """
        Botor.go(
            'list_aliases',
            **{
                'account_number': '000000000000',
                'assume_role': 'role_name',
                'session_name': 'botor',
                'region': 'us-east-1',
                'tech': 'kms',
                'service_type': 'client'
            })

        Botor.go(
            'kms.client.list_aliases',
            **{
                'account_number': '000000000000',
                'assume_role': 'role_name',
                'session_name': 'botor',
                'region': 'us-east-1'
            })
        """
        if '.' in function_expr:
            tech, service_type, function_name = function_expr.split('.')
        else:
            tech = kwargs.pop('tech')
            service_type = kwargs.get('service_type')
            function_name = function_expr

        @sts_conn(tech, service_type=service_type)
        def wrapped_method(function_name, **nargs):
            service_type = nargs.pop(nargs.pop('service_type', 'client'))
            return getattr(service_type, function_name)(**nargs)

        return wrapped_method(function_name, **kwargs)