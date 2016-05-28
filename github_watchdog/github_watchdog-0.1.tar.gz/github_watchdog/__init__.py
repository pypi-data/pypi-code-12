from __future__ import print_function
import ConfigParser, json, datetime, logging, time, sys
import urllib2
from os import path
import requests


logging.basicConfig(filename='watchdog.log',level=logging.DEBUG)

# function to send alert on hipchat
def hipchat_notify(token, room, message, color='yellow', notify=False,
                   format='text', host='api.hipchat.com'):


    """Send notification to a HipChat room via API version 2

    Parameters
    ----------
    token : str
        HipChat API version 2 compatible token (room or user token)
    room: str
        Name or API ID of the room to notify
    message: str
        Message to send to room
    color: str, optional
        Background color for message, defaults to yellow
        Valid values: yellow, green, red, purple, gray, random
    notify: bool, optional
        Whether message should trigger a user notification, defaults to False
    format: str, optional
        Format of message, defaults to text
        Valid values: text, html
    host: str, optional
        Host to connect to, defaults to api.hipchat.com
    """

    if len(message) > 10000:
        raise ValueError('Message too long')
    if format not in ['text', 'html']:
        raise ValueError("Invalid message format '{0}'".format(format))
    if color not in ['yellow', 'green', 'red', 'purple', 'gray', 'random']:
        raise ValueError("Invalid color {0}".format(color))
    if not isinstance(notify, bool):
        raise TypeError("Notify must be boolean")

    url = "https://{0}/v2/room/{1}/notification".format(host, room)
    headers = {'Content-type': 'application/json'}
    headers['Authorization'] = "Bearer " + token
    payload = {
        'message': message,
        'notify': notify,
        'message_format': format,
        'color': color
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    r.raise_for_status()

    try:
        hipchat_notify('MY_HIPCHAT_TOKEN', 'room_name_or_id', 'Hello World!')
    except Exception as e:
        msg = "[ERROR] HipChat notify failed: '{0}'".format(e)
        logging.error(msg, file=sys.stderr)
        sys.exit(1)

# json put and get
def put(data, filename):
	try:
		jsondata = json.dumps(data, indent=4, skipkeys=True, sort_keys=True)
		fd = open(filename, 'w')
		fd.write(jsondata)
		fd.close()
	except Exception,e:
		logging.error('ERROR writing', filename + str(e))
		pass

def get(filename):
	returndata = {}
	try:
		fd = open(filename, 'r')
		text = fd.read()
		fd.close()
		returndata = json.loads(text)
		# Hm.  this returns unicode keys...
		#returndata = simplejson.loads(text)
	except Exception,e :
		logging.error('COULD NOT LOAD:', filename + str(e))
	return returndata

#read config values
config = ConfigParser.ConfigParser()
config.readfp(open(r'conf/watchdog'))
api_endpoint = config.get('metadata', 'api_endpoint')
repo_name = config.get('metadata', 'repo_name')
project_name = config.get('metadata', 'project_name')
polling_interval = config.get('metadata', 'polling_interval')
notification_channel = config.get('metadata', 'notification_channel')

logging.info("-------------The config parameters read as follows-----------" + "\n" + "api_endpoint:" + api_endpoint + "\n" + "repo_name:" + repo_name + "\n" + "project_name:" + project_name \
+ "\n" + "polling_interval:" + str(polling_interval) + "\n" + "notification_channel:" + notification_channel)


#build the contributors api endpoint
endpoint = path.join(api_endpoint, repo_name, project_name)
contrib_endpoint = path.join(endpoint, "contributors")
logging.info("The contributors endpoint is " + contrib_endpoint)

def getContributerCount(endpoint):
    # fetch the number of contributors
    res = urllib2.urlopen(contrib_endpoint)
    parsed_data = json.loads(res.read())
    logging.info("json output is " "\n" + str(parsed_data))
    logging.info("Number of contributors: " + str(len(parsed_data)))
    contrib_count = str(len(parsed_data))
    return contrib_count

try:
    while True:
        contrib_count = getContributerCount(contrib_endpoint)
        if path.isfile('state.json'):
            contrib_state_data = get('state.json')
            latest_contrib_count = contrib_state_data['contributer_count']
            if latest_contrib_count != contrib_count:
                # send notification
                # hipchat_notify("nicetryuseyourowntoken", "yourroom", "contributor count is " + latest_contrib_count, color='yellow', notify=False, format='text', host='api.hipchat.com')
                pass
        contrib_data = {
            'contributer_count': contrib_count,
            'modifiedTime': str(datetime.datetime.now())
        }
        put(contrib_data, 'state.json')

        time.sleep(float(polling_interval))

except Exception,e:
    logging.error(str(e))