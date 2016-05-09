import requests
import json


def get_city(latlong, access_token):
    url = get_url(latlong, access_token)

    try:
        r = requests.get(url)
        jsontext = json.loads(r.text)

        venue = jsontext['response']['venues'][0]
        city = venue['location'].get('city', '').encode('utf-8')
        country = venue['location'].get('country', '').encode('utf-8')
        return [city, country]
    except:
        return []


def get_url(latlong, access_token):
    return 'https://api.foursquare.com/v2/venues/search?ll=' + str(latlong) + '&query=&limit=1&oauth_token=' + access_token + '&v=20151216'
