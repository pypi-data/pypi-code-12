# coding: utf8

import eikon.json_requests
import eikon.Profile
from .tools import is_string_type, to_datetime
import pandas as pd
import numpy as np

News_Headlines_UDF_endpoint = "News_Headlines"
News_Story_UDF_endpoint = "News_Story"

Headline_Selected_Fields = ['versionCreated', 'text', 'storyId', 'sourceCode']
Headline_Selected_Fields_ = ['text', 'storyId', 'bodyType', 'displayDirection', 'documentType',
                             'isAlert', 'language', 'permIDs', 'products', 'rcs', 'reportCode', 'sourceCode',
                             'sourceName', 'versionCreated']


def get_news_headlines(query='Topic:TOPALL and Language:LEN', headlines_count=10, date_from=None,
                       date_to=None, output='pandas', debug=False):
    """
    Returns a list of news headlines

    Parameters
    ----------
    query: string, optional
        News headlines search criteria.
        The text can contain RIC codes, company names, country names and
        operators (AND, OR, NOT, IN, parentheses and quotes for explicit search…).

        Tip: Append 'R:' in front of RIC names to improve performances.

        Default: Top News written in English

    headlines_count: int, optional
        Max number of headlines retrieved.
        Value Range: [1-100].
        Default: 10

    date_from: string or datetime, optional
        Beginning of date range.
        String format is: '%Y-%m-%dT%H:%M:%S'. e.g. '2016-01-20T15:04:05'.

    date_to: string or datetime, optional
        End of date range.
        String format is: '%Y-%m-%dT%H:%M:%S'. e.g. '2016-01-20T15:04:05'.

    output: string
        By default the output is a pandas.DataFrame.
        Set output='raw' to get data in Json format.

    debug: bool
        When set to True, the json request and response are printed.

    Returns
    -------
    pandas.DataFrame
        Returns a DataFrame of news headlines with the following columns:

        - Index               : Timestamp of the publication time
        - version_created     : Date of the latest update on the news
        - text                : Text of the Headline
        - story_id            : Identifier to be used to retrieve the full story using the get_news_story function
        - source_code         : Second news identifier

    Raises
    ----------
    Exception
        If http request fails or if server returns an error
    AttributeError
        If a parameter type is wrong

    Examples
    --------
    >>> import eikon as ek
    >>> ek.set_app_id('set your app id here')
    >>> headlines = ek.get_news_headlines("R:MSFT.O", 2)
    >>> headlines
                                    versionCreated                                              text \
    2016-04-13 18:28:57.000 2016-04-13 18:28:59.001 RBC Applies Blockchain as a Loyalty Boost<MSFT...
    2016-04-13 17:28:21.577 2016-04-13 17:28:21.671 UPDATE 2-Long-stalled email privacy bill advan...
                                                                    storyId
    2016-04-13 18:28:57.000    urn:newsml:reuters.com:20160413:nNRA1uxh03:1
    2016-04-13 17:28:21.577    urn:newsml:reuters.com:20160413:nL2N17G16Q:2

    >>> headlines = ek.get_news_headlines("R:MSFT.O IN FRANCE", 5)
    >>> headlines = ek.get_news_headlines("R:MSFT.O IN FRANCE IN ENGLISH", 5)
    >>> headlines = ek.get_news_headlines("OBA* OR CLINTON IN ENGLISH", 5)
    """

    # check parameters type and values
    if not is_string_type(query):
        raise ValueError('query must be a string')
    if type(headlines_count) is not int:
        raise ValueError('headlines_count must be an integer')
    elif headlines_count < 0:
        raise ValueError('headlines_count must be equal or greater than 0')

    # build the payload
    payload = {'number': str(headlines_count), 'query': query}

    app_id = eikon.Profile.get_profile().get_application_id()
    payload.update({'productName': app_id})
    payload.update({'attributionCode': ''})

    if date_from is not None:
        payload.update({'dateFrom': to_datetime(date_from).isoformat()})

    if date_to is not None:
        payload.update({'dateTo': to_datetime(date_to).isoformat()})

    result = eikon.json_requests.send_json_request(News_Headlines_UDF_endpoint, payload, debug=debug)

    if output.lower() == 'raw':
        return result

    json_headline_array = result['headlines']

    return convert_json_headlines_to_pandas(json_headline_array)


def convert_json_headlines_to_pandas(json_headline_array):
    first_created = [headline['firstCreated'] for headline in json_headline_array]
    headlines = [[headline[field] for field in Headline_Selected_Fields]
                 for headline in json_headline_array]
    headlines_dataframe = pd.DataFrame(headlines, np.array(first_created, dtype='datetime64'), Headline_Selected_Fields)
    headlines_dataframe['versionCreated'] = headlines_dataframe.versionCreated.apply(pd.to_datetime)
    return headlines_dataframe


def get_news_story(headlines, output='string', debug=False):
    """
    Return a news story for the first news in the headlines pandas.DataFrame

    Parameters
    ----------
    headlines: pandas.DataFrame or pandas.Series or tuple
        Headlines DataFrame returned by get_news_headlines.
        Only the first row is used. Use headlines.iloc[[n]] to retrieve the nth story.

    output: string
        By default the output is a string. Set output='raw' to get data in Json format.

    debug: bool
        When set to True, the json request and response are printed.

    Raises
    ------
    Exception
        If http request fails or if Thomson Reuters Services return an error
    ValueError
        If a parameter type or value is wrong

    Examples
    --------
    >>> import eikon as ek
    >>> ek.set_app_id('set your app id here')
    >>> headlines = ek.get_news_headlines('IBM')
    >>> for headline in headlines.iterrows():
        ... story = ek.get_news_story(headline)
        ... print (story)
    """

    # build the request
    app_id = eikon.Profile.get_profile().get_application_id()

    if type(headlines) is tuple:
        try:
            source_code = headlines[1]['sourceCode']
            story_id = headlines[1]['storyId']
        except Exception:
            raise ValueError('tuple headlines has incorrect format')
    elif type(headlines) is pd.Series:
        try:
            source_code = headlines['sourceCode']
            story_id = headlines['storyId']
        except Exception:
            raise ValueError('pandas.Series headlines has incorrect format')
    elif type(headlines) is pd.DataFrame:
        try:
            source_code = headlines['sourceCode'].iloc[0]
            story_id = headlines['storyId'].iloc[0]
        except Exception:
            raise ValueError('headlines DataFrame has incorrect format')
    else:
        try:
            source_code = headlines.sourceCode
            story_id = headlines.storyId
        except Exception:
            raise ValueError('headlines must be a pandas.DataFrame')

    payload = {'attributionCode': source_code, 'productName': app_id, 'storyId': story_id}

    print('Request data: {}'.format(payload))
    result = eikon.json_requests.send_json_request(News_Story_UDF_endpoint, payload, debug=debug)

    if output.lower() == 'raw':
        return result

    return result['story']['storyHtml']
