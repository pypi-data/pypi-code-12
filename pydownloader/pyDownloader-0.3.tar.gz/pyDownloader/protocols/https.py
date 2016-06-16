from http import HTTPDownloader
from exceptions import ProtocolNotConfiguredException


class HTTPSDownloader(HTTPDownloader):
    def __init__(self, uri, local_path, **kwargs):
        # Set the local file path
        self.local_path = local_path

        # Check if we know we don't want to check SSL Certificates
        if 'ssl_verify' in kwargs:
            self.ssl_verify = kwargs['ssl_verify']

        # Split the URI properly based on if it is authenticated or no
        self.protocol = 'https'
        if '@' in str(uri).replace('https://', '') and ':' in str(uri).replace('https://', ''):
            self.username = str(uri).replace('https://', '').split('@')[0].split(':')[0]
            self.password = str(uri).replace('https://', '').split('@')[0].split(':')[1]
            self.host = str(uri).replace('https://', '').split('@')[1].split('/')[0]
            self.path = '/'.join(str(uri).replace('https://', '').split('/')[1:])

        elif '@' not in str(uri).replace('https://', '') and ':' not in str(uri).replace('https://', ''):
            self.username = None
            self.password = None
            self.host = str(uri).replace('https://', '').split('/')[0]
            self.path = '/'.join(str(uri).replace('https://', '').split('/')[1:])

        else:
            raise ProtocolNotConfiguredException('https')
