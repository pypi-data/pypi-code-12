import json
import traceback
from random import random
from sys import stdout
from time import sleep
from termcolor import colored

import requests
from cutils import Gmail


def parse_location(latlong, access_token):
    e_tmr = 0
    e_conn = 0
    e_is = 0

    url = get_url(latlong, access_token)
    jsontext = ''

    for counter in xrange(5):
        try:
            r = requests.get(url)
            jsontext = json.loads(r.text)

            e_tmr = 0
            e_conn = 0

            status = jsontext['meta'].get('code')

            if status == 200:
                e_is = 0
                venues = jsontext.get('response', {'venues': []}).get('venues', [])
                if venues:
                    venue = venues[0]
                    name = venue['name'].encode('utf-8')
                    city = venue['location'].get('city', '').encode('utf-8')
                    state = venue['location'].get('state', '').encode('utf-8')
                    zip = venue['location'].get('postalCode', '').encode('utf-8')
                    country = venue['location'].get('country', '').encode('utf-8')
                    distance = venue['location'].get('distance', '')
                    if venue['categories']:
                        category = venue['categories'][0].get('name', '').encode('utf-8')
                    else:
                        category = ''
                    checkinsCount = venue['stats'].get('checkinsCount', 0)
                    return [name, category, checkinsCount, zip, city, state, country, distance]
                else:
                    return []
            else:
                e_is += 1
                stdout.write(colored(' InvalidStatus,', 'red'))
                stdout.write(colored(str(counter), 'red'))
                stdout.write('\r')
                stdout.flush()
                if e_is >= 5:
                    g_error = Gmail().set_from_to().set_credentials().set_subject('AWS Foursquare APIError!')
                    g_error.send_message(latlong + '@' + str(access_token) + '\n\n' + jsontext['meta'].__str__()).close()
                    break
                else:
                    sleep(60)
                    continue

        except requests.ConnectionError:
            sleep(random() * 60)
            e_conn += 1
            if e_conn >= 5:
                g_error = Gmail().set_from_to().set_credentials().set_subject('AWS Foursquare ConnectionError!')
                g_error.send_message(latlong + '@' + str(access_token) + '\n\nConnectionError').close()
                return []
            else:
                continue

        except requests.TooManyRedirects:
            sleep(random() * 60)
            e_tmr += 1
            if e_tmr >= 5:
                g_error = Gmail().set_from_to().set_credentials().set_subject('AWS Foursquare TooManyRedirects!')
                g_error.send_message(latlong + '@' + str(access_token) + '\n\nTooManyRedirects').close()
                return []
            else:
                continue

        except:
            g_error = Gmail().set_from_to().set_credentials().set_subject('AWS Foursquare Error!')
            g_error.send_message(latlong + '@' + str(access_token))
            g_error.send_message(traceback.format_exc())
            g_error.send_message('\n\n\n')
            if jsontext:
                g_error.send_message(jsontext.__str__()).close()
            else:
                g_error.close()
            return []


def get_url(latlong, access_token):
    if ',' in access_token:
        token = access_token.split(',')
        clientid = token[0]
        clientsecret = token[1]
        return 'https://api.foursquare.com/v2/venues/search?ll=' + str(latlong) + '&query=&limit=1&client_id=' + clientid + '&client_secret=' + clientsecret +'&v=20151216'
    else:
        return 'https://api.foursquare.com/v2/venues/search?ll=' + str(latlong) + '&query=&limit=1&oauth_token=' + access_token + '&v=20151216'
