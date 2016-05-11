import requests
import json
import traceback


def parse_location(latlong, access_token):
    url = get_url(latlong, access_token)

    try:
        r = requests.get(url)
        jsontext = json.loads(r.text)

        venue = jsontext['response']['venues'][0]
        name = venue['name'].encode('utf-8')
        city = venue['location'].get('city', '').encode('utf-8')
        state = venue['location'].get('state', '').encode('utf-8')
        zip = venue['location'].get('postalCode', '')
        country = venue['location'].get('country', '').encode('utf-8')
        distance = venue['location'].get('distance', '')
        category = venue['categories'][0].get('name', '').encode('utf-8')
        checkinsCount = venue['stats'].get('checkinsCount', 0)
        return [name, category, checkinsCount, zip, city, state, country, distance]
    except:
        print traceback.format_exc()
        print jsontext
        return []


def get_url(latlong, access_token):
    if ',' in access_token:
        token = access_token.split(',')
        clientid = token[0]
        clientsecret = token[1]
        return 'https://api.foursquare.com/v2/venues/search?ll=' + str(latlong) + '&query=&limit=1&client_id=' + clientid + '&client_secret=' + clientsecret +'&v=20151216'
    else:
        return 'https://api.foursquare.com/v2/venues/search?ll=' + str(latlong) + '&query=&limit=1&oauth_token=' + access_token + '&v=20151216'
