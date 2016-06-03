from di_export_cli.swagger.swagger_client.rest import ApiException
from di_export_cli.swagger.swagger_client.configuration import Configuration
from settings_handler import update_auth_token, get_credentials

class ApiExecutor:

    def __init__(self):
        self.RETRIES = 3

    def execute_with_retry(self, function, *arguments, **kw_arguments):
        for i in range(self.RETRIES+1):

            # Add api token
            kw_arguments['x_auth_token'] = Configuration().get_api_key_with_prefix('api_key')

            try:
                return function(*arguments, **kw_arguments)
            except ApiException as e:
                if i < self.RETRIES:
                    if e.status in (401):
                        update_auth_token(get_credentials())
                    elif e.status not in (500, 502, 503, 504):
                        raise
                else:
                    raise
