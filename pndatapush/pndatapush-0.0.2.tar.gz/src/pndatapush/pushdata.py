import requests
import os
from abc import ABCMeta, abstractmethod, abstractproperty
import logging
from base64 import b64encode


class PushDataBase(object):
    __metaclass__ = ABCMeta

    # property 'name' for use with logging
    @abstractproperty
    def name(self):
        pass

    # property on whether or not to check if push was successful before marking as sent
    @abstractproperty
    def check_for_success(self):
        pass

    # property for number of max retries before aborting. This should be dependant on check_for_success
    @abstractproperty
    def max_retries(self):
        pass

    # add method for checking whether the push was successful.
    @abstractmethod
    def issuccess(self, response):
        pass

    @abstractmethod
    def push(self, sensordata):
        pass


class PNPushData(PushDataBase):
    name = 'Pervasive Nation'
    max_retries = 20
    check_for_success = True
    pervasivenation_authtoken = None

    def __init__(self, pervasivenation_authtoken=os.environ.get('PERVASIVENATION_AUTHTOKEN', None)):
        self.pervasivenation_authtoken = pervasivenation_authtoken

    def issuccess(self, response):
        status = True
        if self.check_for_success:
            if response.status_code == 200:
                status = True
            elif response.status_code == 401: # 401 Unauthorized.
                logging.error('Authorization token is incorrect or not set. '
                              'Use environment variable PERVASIVENATION_AUTHTOKEN to set token.')
                status = False
            elif response.status_code == 406:  # HTTP_406, 'Media type not acceptable'
                logging.error('You must be able to receive JSON (applicaiton/json) as response from the '
                              'Pervasive nation API. Any other media type is not accepted')
                status = False
            elif response.status_code == 415:  # HTTP_415, 'Unsupported media type'
                logging.error('You must post JSON (applicaiton/json) to Pervasive nation API. '
                              'Any other media type is not accepted')
                status = False

        return status

    def push(self, sensordata):
        print('Pushing [%d] %s data to PN %s with timestamp %s' % (sensordata.id, str(sensordata.deviceid),
                                                                   str(sensordata.payload), str(sensordata.timestamp)))

        sensor_data = {
            "rx": {
                "moteeui": str(sensordata.deviceid),
                "userdata": {
                    "seqno": 0,
                    "port": 1,
                    "payload": b64encode(str(sensordata.payload))
                },
                "gwrx": [
                        {
                            "eui": "0000000000000000",
                            "time": str(sensordata.timestamp),
                            "chan": 0,
                            "rfch": 1,
                            "rssi": -56,
                            "lsnr": "7"
                        }
                    ]
                }
            }

        headers = {"Authorization": "Bearer %s" % self.pervasivenation_authtoken,
                   "content-type": "application/json",
                   "Accept": "application/json"}

        url = os.environ.get('PNDATAPUSH_PNAPI_URL', 'https://api.pervasivenation.com/publish')

        try:
            response = requests.post(url, json=sensor_data, headers=headers)

            return self.issuccess(response)
        except requests.ConnectionError as conn_error:
            logging.error('There was a connection error connecting to Pervasive Nation.')
        # if check_for_success is False then we don't care if it was successful
        return False if self.check_for_success else True
