import urllib2
import json
from datetime import datetime
import calendar
import time
import sys

class DopamineKit(object):
    """
    # Dopamine API interface class

    # appID -
    # developmentSecret -
    # productionSecret -
    # versionID -

    """
    # TODO: fill in descriptions of properties ^



    identity = []

    _client_os = 'python'
    _client_os_version = sys.api_version
    _client_sdk_version = '3.0.0'
    _server_url = 'https://api.usedopamine.com/v3/app'

    _debug = True               # debug flag set to true for console messages

    def __init__(self, appID, developmentSecret, productionSecret, versionID, inProduction):

        self.appID = appID
        self.developmentSecret = developmentSecret
        self.productionSecret = productionSecret
        self.versionID = versionID
        self.inProduction = inProduction

        return

    def call(self, call_type, call_data, timeout=30):
        """
        # sends a call to the api and returns the response as a string
        # call_type - should be: 'track' or 'reinforce'
        # call_data - dictionary of call specific data
        # timeout - in seconds
        """

        if(call_type != 'track' and call_type != 'reinforce'):
            print ('[DopamineKit] - invalid call_type:{}'.format(call_type))
            return None

        # prepare the api call data structure
        data = {
            'appID': self.appID,
            'versionID': self.versionID,
            'clientOS': self._client_os,
            'clientOSVersion': self._client_os_version,
            'clientSDKVersion' : self._client_sdk_version
        }

        if(self.inProduction):
            data['secret'] = self.productionSecret
        else:
            data['secret'] = self.developmentSecret

        # add the specific call data
        data.update(call_data)

        # append the current local and utc timestamps
        data.update(get_time_utc_local())

        # launch POST request
        url = '{}/{}/'.format(self._server_url, call_type)

        if self._debug:
            print('[DopamineKit] - api call type: {} to url: {}'.format(call_type, url))
            print('[DopamineKit] - call data: {}'.format(data))

        req = urllib2.Request(url, json.dumps(data), {'Content-Type': 'application/json'})
        try:
            raw_data = urllib2.urlopen(req, timeout=timeout).read()
            response = json.loads(raw_data)
            if self._debug:
                print('[DopamineKit] - api response:\n{}'.format(response))

        except urllib2.HTTPError, e:
            print('[DopamineKit] - HTTPError:\n' + str(e))
            return None
        except urllib2.URLError, e:
            print('[DopamineKit] - URLError:\n' + str(e))
            return None
        except httplib.HTTPException, e:
            print('[DopamineKit] - HTTPException:\n' + str(e))
            return None
        except Exception:
            import traceback
            print('[DopamineKit] - generic exception:\n' + traceback.format_exc())
            return None


        if(call_type == 'reinforce'):
            try:
                if response['status'] == 200:
                    return response['reinforcementDecision']
                else:
                    print ('[DopamineKit] - request to DopamineAPI failed, bad status code. Returning "neutralResponse"\n{}'.format(json.dumps(response, indent=4)))
                    return "neutralResponse"
            except KeyError, e:
                print('[DopamineKit] - bad response received, no "reinforcementDecision" found:\n{}'.format(json.dumps(response, indent=4)))
        else:
            return response

    def track(self, identity, actionID, metaData):
        """ tracking api call """

        track_call = {
            'primaryIdentity': identity,
            'actionID': actionID,
            'metaData': metaData
        }

        return self.call('track', track_call)

    def reinforce(self, identity, actionID, metaData, timeout=10):
        """ reinforce api call """

        reinforce_call = {
            'primaryIdentity': identity,
            'actionID': actionID,
            'metaData': metaData
        }

        response = self.call('reinforce', reinforce_call, timeout=timeout)
        return response

def get_time_utc_local():
    """ return a dictionary with the current UTC and localTime """

    utcDateTime = datetime.utcnow()
    return {
        'UTC': calendar.timegm(utcDateTime.utctimetuple()) * 1000,
        'localTime': time.time() * 1000
    }


