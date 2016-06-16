import os
from logging import getLogger
from protocols import Protocols
from exceptions import ProtocolNotConfiguredException
from ftplib import FTP


class FTPDownloader(Protocols):
    _logger = getLogger(__name__)

    connection = None

    def __init__(self, uri, local_path, **kwargs):
        # Set the local file path
        self.local_path = local_path
        self._logger.debug('Local Path: ' + self.local_path)

        # Set the port (Default to 21)
        if 'port' in kwargs:
            self.port = kwargs['port']
        else:
            self.port = 21
        self._logger.debug('Port: ' + str(self.port))

        # Split the URI properly based on if it is authenticated or no
        self._logger.debug('URI: ' + uri)
        self.protocol = 'ftp'
        self.connection = FTP()
        if '@' in str(uri).replace('ftp://', '') and str(uri).replace('ftp://', '').count(':') == 1:
            self.username = str(uri).replace('ftp://', '').split('@')[0].split(':')[0]
            self.password = str(uri).replace('ftp://', '').split('@')[0].split(':')[1]
            self.host = str(uri).replace('ftp://', '').split('@')[1].split('/')[0]
            self.path = '/'.join(str(uri).replace('ftp://', '').split('/')[1:])

        elif '@' not in str(uri).replace('ftp://', '') and str(uri).replace('ftp://', '').count(':') == 0:
            self.username = None
            self.password = None
            self.host = str(uri).replace('ftp://', '').split('/')[0]
            self.path = '/'.join(str(uri).replace('ftp://', '').split('/')[1:])

        else:
            raise ProtocolNotConfiguredException(self.protocol)

        self._logger.debug('Username: ' + str(self.username))
        self._logger.debug('Password: ' + str(self.password))
        self._logger.debug('Hostname: ' + self.host)
        self._logger.debug('Path    : ' + self.path)

    def _download(self):
        try:
            self._logger.debug('Removing file!')
            os.remove(self.local_path)
        except OSError:
            self._logger.debug('File can\'t be overwritten!')
            if os.path.isfile(self.local_path):
                self._logger.debug('File still exists!')
                return
            else:
                self._logger.debug('File doesn\'t exist!')
                pass

        self.connection.connect(host=self.host, port=self.port)
        self._logger.debug('FTP Connection open')

        if self.username is not None:
            self.connection.login(user=self.username, passwd=self.password)
            self._logger.debug('FTP Connection authenticated')
        else:
            self.connection.login()

        self.file_size = self.connection.size(self.path)
        self.downloading = True
        self.connection.retrbinary('RETR ' + self.path, self.writeBlock, blocksize=1024)

        self._logger.debug('File Written!')

    def writeBlock(self, data_block):
        with open(self.local_path, 'ab') as f:
            f.write(data_block)
            self.downloaded_size += 1024
