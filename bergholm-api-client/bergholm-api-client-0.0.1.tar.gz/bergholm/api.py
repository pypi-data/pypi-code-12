import urllib2
import urllib
import re
import json

class Client:
    def __init__(self):
        self.base_url = 'http://www.bergholm.com'

    def get(self, path, params=None):
        query = '?{}'.format(urllib.urlencode(params)) if params else ''
        url = '{}/{}/{}'.format(self.base_url, path, query)
        response = urllib2.urlopen(url)
        content = response.read()
        result = re.search(r'\[(.*)\]', content).group(1)
        json_data = json.loads('[{}]'.format(result))
        return json_data

    def get_all_cihb(self):
        return self.get(path='json/cihb.php')

    def get_products_by_family_id(self, _id):
        return self.get(path='json/produktfamilj.php', params={'id': _id})

    def get_models_by_family_id(self, _id):
        return self.get(path='json/produktfamilj_plans.php', params={'id': _id})

    def get_images_by_family_id(self, _id):
        return self.get(path='json/bilder.php', params={'id': _id})

    def get_information_by_model_id(self, _id):
        return self.get(path='json/detaljer.php', params={'id': _id})
