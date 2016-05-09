"""
Google/Apple/Ingress Maps URL processing and Google Geocoding utilities.

"""

import re
import math
from urllib.parse import urlparse, parse_qs, unquote_plus

import requests


def check_mapurl(string):
    """Is this an interesting string?

    This is a simple test for portential map URLs, not a full test. It may
    return false positives and should not be used for validating URLs.

    Returns the URL portion of a potential string, or None if none found.
    """
    match = re.search(r"\b(?P<url>https?://(goo\.gl/maps/|(www\.)?google\.com/maps|maps\.google\.com|(www\.)?ingress\.com/intel|maps\.apple\.com)\S+)",
                      string, re.IGNORECASE|re.MULTILINE)
    return match.group("url") if match else None


def parse_mapurl(url, name=None, caption=None, body=None):
    """Parse an Ingress Intel, or Google or Apple Maps URL.

    Be advised, this routine may make multiple HTTP requests in its quest to parse the URL,
    due to the need to expand short URLs, such as the case when the URL doesn't actually have
    lat/lng information in it and we need to either expand a shortURL or scrape a body.

    It will only parse the first "map-like" URL in the string.

    If the URL is unparsable, raise ValueError

    Returns a dictionary containing:
    'latlng' -- [latitude, longitude] of location specified by the URL
    'zoom' -- zoom parameter from the URL, if present
    'name' -- a name for this location, extracted from URL/Map or generated
    'caption' -- a caption for this map, typically natural language, if we could get one
    'platlng' -- present only if the URL is for an Ingress portal
    """
    if not url:
        raise ValueError("empty url")

    # If it's a short URL, fetch expanded URL and try again
    match = re.search(r"\b(?P<url>https?://goo.gl/maps/\S+)", url, re.IGNORECASE|re.MULTILINE)
    if match:
        res = requests.get(match.group("url"))
        return parse_mapurl(res.url, name, caption, res.text)

    region = {}

    # Does the URL already have an @<lat>,<lng> in it?
    match = re.search(r"@(?P<lat>-?[0-9]{1,3}\.[0-9]+),(?P<lng>-?[0-9]{1,3}\.[0-9]+)(,(?P<zoom>[0-9]+)z)?", url)
    if match:
        region["latlng"] = [float(match.group("lat")),
                            float(match.group("lng"))]
        try:
            region["zoom"] = int(match.group("zoom"))
        except (IndexError, TypeError):
            pass

    # Is it a Google Places URL?
    match = re.search(r"\bhttps?://(www\.)?google\.com/maps/place/(?P<place>[^/]*)/",
                      url, re.IGNORECASE|re.MULTILINE)
    if match:
        region["caption"] = unquote_plus(match.group("place"))

        # if we weren't able to already get the coordinates (above), expand the url and scrape body
        if "latlng" not in region:
            res = requests.get(url)
            body = res.text
            if body:
                match = re.search(r"cacheResponse\(\[\[\[[0-9]+\.[0-9]+,(?P<lng>-?[0-9]{1,3}\.[0-9]+),(?P<lat>-?[0-9]{1,3}\.[0-9]+)\]", body)
                if match:
                    region["latlng"] = [float(match.group("lat")),
                                        float(match.group("lng"))]
                    try:
                        region["zoom"] = int(match.group("zoom"))
                    except IndexError:
                        pass

    # Is it a Google Maps search URL?
    elif re.search(r"\bhttps?://(www\.)?google\.com/maps/search/(?P<lat>-?[0-9]{1,3}\.[0-9]+),(?P<lng>-?[0-9]{1,3}\.[0-9]+)(,(?P<zoom>[0-9]+)z)?", url, re.IGNORECASE|re.MULTILINE):
        match = re.search(r"\bhttps?://(www\.)?google\.com/maps/search/(?P<lat>-?[0-9]{1,3}\.[0-9]+),(?P<lng>-?[0-9]{1,3}\.[0-9]+)(,(?P<zoom>[0-9]+)z)?",
                          url, re.IGNORECASE|re.MULTILINE)
        if match:
            region["latlng"] = [float(match.group("lat")),
                                float(match.group("lng"))]
            try:
                region["zoom"] = int(match.group("zoom"))
            except (IndexError, TypeError):
                pass

    # Is it an Apple Maps URL?
    elif re.search(r"\bhttps?://maps.apple.com/",
                   url, re.IGNORECASE|re.MULTILINE):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        try:
            region["latlng"] = [float(cor) for cor in query["sll"][0].split(",")]
            region["caption"] = unquote_plus(query["q"][0])
        except KeyError:
            pass

    # Is it an Ingress Intel URL or classic (whew!) Google Maps URL?
    elif re.search(r"\bhttps?://((www\.)?google\.com/maps|maps\.google\.com|(www\.)?ingress\.com/intel)",
                   url, re.IGNORECASE|re.MULTILINE):

        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        if "zoom" not in region and "z" in query:
            region["zoom"] = int(query["z"][0])

        if "caption" not in region and "q" in query:
            match = re.search(r"&q=(?P<caption>.+)$", url)
            if match:
                region["caption"] = unquote_plus(match.group("caption"))

        if "latlng" not in region:
            # if ll exists, it is the latlng
            #   if q also exists, q is the caption (note: google doesn't encode & properly!)
            # otherwise
            #   q is, hopefully, the latlng
            try:
                region["latlng"] = [float(cor) for cor in query["ll"][0].split(",")]
            except KeyError:
                region["latlng"] = [float(cor) for cor in query["q"][0].split(",")]

        if "pll" in query:
            region["platlng"] = [float(cor) for cor in query["pll"][0].split(",")]

    if "latlng" not in region:
        raise ValueError("invalid map URL: {}".format(url))

    if not name:
        name = _name_fromlatlngzoom(region)

    region["name"] = name

    if caption:
        region["caption"] = caption
    elif "caption" not in region:
        region["caption"] = name

    return region


