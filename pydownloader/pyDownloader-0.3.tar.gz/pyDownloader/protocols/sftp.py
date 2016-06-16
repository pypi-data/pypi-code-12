from logging import getLogger
from protocols import Protocols, ProtocolNotConfiguredException
import paramiko


class SFTPDownloader(Protocols):
    _logger = getLogger(__name__)

    def __init__(self, uri, local_path, **kwargs):

        # Set the local file path
        self.local_path = local_path
        self._logger.debug('Local Path: ' + self.local_path)

        # Set the port (default to 22)
        if 'port' in kwargs:
            self.port = kwargs['port']
        else:
            self.port = 22
        self._logger.debug('Port: ' + str(self.port))

        # Split the URI properly based on if it is authenticated or no
        self._logger.debug('URI: ' + uri)
        self.protocol = 'sftp'
        if '@' in str(uri).replace('sftp://', '') and str(uri).replace('sftp://', '').count(':') == 2:
            self.username = str(uri).replace('sftp://', '').split('@')[0].split(':')[0]
            self.password = str(uri).replace('sftp://', '').split('@')[0].split(':')[1]
            self.host = str(uri).replace('sftp://', '').split('@')[1].split(':')[0]
            self.path = str(uri).replace('sftp://', '').split(':')[2]
            self.private_key = None

        elif '@' in str(uri).replace('sftp://', '')\
                and str(uri).replace('sftp://', '').count(':') == 1\
                and 'private_key' in kwargs:
            self.username = self.username = str(uri).replace('sftp://', '').split('@')[0]
            self.password = None
            self.host = str(uri).replace('sftp://' + self.username + '@', '').split(':')[0]
            self.path = str(uri).replace('sftp://' + self.username + '@', '').split(':')[1]
            self.private_key = kwargs['private_key']

        else:
            raise ProtocolNotConfiguredException('sftp')

        self._logger.debug('Username: ' + self.username)
        self._logger.debug('Password: ' + str(self.password))
        self._logger.debug('Hostname: ' + self.host)
        self._logger.debug('Path    : ' + self.path)
        self._logger.debug('Pkey    : ' + str(self.private_key))

    def _download(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.password is None:
            self.connection.connect(self.host, port=self.port, username=self.username, pkey=self.private_key)
        else:
            self.connection.connect(self.host, port=self.port, username=self.username, password=self.password)

        self.sftp_client = self.connection.open_sftp()

        self.sftp_client.get(self.path, self.local_path, self.set_progress)

    def set_progress(self, transfered, total):
        if self.file_size != total:
            self.file_size = total
            self.downloading = True

        self.downloaded_size = transfered
