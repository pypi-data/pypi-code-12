import os
import json
import requests

from datetime import datetime
from collabi.open_struct import OpenStruct

class CloudConfig(OpenStruct):
    def __init__(self, env):
        self._rcfn = self._expand_rcfn(env)
        cfg = None
        if os.path.exists(self._rcfn):
            with open(self._rcfn) as rcf:
                cfg = json.load(rcf)
                if 'expiry' in cfg:
                    cfg['expiry'] = self._decode_expiry(cfg['expiry'])
        else:
            url = 'https://public-cdn.cloud.unity3d.com/config/'+env
            resp = requests.get(url)
            resp.raise_for_status()
            cfg = resp.json()
        super(CloudConfig, self).__init__(cfg)

    def save(self):
        adict = {}
        for key, val in self.__dict__.iteritems():
            if key[0] == '_': continue
            if key == 'expiry':
                adict[key] = self._encode_expiry(val)
            else:
                adict[key] = val
        with open(self._rcfn, 'wb') as rcf:
            json.dump(adict, rcf)
        os.chmod(self._rcfn, 0600) # since it houses sensitive tokens (see TODO above)


    ########################################
    # private

    _EXPIRY_FORMAT = '%Y-%m-%d %H:%M:%S '

    @staticmethod
    def _expand_rcfn(env):
        return os.path.join(os.path.expanduser('~'), '.cloud'+env+'rc')

    @staticmethod
    def _decode_expiry(s):
        return datetime.strptime(s, CloudConfig._EXPIRY_FORMAT+'%Z')

    @staticmethod
    def _encode_expiry(e):
        return e.strftime(CloudConfig._EXPIRY_FORMAT+'UTC')
