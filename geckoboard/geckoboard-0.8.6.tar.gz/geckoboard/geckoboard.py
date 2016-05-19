#!/usr/bin/env python
"""Geckoboard API Interface (Unofficial).

This module/class is designed to work with the Geckoboard API.

Geckoboard can be found here:
    https://www.geckoboard.com/

Geckoboard API documentation can be found here:
    https://developer.geckoboard.com/#introduction

Examples:
    >>> import os
    >>> from geckoboard import Gecko
    >>> gecko = Gecko(os.environ['GECKOAPI'])
"""

import requests


class Gecko(object):
    """Geckoboard API Interface.

    Attributes:
        api_key (str): Geckoboard API Key.
        url (str): Geckoboard API Url.

    """

    def __init__(self, api_key):
        """Initialize Gecko object.

        Args:
            api_key (str): Geckoboard API Key.

        """
        self.api_key = api_key
        self.url = 'https://push.geckoboard.com/v1/send/'

    def push(self, widget_key, data):
        """Push data to Geckoboard.

        Args:
            widget_key (str): Unique Geckoboard widget key.
            data (dict): Data to post to Geckoboard.
            Should be in the form of:
                {'item': []}

        Returns:
            None or object: None if error, requests.response if successful.

        """
        status = None
        widget_url = "%s/%s" % (self.url.strip('/'), widget_key)
        post_data = {'api_key': self.api_key, 'data': data}
        try:
            response = requests.post(widget_url, json=post_data)
            response.raise_for_status()
        except requests.HTTPError:
            pass
        else:
            if response.json().get('success'):
                status = response

        return status

    def number(self, widget_key, value1, value2=None, **kwargs):
        """Push to number widget.

        Args:
            widget_key (str): Unique Geckoboard widget key.
            value1 (int): number to publish to Geckoboard.
            value2 (int|list): number or trendline to publish to Geckoboard.
                An (int) is used for comparison to value1.
                A (list) is used to plot a trendline.
            **kwargs: Additional parameters.
                text (str): Label to appear after the primary value.
                prefix (str): Label to appear before the primary value.
                absolute (bool): Comparison using absolute values.
                    Defaults to False.
                    If True, use absolute values for comparison.
                    If False, use percentages for comparison
                reverse (bool): Reverse comparison. Defaults to False.

        Examples:
            >>> import os
            >>> from geckoboard import Gecko
            >>> gecko = Gecko(os.environ['GECKOAPI'])
            >>> widget_key = '186285-86ab59ff-5662-4867-a8ff-0d88a3efc966'

            >>> gecko.number(widget_key, 100)
            <Response [200]>

            >>> gecko.number(widget_key, 100, 200)
            <Response [200]>

            >>> gecko.number(widget_key, 100, [10, 5, 15, 8],\
                             text='Million', prefix='$')
            <Response [200]>

            >>> gecko.number(widget_key, 100, 200, absolute=True)
            <Response [200]>

            >>> gecko.number(widget_key, 100, 200, absolute=True, reverse=True)
            <Response [200]>

            >>> gecko.number(widget_key, 100, 200, text='Million', prefix='$')
            <Response [200]>

        Returns:
            None or object: None if error, requests.response if successful.

        """
        data = {'item': []}
        text = kwargs['text'] if 'text' in kwargs else ''
        prefix = kwargs['prefix'] if 'prefix' in kwargs else ''
        if 'absolute' in kwargs:
            if kwargs['absolute']:
                data['absolute'] = True
        if 'reverse' in kwargs:
            if kwargs['reverse']:
                data['type'] = 'reverse'

        if value1:
            data['item'].append({'value': value1,
                                 'text': text,
                                 'prefix': prefix})
        if isinstance(value2, list):
            data['item'].append(value2)
        else:
            data['item'].append({'value': value2,
                                 'text': text,
                                 'prefix': prefix})
        return self.push(widget_key, data)

    def rag(self, widget_key, items, prefix='', reverse=False):
        """Push to RAG (Red Amber Green) visualization widget.

        Args:
            widget_key (str): Unique Geckoboard widget key.
            items (List[dict]): Items to push to the widget.
            prefix (str): Prefix to append to all items.
                Defaults to ''.
                May be overridden per item, via the items input.
                Percent symbol (%) is treated as a suffix.
            reverse (bool): Reverse the list order. Defaults to False.

        Examples:
            >>> import os
            >>> from geckoboard import Gecko
            >>> gecko = Gecko(os.environ['GECKOAPI'])
            >>> widget_key = '186285-649213c7-c5ac-4d58-a3e5-6d9066aee288'

            >>> gecko.rag(widget_key, [{'Brad': 255},\
                                       {'Rich': 1050},\
                                       {'Bob': 187}])
            <Response [200]>

            >>> gecko.rag(widget_key, [{'Brad': 255},\
                                       {'Rich': 1050},\
                                       {'Bob': 187}],\
                                      prefix='$')
            <Response [200]>

            >>> gecko.rag(widget_key, [{'Brad': 255},\
                                       {'Rich': 1050},\
                                       {'Bob': 187}],\
                          prefix='%')
            <Response [200]>

            >>> gecko.rag(widget_key,\
                          [{'Brad': {'value': 255, 'prefix': '%'}},\
                           {'Rich': {'value': 1050, 'prefix': '%'}},\
                           {'Bob': 187}])
            <Response [200]>

        Returns:
            None or object: None if error, requests.response if successful.

        """
        data = {'item': []}
        if reverse:
            data['type'] = 'reverse'

        for item in items:
            for text, value in item.iteritems():
                if isinstance(value, (int, str)):
                    item = {'text': text, 'value': value, 'prefix': prefix}
                elif isinstance(value, dict):
                    item = {'text': text}
                    for option, val in value.iteritems():
                        item[option] = val
                    if 'prefix' not in item:
                        item['prefix'] = prefix
                data['item'].append(item)

        return self.push(widget_key, data)

    def pie(self, widget_key, items, color=''):
        """Push to pie graph widget.

        Args:
            widget_key (str): Unique Geckoboard widget key.
            items (List[dict]): Items to push to the widget.
            color (str): Pie slice color for all items.
                Defaults to ''.
                May be overridden per item, via the items input.
                Must be valid hex color codes like 'c0c0c0'.

        Examples:
            >>> import os
            >>> from geckoboard import Gecko
            >>> gecko = Gecko(os.environ['GECKOAPI'])
            >>> widget_key = '186285-125dc97d-dfa0-488b-a3ba-9c98a2549e8b'

            >>> gecko.pie(widget_key, [{'Brad': 255},\
                                       {'Rich': 1050},\
                                       {'Bob': 187}])
            <Response [200]>

            >>> gecko.pie(widget_key, [{'Brad': {'value': 255,\
                                                 'color': 'ff0000'}},\
                                       {'Rich': {'value': 1050,\
                                                 'color': '0000ff'}},\
                                       {'Bob': {'value': 187,\
                                                'color': '00ff00'}}])
            <Response [200]>

            >>> gecko.pie(widget_key, [{'Brad': {'value': 255,\
                                                 'color': 'ff0000'}},\
                                       {'Rich': {'value': 1050,\
                                                 'color': '0000ff'}},\
                                       {'Bob': 187}],\
                          color='c0c0c0')
            <Response [200]>

        Returns:
            None or object: None if error, requests.response if successful.

        """
        data = {'item': []}
        for item in items:
            for label, value in item.iteritems():
                if isinstance(value, (int, str)):
                    item = {'label': label, 'value': value, 'color': color}
                elif isinstance(value, dict):
                    item = {'label': label}
                    for option, val in value.iteritems():
                        item[option] = val
                    if 'color' not in item:
                        item['color'] = color
                data['item'].append(item)

        return self.push(widget_key, data)

    def line(self, widget_key, series, **kwargs):
        """Push to line graph widget.

        Args:
            widget_key (str): Unique Geckoboard widget key.
            series (List[dict]): Series of data to publish to the widget.
            **kwargs: Additional parameters.
                type (str): Set x-axis type. Defaults to 'standard'.
                    Specifying the string "datetime" will cause all X axis
                    values to be interpreted as an ISO 8601 date/time.
                    Partial dates (e.g. 2014-10 for October 2014) are
                    supported. See below for details on how datetimes are
                    rendered on the chart. Leaving type empty or setting
                    it to standard will cause X values to be interpreted
                    the usual way.
                format (str): Set y-axis format. Defaults to 'decimal'.
                    If given, this string will represent the format of
                    the Y axis and will be displayed accordingly.
                    Possible values are "decimal", "percent" and "currency".
                unit (str): Set y-axis unit type for the 'currency' format.
                    Defaults to 'USD'.
                    When the format is currency this must be
                    an ISO 4217 currency code. E.g. "GBP", "USD", "EUR"

        Examples:
            >>> import os
            >>> from geckoboard import Gecko
            >>> gecko = Gecko(os.environ['GECKOAPI'])
            >>> widget_key = '186285-4b472381-cf47-422e-9e6a-e03fee123ae7'

            >>> gecko.line(widget_key,\
                           [{'name': 'Brad', 'data': [1, 2, 3, 4]},\
                            {'name': 'Rich', 'data': [4, 3, 2, 1]},\
                            {'name': 'Bob', 'data': [1, 3, 2, 4]}])
            <Response [200]>

            >>> gecko.line(widget_key,\
                           [{'name': 'Brad', 'data': [1, 2, 3, 4]},\
                            {'name': 'Rich', 'data': [4, 3, 2, 1]}],\
                           type='secondary')
            <Response [200]>

            >>> gecko.line(widget_key,\
                           [{'name': 'Brad', 'data': [1, 2, 3, 4]},\
                            {'name': 'Rich', 'data': [4, 3, 2, 1]},\
                            {'name': 'Bob', 'data': [1, 3, 2, 4]}],\
                          x_axis=['2016-01', '2016-02', '2016-03', '2016-04'])
            <Response [200]>

            >>> gecko.line(widget_key,\
                           [{'name': 'Brad', 'data': [1, 2, 3, 4]},\
                            {'name': 'Rich', 'data': [4, 3, 2, 1]},\
                            {'name': 'Bob', 'data': [1, 3, 2, 4]}],\
                          x_axis=['2016-01', '2016-02', '2016-03', '2016-04'],\
                          format='currency', unit='USD')
            <Response [200]>

        Returns:
            None or object: None if error, requests.response if successful.

        """
        data = {'series': series, 'x_axis': {}, 'y_axis': {}}
        if 'x_axis' in kwargs:
            data['x_axis']['labels'] = kwargs['x_axis']
        elif 'labels' in kwargs:
            data['x_axis']['labels'] = kwargs['labels']
        if 'type' in kwargs:
            options = ['standard', 'datetime']
            data['x_axis']['type'] = 'standard'
            if kwargs['type'] in options:
                data['x_axis']['type'] = kwargs['type']
        if 'format' in kwargs:
            options = ['decimal', 'percent', 'currency']
            data['y_axis']['format'] = 'decimal'
            if kwargs['format'] in options:
                data['y_axis']['format'] = kwargs['format']
            if 'currency' in kwargs['format']:
                data['y_axis']['unit'] = 'USD'
        if 'unit' in kwargs:
            data['y_axis']['unit'] = kwargs['unit']

        return self.push(widget_key, data)

    def text(self, widget_key, *texts, **kwargs):
        """Push to text widget.

        Args:
            widget_key (str): Unique Geckoboard widget key.
            *texts (str|dict): Text to publish to the widget.
                Each argument is published as an additional page on the widget.
            **kwargs: Additional parameters.
                flag (str): Add extra visual clue to each page of the widget.
                    Defaults to 'none'.
                    When it's not given or set to 'none' (0), no icon will be
                    added. When type is set to 'alert' (1) an exclamation point
                    on yellow background will appear in the top right corner.
                    When type is set to 'info' (2), an 'i' icon on grey
                    background will be displayed in the top right corner.

        Examples:
            >>> import os
            >>> from geckoboard import Gecko
            >>> gecko = Gecko(os.environ['GECKOAPI'])
            >>> widget_key = '186285-adaf4a5a-dd89-4356-8f43-75bfaf6b9576'

            >>> gecko.text(widget_key, 'Hello World!')
            <Response [200]>

            >>> gecko.text(widget_key, 'Hello', 'World!')
            <Response [200]>

            >>> gecko.text(widget_key, 'Hello', 'World!', flag='alert')
            <Response [200]>

            >>> gecko.text(widget_key,\
                           {'text': 'Hello', 'type': 0},\
                           {'text': 'World', 'type': 1})
            <Response [200]>

        Returns:
            None or object: None if error, requests.response if successful.

        """
        data = {"item": []}
        flags = {'none': 0, 'alert': 1, 'info': 2}
        flag = 0
        if 'flag' in kwargs:
            if kwargs['flag'] in flags:
                flag = flags[kwargs['flag']]

        for text in texts:
            if isinstance(text, dict):
                data['item'].append(dict(text))
            else:
                data['item'].append({'text': text, 'type': flag})

        return self.push(widget_key, data)

    def meter(self, widget_key, value, min_value=0, max_value=100):
        """Push to gecko-o-meter widget.

        Args:
            widget_key (str): Unique Geckoboard widget key.
            value (int): Primary value of the widget.
            min_value (int): Minimum value for the widget scale.
                Defaults to 0
            max_value (int): Maximum value for the widget scale.
                Defaults to 100

        Examples:
            >>> import os
            >>> from geckoboard import Gecko
            >>> gecko = Gecko(os.environ['GECKOAPI'])
            >>> widget_key = '186285-cf4afbf9-e70f-40f6-a965-ed9817cea428'

            >>> gecko.meter(widget_key, 69)
            <Response [200]>

            >>> gecko.meter(widget_key, 690, 0, 1000)
            <Response [200]>

        Returns:
            None or object: None if error, requests.response if successful.

        """
        data = {'item': value,
                'min': {'value': min_value},
                'max': {'value': max_value}}

        return self.push(widget_key, data)

    def leaderboard(self, widget_key, items, **kwargs):
        """Push to leaderboard widget.

        Args:
            widget_key (str): Unique Geckoboard widget key.
            items (List[list]): Series of data to publish to the leaderboard
            **kwargs: Additional parameters.
                format (str): Optional possible values are "decimal", "percent"
                    and "currency". The default is "decimal".
                unit (str): Optional When the format is currency this must be
                    an ISO 4217 currency code. E.g. "GBP", "USD", "EUR".

        Examples:
            >>> import os
            >>> from geckoboard import Gecko
            >>> gecko = Gecko(os.environ['GECKOAPI'])
            >>> widget_key='186285-0ba9cd63-efd0-4a9e-b37a-8ba0cf27694c'

            >>> gecko.leaderboard(widget_key, [['Peter', 234.4],\
                                               ['Patrick', 232]])
            <Response [200]>

            >>> gecko.leaderboard(widget_key, [['Peter', 234.4, 2],\
                                               ['Patrick', 232, 1]])
            <Response [200]>

            >>> gecko.leaderboard(widget_key, [['Peter', 34],\
                                               ['Patrick', 32]],\
                                               format='percent')
            <Response [200]>

            >>> gecko.leaderboard(widget_key, [['Peter', 34.4, 2],\
                                               ['Patrick', 32, 1]],\
                                               format='currency', unit='usd')
            <Response [200]>

        Returns:
            None or object: None if error, requests.response if successful.

        """
        data = {"items": []}
        for item in items:
            if len(item) == 2:
                data['items'].append({"label": item[0], "value": item[1]})
            if len(item) == 3:
                data['items'].append({"label": item[0],
                                      "value": item[1],
                                      "previous_rank": item[2]})
        if 'format' in kwargs:
            data['format'] = kwargs['format']
        if 'unit' in kwargs:
            data['unit'] = kwargs['unit']
        return self.push(widget_key, data)

    # pylint: disable=too-many-branches
    def map(self, widget_key, **kwargs):
        """Push to map widget.
        Examples:
            >>> import os
            >>> from geckoboard import Gecko
            >>> gecko = Gecko(os.environ['GECKOAPI'])
            >>> widget_key='186285-c49c766a-ac6f-420e-b1e5-3a473a1a0c74'

            >>> gecko.map(widget_key,\
                          host=[['www.promnetwork.com', 6, 'ff0000'],\
                                'www.microsoft.com'],\
                          ip=[['208.184.9.4', 2, '00ff00'], '8.8.4.4'],\
                          coordinates=[['33.94336', '18.896484'],\
                                       ['39.412327',\
                                        '-77.425461',\
                                        '2',\
                                        '0000ff']],\
                          city=[['San Francisco', 'us'],\
                                ['New York', 'us', 'ny'],\
                                ['myrtle beach', 'us', 'sc', 8, '0000ff']])
            <Response [200]>

        """
        data = {}
        data['points'] = {}
        data['points']['point'] = []
        if 'ip' in kwargs:
            for value in kwargs['ip']:
                if len(value) == 1:
                    data["points"]["point"].append({'ip': value})
                elif len(value) == 3:
                    data["points"]["point"].append({'ip': value[0],
                                                    'size': value[1],
                                                    'color': value[2]})
        if 'host' in kwargs:
            for value in kwargs['host']:
                if len(value) == 1:
                    data["points"]["point"].append({'value': value})
                elif len(value) == 3:
                    data["points"]["point"].append({'value': value[0],
                                                    'size': value[1],
                                                    'color': value[2]})
        if 'coordinates' in kwargs:
            for value in kwargs['coordinates']:
                if len(value) == 2:
                    data["points"]["point"].append({'latitude': value[0],
                                                    'longitude': value[1]})
                if len(value) == 4:
                    data["points"]["point"].append({'latitude': value[0],
                                                    'longitude': value[1],
                                                    'size': value[2],
                                                    'color': value[3]})
        if 'city' in kwargs:
            for value in kwargs['city']:
                if len(value) == 2:
                    data["points"]["point"].append({'city':
                                                    {'city_name':  value[0],
                                                     'country_code':
                                                     value[1]}})
                if len(value) == 3:
                    data["points"]["point"].append({'city':
                                                    {'city_name': value[0],
                                                     'country_code': value[1],
                                                     'region_code': value[2]}})
                if len(value) == 5:
                    data["points"]["point"].append({'city':
                                                    {'city_name': value[0],
                                                     'country_code': value[1],
                                                     'region_code': value[2]},
                                                    'size': value[3],
                                                    'color': value[4]})
        return self.push(widget_key, data)
