import sys, hmac, uuid, hashlib, base64
if sys.version_info < (3,):
    import ConfigParser
else:
    import configparser as ConfigParser
from lobgect import log

class Auth(object):
    def __init__(self, config_filepath=None, credentials=None):
        self.logger = log.Log(__name__)
        self.logger.info("Initializing Auth object for QuadrigaCX")

        if config_filepath:
            self.logger.info("Setting authentication through a config file: {}".format(config_filepath))

            self.conf = ConfigParser.ConfigParser()
            self.conf.read(config_filepath)

            self.client_id = self.conf.get('authentication', 'client_id')
            self.key = self.conf.get('authentication', 'key')
            self.secret = self.conf.get('authentication', 'secret')

        elif credentials:
            self.logger.info("Setting authentication through passed-in credentials")

            self.client_id = str(credentials['client_id'])
            self.key = str(credentials['key'])
            self.secret = str(credentials['secret'])

    def __getitem__(self, item):
        if item == 'client_id'  : return self.client_id
        if item == 'key'        : return self.key
        if item == 'secret'     : return self.secret


    def _get_signature(self, nonce):
        return hmac.new(
            bytearray(self.secret.encode('utf-8')),
            bytes(str(
                str(nonce) + self.client_id + self.key
                ).encode('utf-8')
            ),
            digestmod=hashlib.sha256
        ).hexdigest()

    def auth_params(self):
        nonce = uuid.uuid1().int
        self.logger.debug("Nonce: {}".format(nonce))
        return {
            'key': self.key,
            'signature': self._get_signature(nonce),
            'nonce': nonce
        }
