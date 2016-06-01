from restkit import Resource, request
from api import FIGSHARE_BASE_URL, get_headers
try:
    import simplejson as json
except ImportError:
    import json  # py2.6 only


class figshare_admin_api(Resource):

    def __init__(self, url=FIGSHARE_BASE_URL, token=None, verbose=False, **kwargs):

        self.url = url
        self.token = token
        self.verbose = verbose
        super(figshare_admin_api, self).__init__(self.url)

    def call_hr_feed(self, feed_file):
        '''
        Upload updated feed file.

        :type feed_file: str
        :param feed_file: the path to the feed file
        :return: whether the import was successful
        :rtype: bool
        '''

        with open(feed_file, 'rb') as fin:

            files = {'hrfeed': (feed_file, fin)}
            response = self.post('/institution/hrfeed/upload',
                                 files=files, headers=get_headers(token=self.token))

            print(response.content)
