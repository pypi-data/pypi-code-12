from __future__ import print_function

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

from collections import namedtuple

import json

Wind = namedtuple('Wind', ['direction', 'speed'])

class Boat(object):
    '''A boat controlled by boatd'''
    def __init__(self, host='localhost', port=2222):
        '''
        Create a boat instance, connecting to boatd at `host` on port `port`
        '''
        self.host = host
        self.port = port

    def boatd_url(self, endpoint):
        '''Return a formatted url pointing at `endpoint` on the boatd server'''
        return 'http://{0}:{1}{2}'.format(self.host, self.port, endpoint)

    def _get(self, endpoint):
        '''Return the result of a GET request to `endpoint` on boatd'''
        json_body = urlopen(self.boatd_url(endpoint)).read().decode('utf-8')
        return json.loads(json_body)

    def _post(self, content, endpoint=''):
        '''
        Issue a POST request with `content` as the body to `endpoint` and
        return the result.
        '''
        url = self.boatd_url(endpoint)
        post_content = json.dumps(content).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        request = Request(url, post_content, headers)
        return urlopen(request)

    @property
    def heading(self):
        '''Return the current heading of the boat in degrees'''
        content = self._get('/boat')
        return float(content.get('heading'))

    @property
    def wind(self):
        '''Return the direction of the wind in degrees'''
        content = self._get('/wind')
        return Wind(content.get('direction'), content.get('speed'))

    @property
    def position(self):
        '''Return a tuple in the form `(latitude, longitude)`'''
        content = self._get('/boat')
        return tuple(content.get('position'))

    @property
    def version(self):
        '''Return the version of boatd'''
        content = self._get('/')
        return content.get('boatd').get('version')

    def rudder(self, angle):
        '''Set the angle of the rudder to be `angle` degrees'''
        request = self._post({'value': angle}, '/rudder')
        content = json.loads(request.read().decode('utf-8'))
        return content.get('result')

    def sail(self, angle):
        '''Set the angle of the sail to `angle` degrees'''
        request = self._post({'value': angle}, '/sail')
        content = json.loads(request.read().decode('utf-8'))
        return content.get('result')

if __name__ == '__main__':
    boat = Boat()
    print(boat._get(''))
    print(boat.version)
    print(boat.heading)
    print(boat.wind)
    print(boat.position)
    print(boat.rudder(0))
    print(boat.rudder(10))

