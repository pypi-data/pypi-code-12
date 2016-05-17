import os.path

import requests

from sermonaudio import BASE_URL, get_request_headers
from sermonaudio.node import types

URL_PATH = 'node'


def get_sermon_info(sermon_id: str, preferred_language_override=None):
    """Calls the sermon_info node endpoint.

    :param sermon_id: The ID of the sermon you want to fetch
    :rtype: sermonaudio.types.Sermon or None
    """
    node_name = 'sermon_info'
    url = os.path.join(BASE_URL, URL_PATH, node_name)
    params = {
        'sermonID': sermon_id
    }

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    if len(node.results) > 0:
        sermon = types.Sermon(node.results[0])
        assert isinstance(sermon, types.Sermon)

        return sermon
    else:
        return None


def get_sermons_by_source(source_id: str, page: int = 1, preferred_language_override=None):
    """Calls the sermons_by_source node endpoint.

    Returned sermons are sorted by date descending.

    :param source_id: The ID of the source you want a listing from.
    :param page: The page number to load (defaults to 1).
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: [sermonaudio.types.Sermon]
    """
    node_name = 'sermons_by_source'
    url = os.path.join(BASE_URL, URL_PATH, node_name)
    params = {
        'sourceID': source_id,
        'page': page
    }

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    sermons = [types.Sermon(result) for result in node.results]

    for sermon in sermons:
        assert isinstance(sermon, types.Sermon)

    return sermons


def get_sermons_by_speaker(speaker_name: str, preferred_language_override=None):
    """Calls the sermons_by_speaker node endpoint.

    Returned sermons are sorted by date descending.

    :param speaker_name: The name of the speaker
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: list of sermonaudio.types.Sermon
    """
    node_name = 'sermons_by_speaker'
    url = os.path.join(BASE_URL, URL_PATH, node_name)
    params = {
        'speakerName': speaker_name
    }

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    sermons = [types.Sermon(result) for result in node.results]

    for sermon in sermons:
        assert isinstance(sermon, types.Sermon)

    return sermons


def get_source_info(source_id: str, preferred_language_override=None):
    """Calls the source_info node endpoint.

    :param source_id: The ID of the source you want info on.
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: sermonaudio.types.Source
    """
    node_name = 'source_info'
    url = os.path.join(BASE_URL, URL_PATH, node_name)
    params = {
        'sourceID': source_id
    }

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    if len(node.results) > 0:
        source = types.Source(node.results[0])
        assert isinstance(source, types.Source)

        return source
    else:
        return None


def get_webcasts_in_progress(preferred_language_override=None):
    """Calls the webcasts_in_progress node endpoint.

    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: [sermonaudio.types.WebcastInfo]
    """
    node_name = 'webcasts_in_progress'
    url = os.path.join(BASE_URL, URL_PATH, node_name)

    response = requests.get(url, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    webcasts = [types.WebcastInfo(result) for result in node.results]

    for webcast in webcasts:
        assert isinstance(webcast, types.WebcastInfo)

    return webcasts


def get_sources_near_location(latitude: float, longitude: float, meters: int, preferred_language_override=None):
    """Calls the source_info node endpoint.

    :param latitude: The latitude of the search origin
    :param longitude: The longitude of the search origin
    :param meters: THe distance from the origin to search
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: sermonaudio.types.Source
    """
    node_name = 'sources_near_location'
    url = os.path.join(BASE_URL, URL_PATH, node_name)
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'meters': meters
    }

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    sources_near_location = [types.SourceNearLocation(result) for result in node.results]

    for source_near_location in sources_near_location:
        assert isinstance(source_near_location, types.SourceNearLocation)

    return sources_near_location
