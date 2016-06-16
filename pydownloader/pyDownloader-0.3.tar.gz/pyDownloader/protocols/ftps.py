from ftp import FTPDownloader
from exceptions import ProtocolNotConfiguredException
from ftplib import FTP_TLS


class FTPSDownloader(FTPDownloader):

    def __init__(self, uri, local_path, **kwargs):
            # Set the local file path
            self.local_path = local_path
            self._logger.debug('Local Path: ' + self.local_path)

            # Set the port (Default to 990)
            if 'port' in kwargs:
                self.port = kwargs['port']
            else:
                self.port = 990
            self._logger.debug('Port: ' + str(self.port))

            # Split the URI properly based on if it is authenticated or not
            self._logger.debug('URI: ' + uri)
            self.protocol = 'ftps'
            self.connection = FTP_TLS()
            if '@' in str(uri).replace('ftps://', '') and str(uri).replace('ftps://', '').count(':') == 1:
                self.username = str(uri).replace('ftps://', '').split('@')[0].split(':')[0]
                self.password = str(uri).replace('ftps://', '').split('@')[0].split(':')[1]
                self.host = str(uri).replace('ftps://', '').split('@')[1].split('/')[0]
                self.path = '/'.join(str(uri).replace('ftps://', '').split('/')[1:])

            elif '@' not in str(uri).replace('ftps://', '') and str(uri).replace('ftps://', '').count(':') == 0:
                self.username = None
                self.password = None
                self.host = str(uri).replace('ftps://', '').split('/')[0]
                self.path = '/'.join(str(uri).replace('ftps://', '').split('/')[1:])

            else:
                raise ProtocolNotConfiguredException(self.protocol)

            self._logger.debug('Username: ' + str(self.username))
            self._logger.debug('Password: ' + str(self.password))
            self._logger.debug('Hostname: ' + self.host)
            self._logger.debug('Path    : ' + self.path)