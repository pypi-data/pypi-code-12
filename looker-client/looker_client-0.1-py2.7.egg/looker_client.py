import json
import urllib
from StringIO import StringIO
from itertools import compress

import pandas as pd
import requests


class LookerClient(object):
    def __init__(self, token, secret, host, port=19999, limit=1000000):
        """
        Python API for Looker 3.0
        NOTE: Limit does not work with get_df_from_slug, have to set the limit within Looker before getting slug
        :param token: string, Looker API Token
        :param secret: string, Looker API Secret
        :param host: string, URL of your Looker instance, for example https://yourcompany.looker.com
        :param port: int
        :param limit: int
        """
        self.token = token
        self.secret = secret
        self.host = host
        self.port = port
        self.limit = limit
        self.access_token = self.get_access_token_to_looker()

    def get_access_token_to_looker(self):
        """
        Logs you in, and returns a session key to let you access data
        :return:
        """
        res = requests.post(
            '{0}:{1}/api/3.0/login?client_id={2}&client_secret={3}'.format(self.host, self.port, self.token,
                                                                           self.secret))
        return json.loads(res.text)['access_token']

    def get_df_from_long_share_url(self, share_url):
        """
        TODO: Handle Pivots/Sorts.
        :param share_url:
        :return:
        """
        share_url = self.get_useful_part(share_url)
        elements = self.parse_looker_link_url(share_url)
        query, column_expected = self.query(elements[0], elements[1], elements[2], elements[3], None, None)
        # Steps to get the order of columns as it was when you set-up the Look
        # It seems Looker is Sorting by name to get their sort, versus keeping original sort
        # 1) Find index of column_expected in column_ordered
        # 2) Find name of column in df
        # 3) Re-order df to match what was expected
        column_ordered = sorted(column_expected)
        expected_to_real = [(l_item, column_ordered.index(l_item)) for l_item in column_expected]
        df = self.get_df_from_url(query)
        real = df.columns.tolist()
        df = df[[real[ex[1]] for ex in expected_to_real]]
        df.columns = column_expected
        return df

    def get_df_from_slug(self, slug):
        """
        Gets a pandas DataFrame from a short URL (Exposed via Tools --> Share in Looker)
        :param url:
        :return:
        """
        slug = slug.split('/')[-1]
        get_slug = requests.get(
            '{0}:{1}/api/3.0/queries/slug/{2}?access_token={3}'.format(self.host, self.port, slug, self.access_token))
        query_id = json.loads(get_slug.text)['id']
        url = '{0}:{1}/api/3.0/queries/{2}/run/csv?access_token={3}'.format(self.host, self.port, query_id,
                                                                            self.access_token)
        return self.get_df_from_url(url)

    def parse_looker_link_url(self, share_url):
        """
        Code to split out a looker long url to explore, models, dimensions, filters, pivots
        TODO: What if slashsplit < 5?
        Written by David Havens/@dhavens
        :param share_url: Long URL from share menu in Looker
        :return:
        """
        share_url = str(urllib.unquote(share_url).decode('utf8'))
        # parse url
        slashsplit = share_url.split('/')
        if len(slashsplit) > 5:
            self.flag = 1
            models = slashsplit[4]
            # parse explore name
            explore = slashsplit[5][0:slashsplit[5].index('?')]
            # parse dimensions
            fields = share_url[share_url.index('fields=') + 7:share_url.index('&')].split(',')
            fields = [x for x in fields if x != '[]']
            if fields:
                dimensions = fields
                filters = self.get_filters(share_url)
                # if pivots, parse pivots
                pivots = self.get_pivots(share_url)
                return [explore, models, dimensions, filters, pivots]
            else:
                self.flag = 0

    @staticmethod
    def get_useful_part(input_url):
        """
        Gets the used parts of a Looker URL shared via Share button / using long share version
        :param input_url:
        :return:
        """
        test_list = ["&sorts", "&limit", "&column_limit", "&vis", "&filter_config", "dynamic_fields", "&show", "origin"]
        matches = [True if substring in input_url else False for substring in test_list]
        matches = list(compress(xrange(len(matches)), matches))
        first_element = test_list[matches[0]]
        req_string = input_url.replace(input_url[input_url.index(first_element):], "&end")
        return req_string

    def query(self, explore, model, fields, filters=None, sorts=None, sortdir=None, output='csv'):
        uri = ":%s/api/3.0/queries/models/%s/views/%s/run/%s" % (self.port, model, explore, output)
        fields_string = ",".join(sorted([field.lower() for field in fields]))
        filters_list = []
        if filters:
            for key, value in filters.iteritems():
                filters_list.append("filters[%s]=%s" % (str(key).lower(), urllib.quote_plus(str(value))))
        sorts_string = '&sorts=%s%s' % (sorts, '+%s' % sortdir if sortdir else '')
        end_query = "fields=%s&%s&limit=%i%s" % (
            fields_string, "&".join(sorted(filters_list)), self.limit, sorts_string if sorts else '')
        ur = "%s%s?%s" % (self.host, uri, end_query)
        return '%s&&access_token=%s' % (ur, self.access_token), fields

    def get_df_from_url(self, url):
        """
        Gets Pandas DataFrame from URL
        :param url:
        :return:
        """
        txt = requests.get(url).text
        self.txt = txt
        df = pd.DataFrame.from_csv(StringIO(txt))
        df[df.index.name] = df.index
        df.index = range(0, len(df))
        df = df.sort_index(axis=1)
        return df

    @staticmethod
    def get_pivots(input_url):
        if input_url.find('&pivot') > 0:
            pivots = input_url[input_url.index('pivots=') + 7:input_url.index('&f')].split(',')
        else:
            pivots = []
        return pivots

    @staticmethod
    def get_filters(input_url):
        if input_url.find('&f[') > 0:
            filterstring = input_url[input_url.index('&f[') + 3:input_url.index('&end')].split('&f[')
            keys = []
            values = []
            for i in range(0, len(filterstring)):
                keys.append(filterstring[i][0:filterstring[i].index(']=')])
                value = filterstring[i][filterstring[i].index(']=') + 2:]
                value = value.replace("+", " ")
                values.append(value)
            return dict(zip(keys, values))
        else:
            return []
