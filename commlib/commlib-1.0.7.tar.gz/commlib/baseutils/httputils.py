#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@date: 2016-04-13

@author: Devin
"""
import cookielib
import json
import random
import urllib
import urllib2


def random_headers():
    random_ip = "%s.%s.%s.%s" % (
        random.randint(10, 240), random.randint(10, 240),
        random.randint(10, 240),
        random.randint(10, 240))
    headers = dict()
    headers[
        "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0"
    headers["Connection"] = "keep-alive"
    headers["http_client_ip"] = random_ip
    headers["HTTP_X_FORWARDED_FOR"] = random_ip
    return headers


def get_request_json(url):
    try:
        res = urllib2.urlopen(url)
        res_json = json.loads(res.read())
        return res_json
    except Exception, e:
        raise e


def JsonHTTPRequest(url, method='GET', **data):
    cj = cookielib.CookieJar()

    data = urllib.urlencode(data)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    if method == 'GET':
        req = urllib2.Request(url + "?" + data)
        print req
        response = opener.open(req)
    elif method == 'POST':
        req = urllib2.Request(url)
        response = opener.open(req, data)

    return json.loads(response.read())


if __name__ == "__main__":
    print JsonHTTPRequest(
        "http://192.168.20.61:9030/hulkopen/rfid/queryByPlaceCode", "GET",
        placeCode=','.join(['A01', 'A02'])).get("data")
    print JsonHTTPRequest(
        "http://192.168.20.61:9030/hulkopen/rfid/queryByRfid", "GET",
        rfid=','.join(['A01', 'A02'])).get('data')
