from constants import PENTAHO_USER_ENDPOINT_DEFINITION
import urlparse


class Pentaho(object):
    def __init__(self, *args, **kwargs):
        self.pentaho_base_url = kwargs.pop("pentaho_base_url", "http://localhost")
        self.pentaho_username = kwargs.pop("pentaho_username", "admin")
        self.pentaho_password = kwargs.pop("pentaho_password", "password")

    @staticmethod
    def validate_urls(url):
        """
        Validate a url
        :param url: the url to validate
        :return: True if valid, False otherwise
        """
        valid = False
        parsed_url = urlparse.urlparse(url)
        if parsed_url:
            valid = True
        return valid

    def get_user_urls(self, endpoint_type):
        """
        Generate the user based urls
        :param endpoint_type: the type of user endpoint required
        :return: the url for the endpoint
        """
        if not endpoint_type or endpoint_type not in PENTAHO_USER_ENDPOINT_DEFINITION:
            raise ValueError("[ERROR] get_user_urls::endpoint_type improper definition ... ")
        pentaho_user_endpoint = urlparse.urljoin(self.pentaho_base_url, PENTAHO_USER_ENDPOINT_DEFINITION[endpoint_type])
        if not self.validate_urls(pentaho_user_endpoint):
            raise ValueError("[ERROR] Improper user endpoint :: {} ... ".format(pentaho_user_endpoint))
        return pentaho_user_endpoint