def parse_natural(location, apikey=None, region=None):
    """Convert a natural language location string -- e.g. "San Francisco, CA" into lat/lng/zoom

    Call's Google's Geocoding API.
    Return empty dictionary if they were unable to parse.
    """
    options = ""
    if apikey:
        options += "&key=" + apikey
    if region:
        options += "&region=" + region

    req = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={}{}". \
            format(location, options))
    req.raise_for_status()
    data = req.json()

    if data["status"] != "OK":
        return {}

    latlng = data["results"][0]["geometry"]["location"]

    region = {
        "caption": data["results"][0]["formatted_address"],
        "latlng": [latlng["lat"], latlng["lng"]],
        "zoom": _fit_bounding(data["results"][0]["geometry"]["viewport"]) - 1
    }
    region["name"] = _name_fromlatlngzoom(region)
    return region


def _name_fromlatlngzoom(region):
    """Return a candidate name for a type of map, given the region object has a lat/lng/zoom"""
    prefix = "map" if "platlng" not in region else "portal"
    name = "{}_@{}".format(prefix, region["latlng"]).translate({ord(i):None for i in " []"})
    if "zoom" in region:
        name = name + "_z{}".format(region["zoom"])
    return name


def _fit_bounding(bounds):
    """Create a bounding box for a given polygon.

    h/t to  http://stackoverflow.com/a/6055653/1091772
    """
    globe_width = 256
    max_zoom = 21
    west_lat = bounds["southwest"]["lat"]
    east_lat = bounds["northeast"]["lat"]
    west_lng = bounds["southwest"]["lng"]
    east_lng = bounds["northeast"]["lng"]

    angle_lat = east_lat - west_lat
    if angle_lat < 0:
        angle_lat += 360
    zoom_lat = round(math.log(1920 * 360 / angle_lat / globe_width) / math.log(2))

    angle_lng = east_lng - west_lng
    if angle_lng < 0:
        angle_lng += 360
    zoom_lng = round(math.log(1920*360 / angle_lng / globe_width) / math.log(2))
    return min(zoom_lat, zoom_lng, max_zoom)
