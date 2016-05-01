class PinPaymentsException(Exception):

    def __init__(self, response, msg=None, errors=None):

        if response.headers['content-type'].startswith('application/json'):
            data = response.json()
            msg = "%s: %s" % (data['error'], data['error_description'])
            errors = []
            if data.get('messages') is not None:
                for error_message in data.get('messages'):
                    error = "%s: %s (%s)" % (error_message['code'], error_message['message'], error_message['param'])
                    errors.append(error)

            super(PinPaymentsException, self).__init__(response, msg, errors)

        self.msg = msg
        self.errors = errors
